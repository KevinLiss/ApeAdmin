"""AI 会议助手插件——业务服务层。

核心工作流：
开始会议进行录音（15 秒准实时切片上传）→ 语音转写（faster-whisper，句级时间戳）
→ LLM 总结 1 句话 → 结构化会议纪要输出（结论、讨论要点、决议、遗留问题）
→ 会后说话人分离（sherpa-onnx 声纹聚类 + 时间戳对齐，虚拟名称可编辑）
"""
import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.agent import chat_non_stream
from src.crud.ai import crud_ai_provider
from src.plugins.builtin.aimeeting.models import (
    AimeetingMeeting,
    AimeetingMinuteRecord,
    AimeetingMinutes,
    AimeetingSpeaker,
    TranscriptStatus,
)

# ── 路径配置 ─────────────────────────────────────────────────────────────
# 录音文件存储目录（相对 backend 根目录，可被配置覆盖）
BACKEND_DIR = Path(__file__).resolve().parents[4]  # backend/
AUDIO_STORE_DIR = Path(os.environ.get("AIMEETING_AUDIO_DIR", BACKEND_DIR / "storage" / "aimeeting" / "audio"))
MODEL_DIR = Path(os.environ.get("AIMEETING_WHISPER_MODEL", BACKEND_DIR / "models" / "faster-whisper-small"))
# 说话人分离模型（sherpa-onnx 官方 pyannote 分段 + Wespeaker 声纹，ONNX）
DIARIZATION_DIR = Path(
    os.environ.get("AIMEETING_DIARIZATION_MODEL", BACKEND_DIR / "models" / "sherpa-diarization")
)

# ── 转写模型（懒加载单例）──────────────────────────────────────────────
_whisper_model = None

# ── 并发控制 ──────────────────────────────────────────────────────────
# CPU int8 小模型并发上限：避免每个切片一个 asyncio.create_task 造成 CPU 排队风暴
_transcribe_sem = asyncio.Semaphore(2)
# 每会议一把锁：串行化增量说话人分离（避免 m{id}_merged.wav 同名互踩 + transcript_json 读写竞态）
# 锁字典的 setdefault 在事件循环内同步执行、无 await 让出点，无需额外 guard。
_diarization_locks: dict[int, asyncio.Lock] = {}


def _get_diarization_lock(meeting_id: int) -> asyncio.Lock:
    """获取会议级说话人分离锁（全局字典，按会议数增长，进程生命周期内可控）。"""
    return _diarization_locks.setdefault(meeting_id, asyncio.Lock())


# 增量分离节流：每 N 秒最多跑一次（会议进行中避免每片都全量重跑）
_incremental_last_ts: dict[int, float] = {}
_INC_DIARIZATION_INTERVAL = 60.0  # 秒


def _should_run_incremental(meeting_id: int, interval: float = _INC_DIARIZATION_INTERVAL) -> bool:
    """增量分离节流：距上次 >= interval 才允许再跑。"""
    import time

    now = time.monotonic()
    if now - _incremental_last_ts.get(meeting_id, -1e9) >= interval:
        _incremental_last_ts[meeting_id] = now
        return True
    return False


def _get_whisper_model():
    """懒加载 faster-whisper small 模型（CPU int8）。"""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel

        _whisper_model = WhisperModel(str(MODEL_DIR), device="cpu", compute_type="int8")
        logger.info("[Aimeeting] faster-whisper small 模型加载完成")
    return _whisper_model


# ── 会议纪要生成提示词（新工作流：一句话总结 + 结构化纪要）──────────
MINUTES_SYSTEM_PROMPT = """你是专业的会议记录助手，负责把会议语音转写文本整理成高质量的结构化会议纪要。

请严格按照以下 JSON 结构输出（不要输出任何额外文字、解释或 Markdown 代码块标记，只输出纯 JSON）：

{
  "summary": "用一句话（不超过 60 字）总结本次会议的核心结论",
  "minutes": "结构化会议纪要，使用 Markdown 格式，必须包含以下四个板块：\n## 结论\n## 讨论要点\n## 决议\n## 遗留问题"
}

注意事项：
- 总结需一句话说清会议最重要结论，简洁有力。
- 会议纪要必须忠实反映转写文本内容，不编造会议中未出现的信息。
- 「结论」概括会议最终达成的一致意见；「讨论要点」分条列出过程中的关键讨论；「决议」列出明确决定的事项；「遗留问题」列出未解决/待跟进事项。
- 若转写文本为空或过短，如实说明信息不足。
"""


# ── 会议自动命名 ─────────────────────────────────────────────────────────

def auto_title(now: datetime | None = None) -> str:
    """按时间自动生成会议名（本地时区）。"""
    t = now or datetime.now()
    return f"会议-{t.strftime('%Y.%m.%d %H:%M')}"


# ── 转写服务 ───────────────────────────────────────────────────────────

def _create_record_sync_data(
    meeting_id: int, offset_sec: int, audio_path: str, duration: int, device_id: str,
) -> AimeetingMinuteRecord:
    """构造转写记录 ORM 对象（未入库）。"""
    return AimeetingMinuteRecord(
        meeting_id=meeting_id,
        offset_sec=offset_sec,
        audio_path=audio_path,
        audio_duration=duration,
        transcript="",
        transcript_status=TranscriptStatus.PROCESSING,
        device_id=device_id,
        creator_id=0,
        creator_name="用户端",
    )


async def transcribe_audio_file(
    db: AsyncSession, meeting: AimeetingMeeting, audio_path: str, device_id: str = "",
    duration: int = 0, offset_sec: int = 0,
) -> str:
    """转写一段录音文件，返回转写文本（同步等待完成，供旧链路/测试使用）。

    使用 faster-whisper small 模型（CPU int8），离线本地推理。
    记录句级时间戳（会议内绝对时间 = 段偏移 + 段内时间）。
    转写结果写入 aimeeting_records 记录。
    """
    record_obj = _create_record_sync_data(meeting.id, offset_sec, audio_path, duration, device_id)
    db.add(record_obj)
    await db.commit()
    await db.refresh(record_obj)

    try:
        # CPU 密集任务放线程池，避免阻塞事件循环（分段上传时尤为关键）
        segments_data = await asyncio.to_thread(_transcribe_sync, audio_path, offset_sec)
        transcript = "\n".join(s["text"] for s in segments_data if s["text"].strip())
        record_obj.transcript = transcript
        record_obj.segments_json = json.dumps(segments_data, ensure_ascii=False)
        record_obj.transcript_status = TranscriptStatus.SUCCESS
        record_obj.error = ""
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"[Aimeeting] 转写失败: {exc}")
        record_obj.transcript_status = TranscriptStatus.FAILED
        record_obj.error = f"转写失败：{exc}"

    await db.commit()
    await db.refresh(record_obj)

    # 转写完成后同步合并到会议 transcript_json（前端实时对话流立即可见）
    await merge_transcript_to_meeting(db, meeting)
    return record_obj.transcript


async def transcribe_record_async(record_id: int) -> None:
    """后台转写一条已登记的记录（独立数据库会话，不阻塞接口）。

    完成后把最新句级片段合并进会议 transcript_json，
    供前端实时对话流轮询展示。
    """
    from src.db import get_db_context

    async with get_db_context() as db:
        record_obj = await db.get(AimeetingMinuteRecord, record_id)
        if not record_obj or record_obj.transcript_status != TranscriptStatus.PROCESSING:
            return
        meeting = await db.get(AimeetingMeeting, record_obj.meeting_id)
        if not meeting or meeting.is_deleted:
            record_obj.transcript_status = TranscriptStatus.FAILED
            record_obj.error = "会议不存在或已删除"
            await db.commit()
            return

        try:
            async with _transcribe_sem:  # 限流：CPU 并发上限 2，防排队风暴
                segments_data = await asyncio.to_thread(
                    _transcribe_sync, record_obj.audio_path, record_obj.offset_sec
                )
            record_obj.transcript = "\n".join(s["text"] for s in segments_data if s["text"].strip())
            record_obj.segments_json = json.dumps(segments_data, ensure_ascii=False)
            record_obj.transcript_status = TranscriptStatus.SUCCESS
            record_obj.error = ""
        except Exception as exc:  # noqa: BLE001
            # 首次失败自动重试一次（模型加载/文件句柄等多为瞬态错误），仍失败才落 failed
            logger.warning(f"[Aimeeting] 转写失败 record={record_id}，重试一次: {exc}")
            try:
                await asyncio.sleep(2.0)
                async with _transcribe_sem:
                    segments_data = await asyncio.to_thread(
                        _transcribe_sync, record_obj.audio_path, record_obj.offset_sec
                    )
                record_obj.transcript = "\n".join(s["text"] for s in segments_data if s["text"].strip())
                record_obj.segments_json = json.dumps(segments_data, ensure_ascii=False)
                record_obj.transcript_status = TranscriptStatus.SUCCESS
                record_obj.error = ""
            except Exception as exc2:  # noqa: BLE001
                logger.exception(f"[Aimeeting] 后台转写重试仍失败 record={record_id}: {exc2}")
                record_obj.transcript_status = TranscriptStatus.FAILED
                record_obj.error = f"转写失败：{exc2}"
        await db.commit()

        # 合并到会议句级转写（实时对话流数据源）
        try:
            await merge_transcript_to_meeting(db, meeting)
        except Exception as exc:  # noqa: BLE001
            logger.exception(f"[Aimeeting] 合并转写失败 meeting={meeting.id}: {exc}")

        # 会议进行中：节流增量跑说话人分离（避免每片全量重跑，CPU 风暴）
        if (
            meeting.status == "in_progress"
            and DIARIZATION_DIR.exists()
            and meeting.transcript_text.strip()
            and _should_run_incremental(meeting.id)
        ):
            try:
                await run_diarization(db, meeting, incremental=True, tail_sec=300)
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"[Aimeeting] 增量说话人分离失败 meeting={meeting.id}: {exc}")


async def wait_for_records_done(db: AsyncSession, meeting: AimeetingMeeting, timeout: float = 60.0) -> bool:
    """等待会议全部转写记录完成（结束会议前调用，防止漏掉最后几段）。

    返回 True 表示全部完成（或无记录）；False 表示超时仍有 processing。
    """
    import time

    deadline = time.monotonic() + timeout
    while True:
        processing = (
            await db.execute(
                select(AimeetingMinuteRecord.id).where(
                    AimeetingMinuteRecord.meeting_id == meeting.id,
                    AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
                    AimeetingMinuteRecord.transcript_status == TranscriptStatus.PROCESSING,
                )
            )
        ).scalars().first()
        if not processing:
            return True
        if time.monotonic() >= deadline:
            return False
        await asyncio.sleep(1.0)


def _transcribe_sync(audio_path: str, offset_sec: int) -> list[dict]:
    """同步转写（线程池内执行），返回句级片段 [{start, end, text}]（会议内绝对时间）。"""
    model = _get_whisper_model()
    segments, info = model.transcribe(
        audio_path,
        language="zh",
        beam_size=1,
        vad_filter=True,
    )
    result = []
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        result.append({
            "start": round(offset_sec + seg.start, 2),
            "end": round(offset_sec + seg.end, 2),
            "text": text,
        })
    return result


def _extract_merged_record_ids(segments: list) -> set[int]:
    """从 transcript_json 中提取已合并记录 id（隐藏元字段），无则空集。"""
    for item in segments:
        if isinstance(item, dict) and "__merged_record_ids" in item:
            return set(item["__merged_record_ids"])
    return set()


async def merge_transcript_to_meeting(db: AsyncSession, meeting: AimeetingMeeting) -> str:
    """合并会议全部有效转写片段到会议完整转写文本与句级 JSON。

    transcript_json 结构：[{start, end, text, speaker}]（speaker 由说话人分离回填，
    分离前为 0=未知）。

    增量策略：transcript_json 末尾维护隐藏元字段 ``__merged_record_ids``（已合并
    记录 id）。每次只合并新增成功记录的片段，历史片段不动，避免每片转写完成都
    全量重建 JSON（P2 卡顿根因之一）。

    兼容旧数据：若已有片段但无元字段（旧版全量合并结果），按「时间范围已存在
    则视为已合并」的规则初始化元字段，避免首次增量把旧片段重复追加。
    """
    # ── 读取现有 transcript_json，分离隐藏元字段与真实片段 ──
    # D7 竞态修复：expire_on_commit=False 下 meeting 可能是早前快照（后台精修/
    # 分离在别的时间点提交过），读旧值整体写回会覆盖他人已提交的修改 → 读前同步。
    await db.refresh(
        meeting,
        attribute_names=["transcript_json", "transcript_text", "transcript_revision"],
    )
    try:
        old_json = json.loads(meeting.transcript_json or "[]")
    except json.JSONDecodeError:
        old_json = []
    segments = [s for s in old_json if not (isinstance(s, dict) and "__merged_record_ids" in s)]
    merged_record_ids = _extract_merged_record_ids(old_json)

    # ── 取全部成功记录 ──
    result = await db.execute(
        select(AimeetingMinuteRecord)
        .where(
            AimeetingMinuteRecord.meeting_id == meeting.id,
            AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
            AimeetingMinuteRecord.transcript_status == TranscriptStatus.SUCCESS,
        )
        .order_by(AimeetingMinuteRecord.id.asc())
    )
    records = result.scalars().all()

    # 兼容旧数据：无元字段且已有片段时，把时间轴上已存在的片段视为已合并
    # （旧版 merge 是「全部记录全量重建」，片段全部已在；此处只需不回填 id，
    #   依赖「新记录才 append」即可——新记录必然是新 id，不会被误判）
    # 但需防止：旧版合并过 record A，新调用时 A 的 id 不在 merged_record_ids，
    # 会把 A 的片段再 append 一次。所以必须识别「已存在片段对应记录」。
    if not merged_record_ids and segments:
        # 用现有片段时间范围建索引：start-> 已存在（记录 offset 也对应 start）
        existing_offsets = {round(float(s.get("start", 0)), 2) for s in segments if isinstance(s, dict) and "start" in s}
        for r in records:
            r_start = round(float(r.offset_sec or 0), 2)
            if r_start in existing_offsets:
                merged_record_ids.add(r.id)

    # ── 只处理新增记录 ──
    # 新增前的既有序列（用于检测「插入到中间」造成的索引位移）。
    # 前端增量轮询以数组索引为 after_id，索引一旦位移，已渲染片段会错位/漏读。
    prev_keys = [
        (round(float(s.get("start") or 0), 2), round(float(s.get("end") or 0), 2))
        for s in segments
    ]
    new_records = [r for r in records if r.id not in merged_record_ids]
    if new_records:
        for r in new_records:
            if not r.segments_json:
                if r.transcript.strip():
                    segments.append({
                        "start": float(r.offset_sec or 0),
                        "end": float((r.offset_sec or 0) + (r.audio_duration or 0)),
                        "text": r.transcript.strip(),
                        "speaker": 0,
                    })
                merged_record_ids.add(r.id)
                continue
            try:
                for seg in json.loads(r.segments_json):
                    seg.setdefault("speaker", 0)
                    segments.append(seg)
                merged_record_ids.add(r.id)
            except json.JSONDecodeError:
                logger.warning(f"[Aimeeting] record {r.id} segments_json 解析失败，跳过")

    # 隐藏元字段从真实片段中剔除（若在 sort 前已在数组里）
    segments = [s for s in segments if not (isinstance(s, dict) and "__merged_record_ids" in s)]

    # 排序（真实片段按 start），隐藏字段固定放末尾
    segments.sort(key=lambda s: s["start"])

    # 索引位移检测：既有片段（排序后的前 N 项）位置若与新增前不一致，
    # 说明有新片段插到了中间（乱序到达），前端 after_id 增量会错位 → 自增修订号触发全量刷新。
    # 纯追加末尾不动索引 → 交给 after_id 增量轮询，避免每段都全量刷新。
    if prev_keys:
        now_keys = [
            (round(float(s.get("start") or 0), 2), round(float(s.get("end") or 0), 2))
            for s in segments[: len(prev_keys)]
        ]
        if now_keys != prev_keys:
            meeting.transcript_revision = (meeting.transcript_revision or 0) + 1

    segments.append({"__merged_record_ids": sorted(merged_record_ids)})

    meeting.transcript_json = json.dumps(segments, ensure_ascii=False)
    # 纯文本只取真实片段（跳过隐藏元字段）
    meeting.transcript_text = "\n".join(
        f"{speaker_code(s['speaker'])}: {s['text']}" if s.get("speaker") else s["text"]
        for s in segments
        if isinstance(s, dict) and "__merged_record_ids" not in s and s["text"].strip()
    )
    meeting.transcript_status = (
        TranscriptStatus.SUCCESS if meeting.transcript_text.strip() else meeting.transcript_status
    )
    await db.commit()
    await db.refresh(meeting)
    return meeting.transcript_text


async def update_merged_segment(
    db: AsyncSession, meeting: AimeetingMeeting, start: float, end: float, text: str,
) -> None:
    """更新会议 transcript_json 中已合并片段的文本（二遍精修替换初稿）。

    定位规则：匹配 start/end 落在容差内的片段（浮点时间戳），替换 text。
    若找不到（精修在 merge 前到达），直接追加为新片段，避免丢失。
    """
    # D7 竞态修复：精修是后台任务，执行时 meeting 内存态可能早于其他提交，
    # 写前同步转写列，避免过期快照覆盖新片段/speaker 回填。
    await db.refresh(
        meeting,
        attribute_names=["transcript_json", "transcript_text", "transcript_revision"],
    )
    try:
        old_json = json.loads(meeting.transcript_json or "[]")
    except json.JSONDecodeError:
        old_json = []
    segments = [s for s in old_json if not (isinstance(s, dict) and "__merged_record_ids" in s)]
    meta = [s for s in old_json if isinstance(s, dict) and "__merged_record_ids" in s]

    replaced = False
    changed = False
    for seg in segments:
        if abs(float(seg.get("start", -1)) - start) < 0.5 and abs(float(seg.get("end", -1)) - end) < 0.5:
            if seg.get("text") != text:
                seg["text"] = text
                changed = True
            replaced = True
            break
    if not replaced:
        # 精修先于 merge 到达：追加为新片段（会插到中间，索引位移）
        segments.append({"start": round(start, 2), "end": round(end, 2), "text": text, "speaker": 0})
        changed = True

    segments.sort(key=lambda s: s["start"])
    meeting.transcript_json = json.dumps(segments + meta, ensure_ascii=False)
    meeting.transcript_text = "\n".join(
        f"{speaker_code(s['speaker'])}: {s['text']}" if s.get("speaker") else s["text"]
        for s in segments
        if s["text"].strip()
    )
    # 已有片段文本被修改 → 自增修订号（增量轮询的 after_id 索引无法感知原地修改，
    # 前端比对 revision 变化后走全量刷新才能拿到精修文本）
    if changed:
        meeting.transcript_revision = (meeting.transcript_revision or 0) + 1
    await db.commit()
    await db.refresh(meeting)


# ── 说话人分离 ─────────────────────────────────────────────────────────

def speaker_code(no: int) -> str:
    """聚类编号 → 发言者编号（1→A001，27→A002…AA001 起扩展）。"""
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    no0 = no - 1
    letter = letters[no0 % 26]
    seq = no0 // 26 + 1
    return f"{letter}{seq:03d}"


async def run_diarization(
    db: AsyncSession, meeting: AimeetingMeeting, incremental: bool = False, tail_sec: int | None = None,
) -> bool:
    """说话人分离入口（会议级锁串行化，防 m{id}_merged.wav 互踩 + transcript_json 读写竞态）。

    - 增量分离（incremental=True）：幂等的重复劳动，已有一轮在跑则直接跳过
      （不排队，避免 N 轮全量分离依次堆积烧 CPU；下一片会再触发）。
    - 会后全量（incremental=False）：权威结果，必须等锁执行（finalize 调用）。

    asyncio 单线程事件循环下，``lock.locked()`` 检查到 ``async with lock``
    之间无 await 让出点，不存在 TOCTOU 竞态。
    """
    lock = _get_diarization_lock(meeting.id)
    if incremental and lock.locked():
        logger.info(f"[Aimeeting] 会议 {meeting.id} 增量分离已在进行中，跳过本轮")
        return False
    async with lock:
        return await _run_diarization_inner(db, meeting, incremental, tail_sec)


async def _run_diarization_inner(
    db: AsyncSession, meeting: AimeetingMeeting, incremental: bool = False, tail_sec: int | None = None,
) -> bool:
    """对会议音频跑说话人分离，输出说话人区间并对齐到句级转写。

    模型：sherpa-onnx（pyannote 分段 + Wespeaker 声纹，ONNX 离线）。
    流程：
    1. 拼接会议全部录音片段为完整音频（按 offset 排序，不足处补静音）。
    2. sherpa-onnx 跑 diarization，输出 [{start, end, speaker}]。
    3. 与 transcript_json 句级片段按时间重叠对齐，回填 speaker 编号。
    4. 生成/更新 aimeeting_speakers 表（发言者A001 + 说话时长）。

    incremental=True：会议进行中的增量分离，保留用户已改过的说话人名称，
    中间失败不打成 failed（下次分片继续尝试）。
    tail_sec：增量模式下只对最近 N 秒音频做分离（避免每片全量重跑），
    分离结果只回填落在该时间窗口内的句级片段。

    返回是否成功。
    """
    if not DIARIZATION_DIR.exists():
        if not incremental:
            meeting.diarization_status = "failed"
        logger.warning(f"[Aimeeting] 说话人分离模型未下载：{DIARIZATION_DIR}，跳过")
        await db.commit()
        return False

    meeting.diarization_status = "pending"
    await db.commit()
    await db.refresh(meeting)

    try:
        # 1. 取全部录音片段（增量模式只取最近 tail_sec 窗口内的片段，避免全量重拼）
        result = await db.execute(
            select(AimeetingMinuteRecord)
            .where(
                AimeetingMinuteRecord.meeting_id == meeting.id,
                AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
            )
            .order_by(AimeetingMinuteRecord.offset_sec.asc())
        )
        records = result.scalars().all()
        if not records:
            meeting.diarization_status = "none"
            await db.commit()
            return False

        # 增量模式：只保留窗口内（会议末尾 tail_sec 秒）的片段，其余丢弃
        # （分离只回填窗口内的句级 speaker，历史已分离片段不受影响）
        if incremental and tail_sec is not None:
            window_end = max((r.offset_sec or 0) + (r.audio_duration or 0) for r in records)
            window_start = max(window_end - tail_sec, 0)
            records = [
                r for r in records
                if (r.offset_sec or 0) + (r.audio_duration or 0) >= window_start
            ]
            if not records:
                logger.info(f"[Aimeeting] 会议 {meeting.id} 增量分离无窗口内片段，跳过")
                meeting.diarization_status = meeting.diarization_status or "pending"
                await db.commit()
                return False

        # 2. 拼接音频（线程池内执行，可能较慢）
        merged_audio = await asyncio.to_thread(_merge_audio_files, meeting, records)

        # 3. 说话人分离（线程池）
        diar_segments = await asyncio.to_thread(_diarize_sync, str(merged_audio))
        if not diar_segments:
            if not incremental:
                meeting.diarization_status = "failed"
            await db.commit()
            return False

        # ── 回填前重读最新转写（D7 竞态修复）──
        # 模型在 to_thread 里跑数秒到数分钟，期间 merge/refine 可能已提交新片段
        # 或精修文本；session 配了 expire_on_commit=False，meeting 内存里的
        # transcript_json 还是启动时刻的旧快照，直接写回会把他人改动整体覆盖
        # （会议46 E2E 实测：精修文本被覆盖回初稿、speaker 回填丢失）。
        # 会议级锁只串行化分离之间，不防「分离 vs merge/refine」，故写前必须刷新。
        # 注意：只刷转写三列——audio_file/audio_duration 是步骤 2 _merge_audio_files
        # 刚在内存设置、尚未 commit 的值，全量 refresh 会把它们冲回旧值（会议47 实测踩过）。
        await db.refresh(
            meeting,
            attribute_names=["transcript_json", "transcript_text", "transcript_revision"],
        )

        # 4. 对齐到句级转写（增量模式只回填窗口内片段，历史已分离 speaker 不动）
        speaker_changed = False
        if meeting.transcript_json:
            segments = json.loads(meeting.transcript_json)
            for seg in segments:
                # 跳过隐藏元字段（__merged_record_ids）
                if isinstance(seg, dict) and "__merged_record_ids" in seg:
                    continue
                if incremental and tail_sec is not None:
                    if seg.get("end", 0) < window_start:
                        continue
                new_no = _match_speaker(seg, diar_segments)
                if seg.get("speaker") != new_no:
                    seg["speaker"] = new_no
                    speaker_changed = True
            meeting.transcript_json = json.dumps(segments, ensure_ascii=False)
            # 同步纯文本格式：发言者A001: 文本（跳过隐藏字段）
            meeting.transcript_text = "\n".join(
                f"{speaker_code(s['speaker'])}: {s['text']}" if s.get("speaker") else s["text"]
                for s in segments
                if isinstance(s, dict) and "__merged_record_ids" not in s and s["text"].strip()
            )
            # speaker 回填改的是「已有片段」，after_id 索引无法感知 → 自增修订号触发前端全量刷新
            if speaker_changed:
                meeting.transcript_revision = (meeting.transcript_revision or 0) + 1

        # 5. 写入/更新 speakers 表（增量模式保留用户已改名的显示名）
        speak_sec: dict[int, int] = {}
        for d in diar_segments:
            speak_sec[d["speaker"]] = speak_sec.get(d["speaker"], 0) + int(d["end"] - d["start"])
        existing = (
            await db.execute(select(AimeetingSpeaker).where(AimeetingSpeaker.meeting_id == meeting.id))
        ).scalars().all()
        existing_map = {s.speaker_no: s for s in existing}
        for no, sec in speak_sec.items():
            if no in existing_map:
                existing_map[no].total_speak_sec = sec
            else:
                db.add(AimeetingSpeaker(
                    meeting_id=meeting.id,
                    speaker_no=no,
                    display_name=f"发言者{speaker_code(no)}",
                    total_speak_sec=sec,
                ))

        meeting.diarization_status = "success"
        await db.commit()
        await db.refresh(meeting)
        logger.info(f"[Aimeeting] 会议 {meeting.id} 说话人分离完成：{len(speak_sec)} 人")
        return True

    except Exception as exc:  # noqa: BLE001
        logger.exception(f"[Aimeeting] 说话人分离失败: {exc}")
        if not incremental:
            meeting.diarization_status = "failed"
            await db.commit()
        return False


def _merge_audio_files(meeting: AimeetingMeeting, records) -> Path:
    """拼接会议录音片段为单个 16k 单声道 wav（按 offset 时间轴放置，间隙补静音）。

    关键：句级转写的时间戳是会议绝对时间（offset + 片段内时间），说话人分离
    必须与之一致，因此合并产物必须保持绝对时间轴——片段按 offset 落到对应
    位置，空隙填静音，而不是简单顺序拼接（否则时间轴漂移导致无法对齐）。

    增量模式：若 m{id}_merged.wav 已存在，只把「超出已有文件时长」的新片段
    追加到时间轴（旧片段不动），避免每片都全量 ffmpeg 重拼整场会议。
    """
    output_path = AUDIO_STORE_DIR / f"m{meeting.id}_merged.wav"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 计算总时长（最后一片的偏移+时长）
    total_sec = max((r.offset_sec or 0) + (r.audio_duration or 0) for r in records)
    inputs = []
    for r in records:
        if r.audio_path and Path(r.audio_path).exists():
            inputs.append((r.audio_path, r.offset_sec or 0))

    import numpy as np
    import wave

    def _read_16k_mono(p: Path) -> np.ndarray:
        """读取音频为 16k 单声道 float32 数组。"""
        import ffmpeg
        import io
        out, _ = (
            ffmpeg
            .input(str(p))
            .output("pipe:1", format="wav", ac=1, ar=16000)
            .run(capture_stdout=True, quiet=True)
        )
        with wave.open(io.BytesIO(out), "rb") as wf:
            frames = wf.readframes(wf.getnframes())
            arr = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        return arr

    def _read_existing_wav(p: Path) -> np.ndarray | None:
        """读取已有合并文件为 float32 数组，读取失败返回 None。"""
        try:
            with wave.open(str(p), "rb") as wf:
                if wf.getframerate() != 16000 or wf.getnchannels() != 1:
                    return None
                frames = wf.readframes(wf.getnframes())
            return np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        except Exception:  # noqa: BLE001
            return None

    # ── 增量：已存在合并文件时，以旧文件为基底叠放全部片段 ──
    # 仅需 ffmpeg 解码新/全部片段 + 内存叠加写回，避免每片全量 ffmpeg 重拼。
    # 重传片段（offset 落在已覆盖区）天然幂等：后写入覆盖旧值。
    existing = _read_existing_wav(output_path) if output_path.exists() else None
    if existing is not None:
        existing_sec = len(existing) / 16000.0
        # 总采样数 = max(旧时长, 全部片段末尾)
        total_samples = max(int(total_sec * 16000), len(existing), 1)
        merged = np.zeros(total_samples, dtype=np.float32)
        merged[: len(existing)] = existing
        for path, offset_sec in inputs:
            arr = _read_16k_mono(path)
            start = int(offset_sec * 16000)
            end = min(start + len(arr), total_samples)
            if end > start:
                merged[start:end] = arr[: end - start]
        pcm = (np.clip(merged, -1.0, 1.0) * 32767).astype(np.int16)
        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm.tobytes())
        meeting.audio_duration = int(total_sec)
        return output_path

    # ── 首次合并：完整重建 ──
    if len(inputs) == 1 and inputs[0][1] == 0:
        # 单文件且 offset=0：直接转 wav（保持原逻辑）
        import ffmpeg
        (
            ffmpeg
            .input(inputs[0][0])
            .output(str(output_path), ac=1, ar=16000)
            .overwrite_output()
            .run(quiet=True)
        )
    else:
        # 总采样数（16k 单声道）
        total_samples = max(int(total_sec * 16000), 1)
        merged = np.zeros(total_samples, dtype=np.float32)
        for path, offset_sec in inputs:
            arr = _read_16k_mono(path)
            start = int(offset_sec * 16000)
            end = min(start + len(arr), total_samples)
            if end > start:
                merged[start:end] = arr[: end - start]

        # 写 16k 单声道 wav
        pcm = (np.clip(merged, -1.0, 1.0) * 32767).astype(np.int16)
        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm.tobytes())

    meeting.audio_duration = int(total_sec)
    return output_path


def _diarize_sync(audio_path: str) -> list[dict]:
    """同步执行 sherpa-onnx 说话人分离（线程池内）。

    官方 API：``sd.process(float32_audio)`` 直接传波形数组（16k 单声道），
    返回 ``sort_by_start_time()`` 的说话人区间列表。
    """
    import sherpa_onnx

    # 模型目录约定：segmentation.onnx + embedding.onnx（已预下载放置）
    seg_model = DIARIZATION_DIR / "segmentation.onnx"
    emb_model = DIARIZATION_DIR / "embedding.onnx"

    config = sherpa_onnx.OfflineSpeakerDiarizationConfig(
        segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
            pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(
                model=str(seg_model),
            ),
        ),
        embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(
            model=str(emb_model),
        ),
        clustering=sherpa_onnx.FastClusteringConfig(
            num_clusters=-1,  # 自动估计人数
            threshold=0.5,
        ),
        min_duration_on=0.3,
        min_duration_off=0.5,
    )
    sd = sherpa_onnx.OfflineSpeakerDiarization(config)

    # 读取 16k 单声道 wav，转 float32
    import wave

    import numpy as np

    with wave.open(audio_path, "rb") as wf:
        assert wf.getframerate() == 16000, "要求 16kHz wav"
        assert wf.getnchannels() == 1, "要求单声道"
        frames = wf.readframes(wf.getnframes())
    samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

    result = sd.process(samples).sort_by_start_time()
    segments = []
    for seg in result:
        segments.append({
            "start": float(seg.start),
            "end": float(seg.end),
            "speaker": int(seg.speaker) + 1,  # 1 起
        })
    return segments


def _match_speaker(seg: dict, diar_segments: list[dict]) -> int:
    """句级片段与说话人区间按时间重叠最大者对齐。"""
    best_speaker = 0
    best_overlap = 0.0
    for d in diar_segments:
        overlap = min(seg["end"], d["end"]) - max(seg["start"], d["start"])
        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = d["speaker"]
    return best_speaker


# ── 会议纪要生成 ─────────────────────────────────────────────────────────

async def _build_source_material(meeting: AimeetingMeeting) -> str:
    """将会议信息与完整转写文本拼接为 AI 输入的文本素材。"""
    lines: list[str] = []
    lines.append(f"会议标题：{meeting.title}")
    if meeting.participants:
        lines.append(f"参会人：{meeting.participants}")
    if meeting.start_time:
        lines.append(f"会议时间：{meeting.start_time.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("【会议语音转写全文】")
    if meeting.transcript_text.strip():
        lines.append(meeting.transcript_text)
    else:
        lines.append("（暂无转写文本）")
    return "\n".join(lines)


async def generate_minutes(
    db: AsyncSession, meeting: AimeetingMeeting, user_id: int = 0
) -> AimeetingMinutes:
    """为指定会议生成会议总结（一句话）与结构化会议纪要。

    流程：
    1. 校验会议存在。
    2. 拼接转写文本为素材。
    3. 获取启用中的 AI 供应商，调用模型生成。
    4. 解析 JSON 结果，写入 aimeeting_minutes 表。
    5. 若 AI 未配置或调用失败，写入失败状态供前端提示。
    """
    source_material = await _build_source_material(meeting)

    result = await db.execute(
        select(AimeetingMinutes).where(AimeetingMinutes.meeting_id == meeting.id)
    )
    minutes_row = result.scalars().first()
    if not minutes_row:
        minutes_row = AimeetingMinutes(meeting_id=meeting.id)
        db.add(minutes_row)

    minutes_row.status = "pending"
    minutes_row.source_material = source_material
    minutes_row.error = ""
    minutes_row.generated_by = user_id or 0
    await db.commit()
    await db.refresh(minutes_row)

    provider = await _get_enabled_provider_or_none(db)
    if provider is None:
        minutes_row.status = "failed"
        minutes_row.error = "未配置可用的 AI 模型供应商，请先在「模型密钥管理」中添加"
        await db.commit()
        await db.refresh(minutes_row)
        return minutes_row

    try:
        messages = [
            {
                "role": "user",
                "content": (
                    f"{MINUTES_SYSTEM_PROMPT}\n\n"
                    "以下是本次会议的语音转写文本：\n\n"
                    f"{source_material}\n\n"
                    "请根据以上转写文本生成会议总结和会议纪要，严格按要求的 JSON 结构输出。"
                ),
            }
        ]
        result_dict = await chat_non_stream(
            messages=messages,
            provider=provider,
            max_tokens=4000,
            temperature=0.3,
            enable_tools=False,
        )
        content = result_dict.get("content", "").strip()
        parsed = _parse_ai_content(content)

        minutes_row.summary = parsed.get("summary", "")
        minutes_row.minutes = parsed.get("minutes", content)
        minutes_row.status = "success"
        minutes_row.provider_name = provider.name
        minutes_row.error = ""
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"[Aimeeting] 生成会议纪要失败: {exc}")
        minutes_row.status = "failed"
        minutes_row.error = f"生成失败：{exc}"
        minutes_row.provider_name = provider.name if provider else ""

    await db.commit()
    await db.refresh(minutes_row)
    return minutes_row


async def _get_enabled_provider_or_none(db: AsyncSession):
    """获取第一个启用的 AI 供应商，无则返回 None。"""
    try:
        return await crud_ai_provider.get_first_enabled(db)
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"[aimeeting] 获取 AI 供应商失败: {exc}")
        return None


def _parse_ai_content(content: str) -> dict:
    """解析 AI 返回的 JSON 内容，容错处理 markdown 包裹。"""
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        return {"summary": "", "minutes": text}


def generate_meeting_code() -> str:
    """生成会议编号（8 位大写字母+数字，如 A1B2C3D4）。"""
    import random
    import string

    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=8))


# ── 会后处理链路（结束后：等待转写完成 → 说话人分离 → AI 纪要）──────────

async def finalize_meeting(meeting_id: int) -> None:
    """会议结束后的完整处理链路（按序执行，失败不中断后续步骤）。

    在独立后台任务中运行，使用自己的数据库会话。
    """
    from src.db import get_db_context

    async with get_db_context() as db:
        meeting = await db.get(AimeetingMeeting, meeting_id)
        if not meeting or meeting.is_deleted:
            logger.warning(f"[Aimeeting] finalize 会议 {meeting_id} 不存在，跳过")
            return

        # 0. 等待全部转写记录完成（最多 90 秒，防止结束时最后几段漏掉）
        done = await wait_for_records_done(db, meeting, timeout=90.0)
        if not done:
            logger.warning(f"[Aimeeting] 会议 {meeting_id} 转写等待超时，继续后续处理")

        # 1. 合并句级转写
        try:
            await merge_transcript_to_meeting(db, meeting)
        except Exception as exc:  # noqa: BLE001
            logger.exception(f"[Aimeeting] 合并转写失败: {exc}")

        # 2. 说话人分离（模型存在才跑）
        if DIARIZATION_DIR.exists() and meeting.transcript_text.strip():
            try:
                await run_diarization(db, meeting)
            except Exception as exc:  # noqa: BLE001
                logger.exception(f"[Aimeeting] 说话人分离失败: {exc}")
        else:
            meeting.diarization_status = "none"
            await db.commit()
            await db.refresh(meeting)

        # 3. AI 纪要（说话人标注后的文本作为素材，纪要质量更高）
        try:
            await generate_minutes(db, meeting, user_id=0)
        except Exception as exc:  # noqa: BLE001
            logger.exception(f"[Aimeeting] 生成纪要失败: {exc}")
