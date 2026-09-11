"""AI 会议助手插件——Pydantic 请求/响应模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── 会议 ────────────────────────────────────────────────────────────────

class MeetingCreate(BaseModel):
    """创建会议（用户端填写，极简：名称可选留空自动命名）。"""
    title: str = Field(default="", max_length=200, description="会议标题（留空则按创建时间自动命名）")
    start_time: Optional[datetime] = Field(default=None, description="会议开始时间")
    participants: str = Field(default="", description="参会人（逗号分隔）")


class MeetingUpdate(BaseModel):
    """更新会议（部分字段可选）。"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    participants: Optional[str] = None
    start_time: Optional[datetime] = None


class MeetingRename(BaseModel):
    """用户端修改会议名称（全程可改）。"""
    title: str = Field(..., min_length=1, max_length=200, description="新会议名称")
    device_id: str = Field(..., min_length=8, max_length=200, description="设备标识")


class MeetingBatchDelete(BaseModel):
    """管理端批量删除会议。"""
    ids: list[int] = Field(..., min_length=1, max_length=500, description="会议ID列表")


class SpeakerUpdate(BaseModel):
    """修改说话人显示名称。"""
    display_name: str = Field(..., min_length=1, max_length=100, description="新显示名称")


class MeetingStatusUpdate(BaseModel):
    """更新会议状态。"""
    status: str = Field(..., description="会议状态: scheduled/in_progress/ended/cancelled")


class MeetingOut(BaseModel):
    """会议响应（管理端/用户端通用）。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    meeting_code: str
    participants: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    status: str
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    audio_file: str
    audio_duration: int
    transcript_text: str
    transcript_status: str
    # 转写修订号：已合并片段被修改（精修/说话人回填）时自增，前端据此判断是否需全量刷新
    transcript_revision: int = 0
    diarization_status: str
    device_id: str
    creator_id: int
    creator_name: str
    created_at: datetime
    updated_at: datetime


# ── 用户端无感登录 ───────────────────────────────────────────────────────

class DeviceBind(BaseModel):
    """用户端设备标识（无感登录）。"""
    device_id: str = Field(..., min_length=8, max_length=200, description="设备标识（指纹）")


class MeetingLookup(BaseModel):
    """用户端通过会议编号查询会议。"""
    meeting_code: str = Field(..., min_length=1, max_length=32, description="会议编号")
    device_id: str = Field(..., min_length=8, max_length=200, description="设备标识")


# ── 录音转写 ─────────────────────────────────────────────────────────────

class AudioUpload(BaseModel):
    """录音文件上传（multipart 中附带元数据）。"""
    device_id: str = Field(..., min_length=8, max_length=200, description="设备标识")
    duration: int = Field(default=0, ge=0, description="录音时长（秒）")
    offset_sec: int = Field(default=0, ge=0, description="本段在会议内的时间偏移（秒，实时切片累计）")


class RecordOut(BaseModel):
    """转写记录响应。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    offset_sec: int
    audio_path: str
    audio_duration: int
    transcript: str
    segments_json: str
    transcript_status: str
    error: str
    created_at: datetime


class SpeakerOut(BaseModel):
    """说话人响应。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    speaker_no: int
    display_name: str
    total_speak_sec: int
    created_at: datetime


# ── 重点标记 / 自定义标记 ────────────────────────────────────────────────

class HighlightCreate(BaseModel):
    """创建重点标记。"""
    device_id: str = Field(..., min_length=8, max_length=200, description="设备标识")
    offset_sec: int = Field(..., ge=0, description="标记时会议内时间偏移（秒）")
    text_snapshot: str = Field(default="", max_length=2000, description="标记时点转写文本快照")
    note: str = Field(default="", max_length=500, description="备注（可选）")


class HighlightOut(BaseModel):
    """重点标记响应。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    offset_sec: int
    segment_idx: int
    text_snapshot: str
    note: str
    created_at: datetime


class MarkCreate(BaseModel):
    """创建自定义标记。"""
    device_id: str = Field(..., min_length=8, max_length=200, description="设备标识")
    offset_sec: int = Field(..., ge=0, description="标记时会议内时间偏移（秒）")
    content: str = Field(..., min_length=1, max_length=500, description="标记内容")


class MarkOut(BaseModel):
    """自定义标记响应。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    offset_sec: int
    content: str
    created_at: datetime


# ── 会议纪要/总结 ───────────────────────────────────────────────────────

class MinutesOut(BaseModel):
    """AI 生成的会议纪要/总结响应。"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    summary: str
    minutes: str
    status: str
    provider_name: str
    error: str
    created_at: datetime
    updated_at: datetime