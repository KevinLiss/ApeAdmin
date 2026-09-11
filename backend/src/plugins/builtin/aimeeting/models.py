"""AI 会议助手插件——数据库模型。

表名约定：``aimeeting_`` 开头（插件名 aimeeting）。

核心工作流：
开始会议进行录音 → 语音转写（faster-whisper）→ LLM 总结 1 句话 → 结构化会议纪要输出
（结论、讨论要点、决议、遗留问题）

数据模型设计：
- ``aimeeting_meetings``：会议主表。用户端通过「会议编号 + 设备标识」访问；
  管理端用于管理历史会议、查看转写文本与纪要。
- ``aimeeting_records``：录音文件与语音转写结果。一次会议可有多次录音/转写片段，
  最终合并为完整转写文本。
- ``aimeeting_minutes``：AI 生成的会议总结（一句话）与结构化会议纪要（结论/讨论要点/决议/遗留问题）。
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.models.mixins import IDMixin, TimestampMixin


class MeetingStatus:
    """会议状态常量。"""
    SCHEDULED = "scheduled"      # 待开始
    IN_PROGRESS = "in_progress"  # 进行中（已上传录音/转写中）
    ENDED = "ended"              # 已结束（纪要已生成）
    CANCELLED = "cancelled"      # 已取消


class TranscriptStatus:
    """转写状态常量。"""
    PENDING = "pending"     # 待转写
    PROCESSING = "processing"  # 转写中
    SUCCESS = "success"     # 转写完成
    FAILED = "failed"       # 转写失败


class AimeetingMeeting(IDMixin, TimestampMixin, Base):
    """AI 会议表。

    表名：``aimeeting_meetings``
    """

    __tablename__ = "aimeeting_meetings"

    # 会议基本信息（用户端创建时填写；留空则按时间自动命名）
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="会议标题")
    # 会议编号（用户输入作为凭证查询会议）
    meeting_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True, comment="会议编号")
    # 参会人（用户填写，逗号分隔）
    participants: Mapped[str] = mapped_column(Text, default="", comment="参会人名单（逗号分隔）")
    # 会议时间
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="会议开始时间（用户填写）"
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="会议结束时间"
    )

    # 会议状态
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=MeetingStatus.SCHEDULED, comment="会议状态"
    )
    actual_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="实际开始录音时间"
    )
    actual_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="实际结束时间"
    )

    # 录音转写
    audio_file: Mapped[str] = mapped_column(String(500), default="", comment="录音文件路径（合并后的完整录音）")
    audio_duration: Mapped[int] = mapped_column(Integer, default=0, comment="录音总时长（秒）")
    transcript_text: Mapped[str] = mapped_column(Text, default="", comment="完整语音转写文本")
    transcript_status: Mapped[str] = mapped_column(
        String(20), default=TranscriptStatus.PENDING, comment="转写状态"
    )
    # 结构化转写（句级 JSON：[{start,end,text,speaker}]），实时对话流渲染与说话人对齐的数据源
    transcript_json: Mapped[str] = mapped_column(Text, default="", comment="句级结构化转写（JSON 数组）")
    # 转写修订号：任何对 transcript_json 中「已有片段」的修改（精修替换文本 / 说话人回填）
    # 都会自增此值。前端增量轮询用数组索引做 after_id，无法感知原地修改；
    # 改为比对 revision，变化则走全量刷新，确保精修结果与说话人回填能到达前端。
    transcript_revision: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="转写修订号（已合并片段的修改计数）"
    )

    # 说话人分离状态：none=未分离 / pending=分离中 / success=完成 / failed=失败
    diarization_status: Mapped[str] = mapped_column(
        String(20), default="none", comment="说话人分离状态"
    )

    # 创建人（后台管理创建/用户端创建时记录）
    creator_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True, comment="创建人ID")
    creator_name: Mapped[str] = mapped_column(String(100), default="", comment="创建人名称")
    # 用户端无感登录设备标识
    device_id: Mapped[str] = mapped_column(String(200), default="", index=True, comment="设备标识（无感登录）")

    # 软删除
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, comment="软删除")


class AimeetingMinuteRecord(IDMixin, TimestampMixin, Base):
    """录音转写记录。

    表名：``aimeeting_records``
    一次会议可上传多段录音（15 秒准实时切片 + 手动分段），每段独立转写，
    携带会议内时间偏移，最终合并为句级结构化转写（transcript_json）。

    ⚠️ 前端切片边界可能切断句子：whisper 对每段独立转写，句首半个字/句尾重复
    属正常现象，由 merge 环节做轻量去重。
    """

    __tablename__ = "aimeeting_records"

    meeting_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="所属会议ID")
    # 本段录音在会议内的偏移（秒，实时切片 = 已录时长累计）
    offset_sec: Mapped[int] = mapped_column(Integer, default=0, comment="本段在会议内的时间偏移（秒）")
    # 录音文件
    audio_path: Mapped[str] = mapped_column(String(500), default="", comment="录音文件路径")
    audio_duration: Mapped[int] = mapped_column(Integer, default=0, comment="录音时长（秒）")
    # 转写
    transcript: Mapped[str] = mapped_column(Text, default="", comment="本段转写文本")
    # 句级结构化转写（JSON：[{start,end,text}]，start/end 为会议内绝对时间）
    segments_json: Mapped[str] = mapped_column(Text, default="", comment="句级转写片段（JSON）")
    transcript_status: Mapped[str] = mapped_column(
        String(20), default=TranscriptStatus.PENDING, comment="本段转写状态"
    )
    error: Mapped[str] = mapped_column(Text, default="", comment="转写失败原因")
    # 设备
    device_id: Mapped[str] = mapped_column(String(200), default="", index=True, comment="设备标识")
    creator_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="上传人ID")
    creator_name: Mapped[str] = mapped_column(String(100), default="", comment="上传人名称")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, comment="软删除")


class AimeetingSpeaker(IDMixin, TimestampMixin, Base):
    """会议说话人（声纹聚类出的虚拟身份，名称可编辑）。

    表名：``aimeeting_speakers``
    说话人分离完成后，按聚类编号生成「发言者A001」，用户可改为真实姓名。
    """

    __tablename__ = "aimeeting_speakers"

    meeting_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="所属会议ID")
    speaker_no: Mapped[int] = mapped_column(Integer, nullable=False, comment="说话人聚类编号（1 起）")
    display_name: Mapped[str] = mapped_column(String(100), default="", comment="显示名称（可编辑，默认「发言者A001」）")
    # 说话时间统计（秒），由分离结果聚合
    total_speak_sec: Mapped[int] = mapped_column(Integer, default=0, comment="累计说话时长（秒）")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, comment="软删除")


class AimeetingHighlight(IDMixin, TimestampMixin, Base):
    """会议重点标记（实时转写中「记重点」产生）。

    表名：``aimeeting_highlights``
    用户在录音转写过程中点击「记重点」，把当前时间点对应的转写片段标记为重点，
    用于会后快速回顾关键内容。
    """

    __tablename__ = "aimeeting_highlights"

    meeting_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="所属会议ID")
    # 标记时间点（会议内绝对偏移，秒）
    offset_sec: Mapped[int] = mapped_column(Integer, default=0, comment="标记时会议内时间偏移（秒）")
    # 关联转写片段（按时间就近匹配到的 transcript 片段索引，可为空）
    segment_idx: Mapped[int] = mapped_column(Integer, default=-1, comment="关联转写片段索引（transcript_json 数组下标）")
    # 标记内容快照（标记时的转写文本，事后可展示）
    text_snapshot: Mapped[str] = mapped_column(Text, default="", comment="标记时点转写文本快照")
    note: Mapped[str] = mapped_column(String(500), default="", comment="备注（可选）")
    device_id: Mapped[str] = mapped_column(String(200), default="", index=True, comment="设备标识")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, comment="软删除")


class AimeetingMark(IDMixin, TimestampMixin, Base):
    """会议自定义标记（实时转写中「标记」按钮）。

    表名：``aimeeting_marks``
    用户在转写过程中点击「标记」，在指定时间点插入自定义标识（如「待办」「疑问」）。
    """

    __tablename__ = "aimeeting_marks"

    meeting_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="所属会议ID")
    offset_sec: Mapped[int] = mapped_column(Integer, default=0, comment="标记时会议内时间偏移（秒）")
    # 标记内容
    content: Mapped[str] = mapped_column(String(500), default="", comment="标记内容")
    device_id: Mapped[str] = mapped_column(String(200), default="", index=True, comment="设备标识")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, comment="软删除")


class AimeetingMinutes(IDMixin, TimestampMixin, Base):
    """AI 生成的会议总结与会议记录。

    表名：``aimeeting_minutes``
    会议转写完成后由 AI 自动生成：一句话总结 + 结构化会议纪要。
    """

    __tablename__ = "aimeeting_minutes"

    meeting_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="所属会议ID")
    # 会议总结（LLM 总结 1 句话）
    summary: Mapped[str] = mapped_column(Text, default="", comment="会议总结（一句话）")
    # 结构化会议纪要：结论 / 讨论要点 / 决议 / 遗留问题
    minutes: Mapped[str] = mapped_column(Text, default="", comment="结构化会议纪要（Markdown）")
    # 生成原始素材（完整转写文本）
    source_material: Mapped[str] = mapped_column(Text, default="", comment="生成素材（完整转写文本）")
    # 生成状态：pending / success / failed
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="生成状态")
    provider_name: Mapped[str] = mapped_column(String(100), default="", comment="使用的AI供应商")
    error: Mapped[str] = mapped_column(Text, default="", comment="生成失败原因")
    generated_by: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="触发生成用户ID")