"""AI 会议助手插件——API 路由。

权限说明：
- 管理端接口：沿用 ``aimeeting:`` 权限前缀（需登录）。
- 用户端接口：通过「会议编号 + 设备标识」无感认证，不依赖登录。

核心工作流：
开始会议进行录音（15 秒切片上传）→ 后台转写（faster-whisper，句级时间戳）
→ 实时对话流展示 → 结束会议 → 说话人分离（会后批处理）→ LLM 总结 + 结构化纪要
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user
from src.core.deps import require_permission as _require_perm
from src.core.exceptions import success_response
from src.db import get_db
from src.models import User
from src.plugins.builtin.aimeeting.models import (
    AimeetingHighlight,
    AimeetingMark,
    AimeetingMeeting,
    AimeetingMinuteRecord,
    AimeetingMinutes,
    AimeetingSpeaker,
    MeetingStatus,
    TranscriptStatus,
)
from src.plugins.builtin.aimeeting.schemas import (
    DeviceBind,
    HighlightCreate,
    HighlightOut,
    MarkCreate,
    MarkOut,
    MeetingCreate,
    MeetingBatchDelete,
    MeetingLookup,
    MeetingOut,
    MeetingRename,
    MeetingStatusUpdate,
    MeetingUpdate,
    MinutesOut,
    RecordOut,
    SpeakerOut,
    SpeakerUpdate,
)
from src.plugins.builtin.aimeeting.services import (
    AUDIO_STORE_DIR,
    auto_title,
    finalize_meeting,
    generate_meeting_code,
    generate_minutes,
    speaker_code,
    transcribe_record_async,
)

router = APIRouter(prefix="/aimeeting", tags=["AI 会议助手"])


def _now() -> datetime:
    """当前 UTC 时间。"""
    return datetime.now(timezone.utc)


async def _get_meeting_or_404(db: AsyncSession, meeting_id: int) -> AimeetingMeeting:
    """获取会议，不存在或已删除则抛 404。"""
    meeting = await db.get(AimeetingMeeting, meeting_id)
    if not meeting or meeting.is_deleted:
        raise HTTPException(status_code=404, detail="会议不存在")
    return meeting


async def _get_meeting_by_code_or_404(db: AsyncSession, meeting_code: str) -> AimeetingMeeting:
    """通过会议编号获取会议。"""
    result = await db.execute(
        select(AimeetingMeeting).where(
            AimeetingMeeting.meeting_code == meeting_code,
            AimeetingMeeting.is_deleted == False,  # noqa: E712
        )
    )
    meeting = result.scalars().first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议编号不存在")
    return meeting


async def _check_device(meeting: AimeetingMeeting, device_id: str):
    """轻量设备校验（不提交，改由调用方统一 commit）。"""
    if not meeting.device_id:
        meeting.device_id = device_id
    elif meeting.device_id != device_id:
        raise HTTPException(status_code=403, detail="该会议已绑定其他设备")


async def _check_meeting(db: AsyncSession, meeting: AimeetingMeeting, device_id: str):
    """校验设备访问权限并绑定。

    注意：首次绑定会触发 ``db.commit()``，此时 ``updated_at`` 等由数据库
    ``onupdate`` 生成的字段会过期，必须在 commit 后 ``refresh`` 整个对象，
    否则后续 ``MeetingOut.model_validate`` 序列化时访问过期属性会触发
    MissingGreenlet。
    """
    if not meeting.device_id:
        meeting.device_id = device_id
        await db.commit()
        await db.refresh(meeting)
    elif meeting.device_id != device_id:
        raise HTTPException(status_code=403, detail="该会议已绑定其他设备")


def _sanitize_client_meeting(data: dict) -> dict:
    """用户端只暴露必要字段（transcript_json 由 client_get_meeting 保留，
    实时对话流数据源，勿在此处删除）。"""
    data.pop("transcript_text", None)
    data.pop("device_id", None)
    data.pop("creator_id", None)
    data.pop("creator_name", None)
    data.pop("audio_file", None)
    return data


# ─────────────────────────────────────────────────────────────────────────
# 用户端接口（无感登录：会议编号 + 设备标识）
# ─────────────────────────────────────────────────────────────────────────

@router.post("/client/meetings/lookup")
async def client_lookup_meeting(
    body: MeetingLookup,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """用户端：输入会议编号查询会议（无感绑定设备）。"""
    meeting = await _get_meeting_by_code_or_404(db, body.meeting_code.strip().upper())
    await _check_meeting(db, meeting, body.device_id)
    data = MeetingOut.model_validate(meeting).model_dump(mode="json")
    return success_response(data=_sanitize_client_meeting(data))


@router.post("/client/meetings")
async def client_create_meeting(
    body: MeetingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """用户端：创建会议（名称可选，留空按时间自动命名）。"""
    # 生成唯一会议编号
    code = generate_meeting_code()
    while True:
        exists = (
            await db.execute(
                select(AimeetingMeeting.id).where(AimeetingMeeting.meeting_code == code)
            )
        ).scalars().first()
        if not exists:
            break
        code = generate_meeting_code()

    title = body.title.strip() or auto_title()
    meeting = AimeetingMeeting(
        title=title,
        meeting_code=code,
        participants=body.participants,
        start_time=body.start_time,
        status=MeetingStatus.SCHEDULED,
        creator_id=0,
        creator_name="用户端",
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return success_response(
        data=MeetingOut.model_validate(meeting).model_dump(mode="json"),
        msg="会议创建成功，会议编号：" + code,
    )


@router.patch("/client/meetings/{meeting_id}")
async def client_rename_meeting(
    meeting_id: int,
    body: MeetingRename,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """用户端：修改会议名称（全程可改）。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, body.device_id)
    new_title = body.title.strip()
    if not new_title:
        raise HTTPException(status_code=422, detail="会议名称不能为空")
    meeting.title = new_title
    await db.commit()
    await db.refresh(meeting)
    return success_response(
        data=MeetingOut.model_validate(meeting).model_dump(mode="json"),
        msg="会议名称已更新",
    )


@router.post("/client/meetings/{meeting_id}/audio")
async def client_upload_audio(
    meeting_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
    device_id: str = Form(...),
    duration: int = Form(default=0),
    offset_sec: int = Form(default=0, ge=0),
):
    """用户端：上传一段录音切片，登记后立即返回，转写在后台执行。

    15 秒实时切片方案：前端每 15 秒上传一段，携带会议内偏移秒数。
    接口立即返回（转写后台异步），前端轮询 /client/meetings/{id} 获取
    最新 transcript_json 渲染实时对话流。
    """
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, device_id)

    # 会议状态流转：进行中
    if meeting.status == MeetingStatus.SCHEDULED:
        meeting.status = MeetingStatus.IN_PROGRESS
        meeting.actual_start = meeting.actual_start or _now()

    # 校验文件类型与大小（≤50MB）
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="录音文件过大（上限 50MB）")

    # 保存录音文件
    AUDIO_STORE_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "audio.webm").suffix.lower() or ".webm"
    if ext not in {".webm", ".ogg", ".wav", ".m4a", ".mp3", ".mp4", ".aac"}:
        ext = ".webm"
    saved_name = f"m{meeting_id}_{uuid.uuid4().hex[:12]}{ext}"
    saved_path = AUDIO_STORE_DIR / saved_name
    content = await file.read()
    with open(saved_path, "wb") as f:
        f.write(content)

    # 登记转写记录（processing 状态），后台异步转写
    record = AimeetingMinuteRecord(
        meeting_id=meeting.id,
        offset_sec=offset_sec,
        audio_path=str(saved_path),
        audio_duration=duration,
        transcript="",
        transcript_status=TranscriptStatus.PROCESSING,
        device_id=device_id,
        creator_id=0,
        creator_name="用户端",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    # 后台转写（不阻塞本接口，前端轮询看结果）
    asyncio.create_task(transcribe_record_async(record.id))

    return success_response(
        data={"record_id": record.id, "transcript_status": record.transcript_status},
        msg="录音已接收，正在转写",
    )


@router.post("/client/meetings/{meeting_id}/start")
async def client_start_meeting(
    meeting_id: int,
    body: DeviceBind,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """用户端：正式开始会议（开始计时，状态流转 scheduled → in_progress）。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, body.device_id)

    if meeting.status == MeetingStatus.ENDED:
        raise HTTPException(status_code=409, detail="会议已结束")
    if meeting.status != MeetingStatus.IN_PROGRESS:
        meeting.status = MeetingStatus.IN_PROGRESS
        meeting.actual_start = meeting.actual_start or _now()
        await db.commit()
        await db.refresh(meeting)

    return success_response(
        data={"status": meeting.status, "actual_start": meeting.actual_start.isoformat() if meeting.actual_start else None},
        msg="会议已开始",
    )


@router.post("/client/meetings/{meeting_id}/finish")
async def client_finish_meeting(
    meeting_id: int,
    body: DeviceBind,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """用户端：结束会议。

    立即返回，不做任何长等待：转写/分离/纪要全部在后台 finalize_meeting 中
    按序执行（含等待在途转写，最长 90 秒），前端轮询 transcript 接口看进度。
    """
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, body.device_id)

    # 是否存在录音记录（无录音则跳过语音链路）
    has_records = (
        await db.execute(
            select(AimeetingMinuteRecord.id)
            .where(
                AimeetingMinuteRecord.meeting_id == meeting.id,
                AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
            )
            .limit(1)
        )
    ).scalars().first()

    meeting.status = MeetingStatus.ENDED
    meeting.actual_end = meeting.actual_end or _now()
    if has_records:
        # 会后链路放后台任务：等转写完 → 合并 → 说话人分离 → AI 纪要
        # （finalize_meeting 内部自带转写等待与状态回写，接口立即返回不阻塞）
        asyncio.ensure_future(finalize_meeting(meeting.id))
    else:
        meeting.audio_duration = meeting.audio_duration or 0
    await db.commit()
    await db.refresh(meeting)

    return success_response(
        data={"status": meeting.status, "transcripts_done": True if not has_records else None},
        msg="会议已结束" + ("" if has_records else "，会议记录已存档"),
    )


@router.get("/client/meetings/{meeting_id}")
async def client_get_meeting(
    meeting_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    device_id: str = Query(..., min_length=8),
):
    """用户端：查询会议详情（含实时对话流、转写进度、纪要状态、说话人）。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_meeting(db, meeting, device_id)

    minutes_row = (
        await db.execute(
            select(AimeetingMinutes).where(AimeetingMinutes.meeting_id == meeting.id)
        )
    ).scalars().first()

    speakers = (
        await db.execute(
            select(AimeetingSpeaker).where(
                AimeetingSpeaker.meeting_id == meeting.id,
                AimeetingSpeaker.is_deleted == False,  # noqa: E712
            )
            .order_by(AimeetingSpeaker.speaker_no.asc())
        )
    ).scalars().all()

    # 在途/失败记录数（前端显示"转写中 N 段"）
    processing_count = (
        await db.execute(
            select(func.count(AimeetingMinuteRecord.id)).where(
                AimeetingMinuteRecord.meeting_id == meeting.id,
                AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
                AimeetingMinuteRecord.transcript_status == TranscriptStatus.PROCESSING,
            )
        )
    ).scalar() or 0
    failed_count = (
        await db.execute(
            select(func.count(AimeetingMinuteRecord.id)).where(
                AimeetingMinuteRecord.meeting_id == meeting.id,
                AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
                AimeetingMinuteRecord.transcript_status == TranscriptStatus.FAILED,
            )
        )
    ).scalar() or 0

    data = MeetingOut.model_validate(meeting).model_dump(mode="json")
    # 用户端保留 transcript_json（实时对话流数据源），去掉完整纯文本等冗余字段
    # 过滤内部隐藏元字段（__merged_record_ids），避免泄露内部实现
    try:
        tj = json.loads(meeting.transcript_json or "[]")
        tj = [s for s in tj if isinstance(s, dict) and "__merged_record_ids" not in s]
        data["transcript_json"] = json.dumps(tj, ensure_ascii=False)
    except json.JSONDecodeError:
        data["transcript_json"] = meeting.transcript_json or "[]"
    data["minutes"] = (
        MinutesOut.model_validate(minutes_row).model_dump(mode="json")
        if minutes_row
        else None
    )
    data["speakers"] = [
        SpeakerOut.model_validate(s).model_dump(mode="json") for s in speakers
    ]
    data["processing_count"] = processing_count
    data["failed_count"] = failed_count
    _sanitize_client_meeting(data)
    return success_response(data=data)


@router.get("/client/meetings/{meeting_id}/transcript")
async def client_get_transcript(
    meeting_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    device_id: str = Query(..., min_length=8),
    after_id: int = Query(default=0, ge=0, description="只返回 id 大于此值的片段（增量轮询）"),
):
    """用户端：轮询接口——轻量返回最新句级转写（实时对话流增量渲染）。

    after_id：前端传入已渲染的最大片段序号（按 start 时间排序的索引），
    后端只返回比它新的片段，避免每 5s 全量重传整场会议转写（P2 卡顿根因）。
    """
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, device_id)

    processing_count = (
        await db.execute(
            select(func.count(AimeetingMinuteRecord.id)).where(
                AimeetingMinuteRecord.meeting_id == meeting.id,
                AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
                AimeetingMinuteRecord.transcript_status == TranscriptStatus.PROCESSING,
            )
        )
    ).scalar() or 0

    try:
        segments = json.loads(meeting.transcript_json or "[]")
    except json.JSONDecodeError:
        segments = []

    # 过滤隐藏元字段（__merged_record_ids）与增量窗口
    segments = [
        s for s in segments
        if isinstance(s, dict) and "__merged_record_ids" not in s
    ]
    if after_id > 0:
        # 片段按 start 升序（merge 已排序），用数组索引作为稳定递增序号
        segments = segments[after_id:]
        seg_id_start = after_id
    else:
        seg_id_start = 0

    # 说话人显示名映射（speaker_no -> display_name）
    speakers = (
        await db.execute(
            select(AimeetingSpeaker).where(
                AimeetingSpeaker.meeting_id == meeting.id,
                AimeetingSpeaker.is_deleted == False,  # noqa: E712
            )
        )
    ).scalars().all()
    speaker_names = {s.speaker_no: s.display_name for s in speakers}

    for idx, seg in enumerate(segments, start=seg_id_start):
        no = seg.get("speaker", 0)
        seg["speaker_name"] = speaker_names.get(no, f"发言者{speaker_code(no)}" if no else "")
        seg["seq"] = idx  # 稳定序号，前端用最大 seq 作为下次 after_id

    return success_response(data={
        "segments": segments,
        "next_after_id": seg_id_start + len(segments),
        "processing_count": processing_count,
        "transcript_status": meeting.transcript_status,
        # 修订号：已合并片段被修改（精修替换文本 / 说话人回填 / 索引位移）时自增。
        # 前端比对本地值，变化则走全量刷新——增量 after_id 索引无法感知原地修改。
        "revision": meeting.transcript_revision or 0,
        "diarization_status": meeting.diarization_status,
        "updated_at": meeting.updated_at.isoformat() if meeting.updated_at else None,
    })


@router.patch("/client/meetings/{meeting_id}/speakers/{speaker_id}")
async def client_update_speaker(
    meeting_id: int,
    speaker_id: int,
    body: SpeakerUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    device_id: str = Query(..., min_length=8),
):
    """用户端：修改说话人显示名称（如「说话人1」→「张三」）。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, device_id)

    speaker = await db.get(AimeetingSpeaker, speaker_id)
    if not speaker or speaker.meeting_id != meeting.id or speaker.is_deleted:
        raise HTTPException(status_code=404, detail="说话人不存在")

    speaker.display_name = body.display_name.strip()
    if not speaker.display_name:
        raise HTTPException(status_code=422, detail="显示名称不能为空")
    await db.commit()
    await db.refresh(speaker)
    return success_response(
        data=SpeakerOut.model_validate(speaker).model_dump(mode="json"),
        msg="说话人名称已更新",
    )


# ── 重点标记 / 自定义标记（用户端） ─────────────────────────────────────

@router.post("/client/meetings/{meeting_id}/highlights")
async def client_create_highlight(
    meeting_id: int,
    body: HighlightCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """用户端：记重点——把当前时间点标记为重点，供会后快速回顾。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, body.device_id)

    # 就近匹配当前时间点对应的转写片段（transcript_json 数组下标）
    segment_idx = -1
    try:
        tj = json.loads(meeting.transcript_json or "[]")
        segs = [s for s in tj if isinstance(s, dict) and "__merged_record_ids" not in s]
        best_idx, best_dist = -1, float("inf")
        for i, s in enumerate(segs):
            dist = abs(float(s.get("start", 0)) - body.offset_sec)
            if dist < best_dist:
                best_idx, best_dist = i, dist
        if best_idx >= 0 and best_dist <= 30:  # 30s 窗口内才关联
            segment_idx = best_idx
    except (json.JSONDecodeError, ValueError):
        segment_idx = -1

    hl = AimeetingHighlight(
        meeting_id=meeting.id,
        offset_sec=body.offset_sec,
        segment_idx=segment_idx,
        text_snapshot=body.text_snapshot.strip(),
        note=body.note.strip(),
        device_id=body.device_id,
    )
    db.add(hl)
    await db.commit()
    await db.refresh(hl)
    return success_response(
        data=HighlightOut.model_validate(hl).model_dump(mode="json"),
        msg="已标记为重点",
    )


@router.delete("/client/meetings/{meeting_id}/highlights/{highlight_id}")
async def client_delete_highlight(
    meeting_id: int,
    highlight_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    device_id: str = Query(..., min_length=8),
):
    """用户端：取消重点标记（软删除）。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, device_id)
    hl = await db.get(AimeetingHighlight, highlight_id)
    if not hl or hl.meeting_id != meeting.id or hl.is_deleted:
        raise HTTPException(status_code=404, detail="标记不存在")
    hl.is_deleted = True
    await db.commit()
    return success_response(msg="已取消重点标记")


@router.get("/client/meetings/{meeting_id}/highlights")
async def client_list_highlights(
    meeting_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    device_id: str = Query(..., min_length=8),
):
    """用户端：查询全部重点标记（含关联转写文本）。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, device_id)
    result = await db.execute(
        select(AimeetingHighlight)
        .where(
            AimeetingHighlight.meeting_id == meeting.id,
            AimeetingHighlight.is_deleted == False,  # noqa: E712
        )
        .order_by(AimeetingHighlight.offset_sec.asc())
    )
    items = result.scalars().all()

    # 若标记无快照，从 transcript_json 就近取转写文本补全
    try:
        tj = json.loads(meeting.transcript_json or "[]")
        segs = [s for s in tj if isinstance(s, dict) and "__merged_record_ids" not in s]
    except json.JSONDecodeError:
        segs = []

    result_data = []
    for hl in items:
        d = HighlightOut.model_validate(hl).model_dump(mode="json")
        if not d["text_snapshot"] and 0 <= hl.segment_idx < len(segs):
            d["text_snapshot"] = segs[hl.segment_idx].get("text", "")
        result_data.append(d)
    return success_response(data=result_data)


@router.post("/client/meetings/{meeting_id}/marks")
async def client_create_mark(
    meeting_id: int,
    body: MarkCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """用户端：在指定时间点插入自定义标记（如「待办」「疑问」）。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, body.device_id)
    mark = AimeetingMark(
        meeting_id=meeting.id,
        offset_sec=body.offset_sec,
        content=body.content.strip(),
        device_id=body.device_id,
    )
    db.add(mark)
    await db.commit()
    await db.refresh(mark)
    return success_response(
        data=MarkOut.model_validate(mark).model_dump(mode="json"),
        msg="标记已添加",
    )


@router.delete("/client/meetings/{meeting_id}/marks/{mark_id}")
async def client_delete_mark(
    meeting_id: int,
    mark_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    device_id: str = Query(..., min_length=8),
):
    """用户端：删除自定义标记。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, device_id)
    mark = await db.get(AimeetingMark, mark_id)
    if not mark or mark.meeting_id != meeting.id or mark.is_deleted:
        raise HTTPException(status_code=404, detail="标记不存在")
    mark.is_deleted = True
    await db.commit()
    return success_response(msg="标记已删除")


@router.get("/client/meetings/{meeting_id}/marks")
async def client_list_marks(
    meeting_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    device_id: str = Query(..., min_length=8),
):
    """用户端：获取会议自定义标记列表。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _check_device(meeting, device_id)
    result = await db.execute(
        select(AimeetingMark)
        .where(
            AimeetingMark.meeting_id == meeting.id,
            AimeetingMark.is_deleted == False,  # noqa: E712
        )
        .order_by(AimeetingMark.offset_sec.asc())
    )
    items = result.scalars().all()
    return success_response(data=[
        MarkOut.model_validate(m).model_dump(mode="json") for m in items
    ])


# ─────────────────────────────────────────────────────────────────────────
# 管理端接口（需登录 + aimeeting: 权限）
# ─────────────────────────────────────────────────────────────────────────

@router.get("/env/check")
async def check_environment(
    _user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:meeting:list"))],
):
    """管理端：运行环境自检（只读诊断：依赖库版本、模型文件、ffmpeg）。

    本接口不执行任何安装/下载动作；补齐环境请运行 backend/scripts/setup_aimeeting_env.sh。
    """
    from src.plugins.builtin.aimeeting.envcheck import check_env

    return success_response(data=check_env())


@router.get("/meetings")
async def list_meetings(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:meeting:list"))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str = Query(default="", description="按状态筛选"),
    keyword: str = Query(default="", description="标题/编号搜索关键词"),
):
    """管理端：分页查询会议列表（历史会议管理）。"""
    stmt = select(AimeetingMeeting).where(AimeetingMeeting.is_deleted == False)  # noqa: E712
    if status:
        stmt = stmt.where(AimeetingMeeting.status == status)
    if keyword:
        stmt = stmt.where(
            (AimeetingMeeting.title.ilike(f"%{keyword}%"))
            | (AimeetingMeeting.meeting_code.ilike(f"%{keyword}%"))
        )

    count_stmt = select(func.count(AimeetingMeeting.id)).where(
        AimeetingMeeting.is_deleted == False  # noqa: E712
    )
    if status:
        count_stmt = count_stmt.where(AimeetingMeeting.status == status)
    if keyword:
        count_stmt = count_stmt.where(
            (AimeetingMeeting.title.ilike(f"%{keyword}%"))
            | (AimeetingMeeting.meeting_code.ilike(f"%{keyword}%"))
        )
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        stmt.order_by(AimeetingMeeting.start_time.desc().nullslast(), AimeetingMeeting.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = (await db.execute(stmt)).scalars().all()
    if not items:
        return success_response(data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [],
        })

    meeting_ids = [m.id for m in items]
    record_counts = dict(
        (
            await db.execute(
                select(AimeetingMinuteRecord.meeting_id, func.count(AimeetingMinuteRecord.id))
                .where(
                    AimeetingMinuteRecord.meeting_id.in_(meeting_ids),
                    AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
                )
                .group_by(AimeetingMinuteRecord.meeting_id)
            )
        ).all()
    )
    minutes_rows = (
        await db.execute(
            select(AimeetingMinutes.meeting_id, AimeetingMinutes.status).where(
                AimeetingMinutes.meeting_id.in_(meeting_ids)
            )
        )
    ).all()
    minutes_status_map = {mid: status for mid, status in minutes_rows}

    result_items = []
    for m in items:
        data = MeetingOut.model_validate(m).model_dump(mode="json")
        data["record_count"] = record_counts.get(m.id, 0)
        data["minutes_status"] = minutes_status_map.get(m.id, "none")
        result_items.append(data)

    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": result_items,
    })


@router.get("/meetings/{meeting_id}")
async def get_meeting(
    meeting_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:meeting:list"))],
):
    """管理端：查询单个会议详情（含记录条数与纪要状态）。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    record_count = (
        await db.execute(
            select(func.count(AimeetingMinuteRecord.id)).where(
                AimeetingMinuteRecord.meeting_id == meeting.id,
                AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
            )
        )
    ).scalar() or 0
    minutes_row = (
        await db.execute(
            select(AimeetingMinutes).where(AimeetingMinutes.meeting_id == meeting.id)
        )
    ).scalars().first()
    speakers = (
        await db.execute(
            select(AimeetingSpeaker).where(
                AimeetingSpeaker.meeting_id == meeting.id,
                AimeetingSpeaker.is_deleted == False,  # noqa: E712
            )
            .order_by(AimeetingSpeaker.speaker_no.asc())
        )
    ).scalars().all()

    data = MeetingOut.model_validate(meeting).model_dump(mode="json")
    data["record_count"] = record_count
    data["minutes_status"] = minutes_row.status if minutes_row else "none"
    data["minutes"] = (
        MinutesOut.model_validate(minutes_row).model_dump(mode="json")
        if minutes_row
        else None
    )
    data["speakers"] = [
        SpeakerOut.model_validate(s).model_dump(mode="json") for s in speakers
    ]
    return success_response(data=data)


@router.post("/meetings")
async def create_meeting(
    body: MeetingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:meeting:create"))],
):
    """管理端：创建会议（名称可选，留空自动命名）。"""
    code = generate_meeting_code()
    while True:
        exists = (
            await db.execute(
                select(AimeetingMeeting.id).where(AimeetingMeeting.meeting_code == code)
            )
        ).scalars().first()
        if not exists:
            break
        code = generate_meeting_code()
    title = body.title.strip() or auto_title()
    meeting = AimeetingMeeting(
        title=title,
        meeting_code=code,
        participants=body.participants,
        start_time=body.start_time,
        status=MeetingStatus.SCHEDULED,
        creator_id=user.id,
        creator_name=user.nickname or user.username,
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return success_response(data=MeetingOut.model_validate(meeting).model_dump(mode="json"), msg=f"会议创建成功，编号 {code}")


@router.put("/meetings/{meeting_id}")
async def update_meeting(
    meeting_id: int,
    body: MeetingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:meeting:edit"))],
):
    """管理端：更新会议基本信息（含改名）。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(meeting, key, value)
    await db.commit()
    await db.refresh(meeting)
    return success_response(data=MeetingOut.model_validate(meeting).model_dump(mode="json"), msg="会议更新成功")


@router.put("/meetings/{meeting_id}/status")
async def update_meeting_status(
    meeting_id: int,
    body: MeetingStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:meeting:edit"))],
):
    """管理端：流转会议状态。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    new_status = body.status
    valid_statuses = {
        MeetingStatus.SCHEDULED,
        MeetingStatus.IN_PROGRESS,
        MeetingStatus.ENDED,
        MeetingStatus.CANCELLED,
    }
    if new_status not in valid_statuses:
        raise HTTPException(status_code=422, detail="无效的会议状态")

    meeting.status = new_status
    if new_status == MeetingStatus.IN_PROGRESS and not meeting.actual_start:
        meeting.actual_start = _now()
    if new_status == MeetingStatus.ENDED and not meeting.actual_end:
        meeting.actual_end = _now()
    await db.commit()
    await db.refresh(meeting)
    return success_response(data=MeetingOut.model_validate(meeting).model_dump(mode="json"), msg="会议状态已更新")


async def _soft_delete_meeting(db: AsyncSession, meeting: AimeetingMeeting) -> None:
    """软删除单个会议及其转写记录与说话人（不提交，由调用方 commit）。"""
    meeting.is_deleted = True
    await db.execute(
        AimeetingMinuteRecord.__table__.update()
        .where(AimeetingMinuteRecord.meeting_id == meeting.id)
        .values(is_deleted=True)
    )
    await db.execute(
        AimeetingSpeaker.__table__.update()
        .where(AimeetingSpeaker.meeting_id == meeting.id)
        .values(is_deleted=True)
    )
    await db.execute(
        AimeetingHighlight.__table__.update()
        .where(AimeetingHighlight.meeting_id == meeting.id)
        .values(is_deleted=True)
    )
    await db.execute(
        AimeetingMark.__table__.update()
        .where(AimeetingMark.meeting_id == meeting.id)
        .values(is_deleted=True)
    )


@router.delete("/meetings/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:meeting:delete"))],
):
    """管理端：删除会议（软删除，同时删除其记录与纪要）。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    await _soft_delete_meeting(db, meeting)
    await db.commit()
    return success_response(msg="会议删除成功")


@router.post("/meetings/batch-delete")
async def batch_delete_meetings(
    body: MeetingBatchDelete,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:meeting:delete"))],
):
    """管理端：批量删除会议（软删除，同时删除其转写记录与说话人）。"""
    ids = sorted(set(body.ids))
    result = await db.execute(
        select(AimeetingMeeting).where(
            AimeetingMeeting.id.in_(ids),
            AimeetingMeeting.is_deleted == False,  # noqa: E712
        )
    )
    meetings = result.scalars().all()
    for meeting in meetings:
        await _soft_delete_meeting(db, meeting)
    await db.commit()
    return success_response(
        data={"deleted": len(meetings), "requested": len(ids)},
        msg=f"已删除 {len(meetings)} 个会议",
    )


# ── 转写记录（管理端查看） ─────────────────────────────────────────────

@router.get("/meetings/{meeting_id}/records")
async def list_records(
    meeting_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:record:list"))],
):
    """管理端：查询会议的转写记录列表（多段录音的转写结果）。"""
    await _get_meeting_or_404(db, meeting_id)
    result = await db.execute(
        select(AimeetingMinuteRecord)
        .where(
            AimeetingMinuteRecord.meeting_id == meeting_id,
            AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
        )
        .order_by(AimeetingMinuteRecord.id.asc())
    )
    records = result.scalars().all()
    return success_response(data=[
        RecordOut.model_validate(r).model_dump(mode="json") for r in records
    ])


@router.post("/meetings/{meeting_id}/minutes/generate")
async def generate_meeting_minutes(
    meeting_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:minutes:generate"))],
):
    """管理端：触发 AI 生成会议总结与会议纪要。"""
    meeting = await _get_meeting_or_404(db, meeting_id)
    minutes_row = await generate_minutes(db, meeting, user_id=user.id)
    return success_response(
        data=MinutesOut.model_validate(minutes_row).model_dump(mode="json"),
        msg="生成成功" if minutes_row.status == "success" else "生成未完成",
    )


@router.get("/meetings/{meeting_id}/minutes")
async def get_meeting_minutes(
    meeting_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    _perm: Annotated[User, Depends(_require_perm("aimeeting:minutes:list"))],
):
    """管理端：查询会议的 AI 纪要。"""
    await _get_meeting_or_404(db, meeting_id)
    minutes_row = (
        await db.execute(
            select(AimeetingMinutes).where(AimeetingMinutes.meeting_id == meeting_id)
        )
    ).scalars().first()
    if not minutes_row:
        return success_response(data=None)
    return success_response(data=MinutesOut.model_validate(minutes_row).model_dump(mode="json"))
