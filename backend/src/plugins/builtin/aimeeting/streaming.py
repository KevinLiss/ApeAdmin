"""AI 会议助手插件——WebSocket 流式 ASR 端点。

P3 方案：sherpa-onnx streaming zipformer（实时初稿）→ faster-whisper 二遍精修。

协议（前端 AudioWorklet → 本端点）：
- 建立连接后，客户端先发一条 JSON 文本帧：
    {"type": "hello", "meeting_id": 123, "device_id": "xxxx", "offset_sec": 0}
  服务端校验会议存在 + 设备绑定，返回 {"type": "ready", "sampling_rate": 16000}
- 之后音频以二进制帧发送：PCM16 单声道 16kHz（AudioWorklet 直接输出）
- 服务端实时回推文本帧：
  - {"type": "partial", "text": "...", "segment": n}        流式初稿（持续更新）
  - {"type": "final", "text": "...", "start": 12.3, "end": 15.6, "record_id": 1}  段定稿
  - {"type": "refined", "text": "...", "start": 12.3, "end": 15.6, "record_id": 1} 二遍精修
  - {"type": "error", "message": "..."}                      错误
- 客户端可发 {"type": "done"} 结束会话（服务端补尾 0.3s padding 收尾落库）

设计要点：
- 流式初稿：sherpa-onnx OnlineRecognizer（zipformer transducer，int8，CPU）
- endpoint 检测：is_endpoint() 触发段定稿，reset() 开始新段
- 二遍精修：endpoint 定稿时，把该段 PCM 缓存转 wav，交给 faster-whisper 精修
  （异步，不阻塞流式循环），精修文本替换初稿落库
- 落库复用现有 aimeeting_records 表：一段一条记录，merge_transcript_to_meeting 增量合并，
  前端现有 transcript 轮询天然可见
- 段时间模型：会话维护累计消费时长 elapsed_sec；段 start = 段开始时刻的累计时长，
  段 end = 定稿时刻的累计时长（均为会议内绝对偏移 = base_offset + 会话内偏移）
"""
import asyncio
import json
import math
import struct
import wave
from pathlib import Path

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from sqlalchemy import select

from src.db import get_db_context
from src.plugins.builtin.aimeeting.models import (
    AimeetingMeeting,
    AimeetingMinuteRecord,
    MeetingStatus,
    TranscriptStatus,
)
from src.plugins.builtin.aimeeting.services import (
    AUDIO_STORE_DIR,
    DIARIZATION_DIR,
    _should_run_incremental,
    merge_transcript_to_meeting,
    run_diarization,
    update_merged_segment,
)

router = APIRouter(prefix="/aimeeting", tags=["AI 会议助手-流式转写"])

# 后台任务强引用集合：asyncio.create_task 返回的 Task 若无引用可能被 GC 提前回收
# （表现为精修/分离静默不执行）。任务完成后自动从集合移除。
_bg_tasks: set[asyncio.Task] = set()


def _spawn_bg(coro) -> None:
    """派发后台任务并持有强引用，避免被垃圾回收中断。"""
    task = asyncio.create_task(coro)
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)

# ── 流式识别器（懒加载单例）──────────────────────────────────────────────
_streaming_recognizer = None

# 模型目录（sherpa-onnx streaming zipformer zh 14M int8）
_STREAMING_MODEL_DIR = Path(__file__).resolve().parents[4] / "models" / "sherpa-streaming-zh-14m"

# 采样率（sherpa-onnx 固定 16k）
SAMPLE_RATE = 16000

# 二遍精修并发上限（faster-whisper 与离线转写共用 CPU）
_refine_sem = asyncio.Semaphore(1)


def _get_streaming_recognizer():
    """懒加载 sherpa-onnx 流式识别器（创建后只读，GIL 保护并发访问）。"""
    global _streaming_recognizer
    if _streaming_recognizer is None:
        import sherpa_onnx

        model_dir = _STREAMING_MODEL_DIR
        if not model_dir.exists():
            raise RuntimeError(f"流式模型目录不存在: {model_dir}")
        _streaming_recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=str(model_dir / "tokens.txt"),
            encoder=str(model_dir / "encoder.int8.onnx"),
            decoder=str(model_dir / "decoder.int8.onnx"),
            joiner=str(model_dir / "joiner.int8.onnx"),
            num_threads=2,
            sample_rate=SAMPLE_RATE,
            feature_dim=80,
            decoding_method="greedy_search",
            enable_endpoint_detection=True,
            rule1_min_trailing_silence=2.4,
            rule2_min_trailing_silence=1.2,
            rule3_min_utterance_length=300,
        )
        logger.info("[Aimeeting] sherpa-onnx 流式识别器加载完成")
    return _streaming_recognizer


class StreamingSession:
    """单条 WebSocket 连接的流式 ASR 会话。

    - 维护自己的 OnlineStream 实例（流式状态不跨连接共享）
    - 段缓存：当前段累计的 PCM 样本（供二遍精修）
    - endpoint 触发时：发送 final → 缓存段存 wav → 异步 faster-whisper 精修
      → 精修结果写回 record → merge 到会议
    """

    def __init__(self, websocket: WebSocket, meeting_id: int, device_id: str, base_offset: float = 0.0):
        self.ws = websocket
        self.meeting_id = meeting_id
        self.device_id = device_id
        self.base_offset = base_offset  # 会话起始的会议内偏移（秒）
        self.recognizer = None
        self.stream = None
        # 会话内累计消费时长（秒），作为段时间戳依据
        self._elapsed_sec = 0.0
        # 当前段缓存（PCM int16 list），供二遍精修
        self.cur_segment_samples: list[int] = []
        self.cur_segment_start = base_offset  # 当前段的会议内绝对偏移（秒）
        self.segment_no = 0
        self.closed = False
        self._seg_lock = asyncio.Lock()

    # ── 生命周期 ─────────────────────────────────────────────────────
    async def open(self):
        """初始化识别器与流（懒加载，首次连接时可能耗时）。"""
        self.recognizer = await asyncio.to_thread(_get_streaming_recognizer)
        self.stream = self.recognizer.create_stream()

    async def close(self):
        """收尾：输入结束 + 冲刷残留段，然后释放。"""
        if self.stream is None:
            return
        try:
            # 补 0.3s 尾静音，让模型吐出最后一段
            tail = np.zeros(int(SAMPLE_RATE * 0.3), dtype=np.float32)
            self.stream.accept_waveform(SAMPLE_RATE, tail)
            self.stream.input_finished()
            while self.recognizer.is_ready(self.stream):
                self.recognizer.decode_stream(self.stream)
            tail_text = self.recognizer.get_result(self.stream).strip()
            if tail_text:
                await self._finalize_segment(tail_text)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[streaming] close 冲刷失败 meeting={self.meeting_id}: {exc}")

    # ── 主循环：接收音频 ─────────────────────────────────────────────
    async def feed(self, samples: bytes):
        """处理一帧 PCM16 音频（来自 WebSocket 二进制帧）。"""
        if self.stream is None or self.closed:
            return
        # bytes → int16 list（sherpa-onnx accept_waveform 需要 Sequence[float]）
        if len(samples) < 2:
            return
        ints = list(struct.unpack(f"<{len(samples) // 2}h", samples))
        if not ints:
            return

        self._elapsed_sec += len(ints) / SAMPLE_RATE
        self.stream.accept_waveform(SAMPLE_RATE, ints)
        # 当前段缓存（供二遍精修）
        self.cur_segment_samples.extend(ints)

        # 解码到就绪
        while self.recognizer.is_ready(self.stream):
            self.recognizer.decode_stream(self.stream)

        result = self.recognizer.get_result(self.stream).strip()
        if result:
            await self.ws.send_json({
                "type": "partial",
                "text": result,
                "segment": self.segment_no,
            })

        # endpoint 检测：一句话说完了，定稿
        if self.recognizer.is_endpoint(self.stream):
            final_text = self.recognizer.get_result(self.stream).strip()
            if final_text:
                await self._finalize_segment(final_text)
            self.recognizer.reset(self.stream)
            self.segment_no += 1
            self.cur_segment_start = self.base_offset + self._elapsed_sec
            self.cur_segment_samples = []

    # ── 段定稿 ──────────────────────────────────────────────────────
    async def _finalize_segment(self, text: str):
        """一段定稿：落库 record + 异步精修 + 发 final 消息。"""
        async with self._seg_lock:
            start = self.cur_segment_start
            end = self.base_offset + self._elapsed_sec
            # 落库 + 精修
            record_id = await self._persist_segment(text, start, end)
            await self.ws.send_json({
                "type": "final",
                "text": text,
                "start": round(start, 2),
                "end": round(end, 2),
                "record_id": record_id,
                "segment": self.segment_no,
            })
            # 异步精修（不阻塞流式主循环）
            _spawn_bg(self._refine_segment(record_id, start, end))

    async def _persist_segment(self, text: str, start: float, end: float) -> int:
        """把一段定稿转写落库为 aimeeting_records 记录（复用 merge 链路）。"""
        async with get_db_context() as db:
            meeting = await db.get(AimeetingMeeting, self.meeting_id)
            if not meeting or meeting.is_deleted:
                return 0
            # 缓存样本转 wav（供 whisper 精修）
            wav_path = self._dump_segment_wav(start)
            record = AimeetingMinuteRecord(
                meeting_id=self.meeting_id,
                offset_sec=int(start),
                audio_path=str(wav_path) if wav_path else "",
                # 含头部对齐静音的时长：wav 从 int(start) 起、到 end 止，
                # 向上取整确保 merge 计算 total_sec 不会裁掉尾音。
                audio_duration=max(math.ceil(end - int(start)), 0),
                transcript=text,
                segments_json=json.dumps([{
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "text": text,
                    "speaker": 0,
                }], ensure_ascii=False),
                transcript_status=TranscriptStatus.SUCCESS,
                device_id=self.device_id,
                creator_id=0,
                creator_name="用户端-流式",
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)
            # 增量合并到会议 transcript_json（前端实时可见）
            await merge_transcript_to_meeting(db, meeting)
            # 节流触发增量说话人分离（复用旧链路逻辑；异步执行不阻塞流式主循环）
            should_diar = (
                meeting.status == MeetingStatus.IN_PROGRESS
                and DIARIZATION_DIR.exists()
                and meeting.transcript_text.strip()
                and _should_run_incremental(self.meeting_id)
            )
            rid = record.id  # session 关闭前捕获，避免 detached instance 访问
        if should_diar:
            _spawn_bg(self._run_incremental_diarization())
        return rid

    async def _run_incremental_diarization(self) -> None:
        """流式链路增量说话人分离（独立 db 会话，后台执行）。

        与旧切片链路 services.transcribe_record_async 中的增量分离语义一致：
        tail_sec 窗口分离 + 会议级锁串行化（锁内已处理并发跳过）。
        """
        try:
            async with get_db_context() as db:
                meeting = await db.get(AimeetingMeeting, self.meeting_id)
                if not meeting or meeting.is_deleted:
                    return
                await run_diarization(db, meeting, incremental=True, tail_sec=300)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[streaming] 增量说话人分离失败 meeting={self.meeting_id}: {exc}")

    def _dump_segment_wav(self, start_sec: float) -> Path | None:
        """把当前段缓存转成 16k 单声道 wav（供 whisper 精修 + 说话人分离），存音频目录。

        时间轴对齐：record.offset_sec 是整数秒（int(start_sec)），而段音频实际
        从精确的 start_sec 开始。合并音频时按 offset_sec 放置，若不补偿会把该段
        整体提前 (start_sec - int(start_sec)) 秒，导致分离结果与转写句级时间戳错位。
        因此在 wav 头部补等长静音，使「wav 位置 0 == 时间轴 int(start_sec)」。
        """
        if not self.cur_segment_samples:
            return None
        AUDIO_STORE_DIR.mkdir(parents=True, exist_ok=True)
        path = AUDIO_STORE_DIR / f"m{self.meeting_id}_seg{self.segment_no}_{int(start_sec)}.wav"
        try:
            import array
            pad_samples = int(round((start_sec - int(start_sec)) * SAMPLE_RATE))
            samples = array.array("h", [0] * max(pad_samples, 0))
            samples.extend(self.cur_segment_samples)
            with wave.open(str(path), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(SAMPLE_RATE)
                w.writeframes(samples.tobytes())
            return path
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[streaming] 段 wav 写入失败: {exc}")
            return None

    async def _refine_segment(self, record_id: int, start: float, end: float):
        """二遍精修：用 faster-whisper 对段音频整句重解码，替换初稿。"""
        if not record_id:
            return
        try:
            # 拿到 record 的 audio_path（同步取一次）
            async with get_db_context() as db:
                record = await db.get(AimeetingMinuteRecord, record_id)
                if not record or not record.audio_path or not Path(record.audio_path).exists():
                    return
                audio_path = record.audio_path
            async with _refine_sem:
                refined = await asyncio.to_thread(self._whisper_refine, audio_path)
            if not refined or not refined.strip():
                return
            async with get_db_context() as db:
                record = await db.get(AimeetingMinuteRecord, record_id)
                if not record:
                    return
                record.transcript = refined
                record.segments_json = json.dumps([{
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "text": refined,
                    "speaker": 0,
                }], ensure_ascii=False)
                await db.commit()
                # 精修结果替换会议 transcript 中的初稿片段（不依赖 merge 增量跳过）
                meeting = await db.get(AimeetingMeeting, self.meeting_id)
                if meeting:
                    await update_merged_segment(db, meeting, start, end, refined)
            try:
                await self.ws.send_json({
                    "type": "refined",
                    "text": refined,
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "record_id": record_id,
                })
            except Exception:  # noqa: BLE001
                # WS 已关闭（用户停止后等不到精修帧即断开）属正常情况：
                # 数据库已写入精修文本且 revision 自增，前端恢复后经全量刷新可见。
                logger.debug(f"[streaming] 精修帧推送跳过（连接已关）record={record_id}")
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[streaming] 精修失败 record={record_id}: {exc}")

    @staticmethod
    def _whisper_refine(audio_path: str) -> str:
        """线程池内执行 faster-whisper 精修（不占事件循环），返回精修文本。"""
        from src.plugins.builtin.aimeeting.services import _get_whisper_model

        model = _get_whisper_model()
        segments, _info = model.transcribe(
            audio_path,
            language="zh",
            beam_size=5,  # 精修用更大 beam，比流式 greedy 更准
            vad_filter=True,
        )
        parts = [s.text.strip() for s in segments if s.text.strip()]
        return "".join(parts)


# ── WebSocket 端点 ──────────────────────────────────────────────────────

@router.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket):
    """流式转写 WebSocket 端点。

    连接流程：
    1. 客户端连接，先发 JSON hello 帧（meeting_id + device_id + offset_sec）
    2. 服务端校验并绑定设备，回复 ready
    3. 之后音频二进制帧（PCM16 16k mono）持续发送
    4. 服务端回推 partial / final / refined 文本帧
    5. 客户端发 done 或断开 → 收尾
    """
    await websocket.accept()
    session: StreamingSession | None = None
    try:
        # 1. 等 hello
        hello = await websocket.receive_text()
        data = json.loads(hello)
        if data.get("type") != "hello":
            await websocket.send_json({"type": "error", "message": "首帧必须是 hello"})
            await websocket.close()
            return
        meeting_id = int(data.get("meeting_id", 0))
        device_id = str(data.get("device_id", "")).strip()
        offset_sec = float(data.get("offset_sec", 0) or 0)
        if meeting_id <= 0 or len(device_id) < 8:
            await websocket.send_json({"type": "error", "message": "参数不合法"})
            await websocket.close()
            return

        # 校验会议（多设备共享：不再做设备绑定，任意设备可同时推流）
        async with get_db_context() as db:
            meeting = await db.get(AimeetingMeeting, meeting_id)
            if not meeting or meeting.is_deleted:
                await websocket.send_json({"type": "error", "message": "会议不存在"})
                await websocket.close()
                return
            if meeting.status == "ended":
                await websocket.send_json({"type": "error", "message": "会议已结束"})
                await websocket.close()
                return

        session = StreamingSession(websocket, meeting_id, device_id, base_offset=offset_sec)
        await session.open()
        await websocket.send_json({"type": "ready", "sampling_rate": SAMPLE_RATE})

        # 2. 音频循环
        while True:
            msg = await websocket.receive()
            if msg["type"] == "websocket.disconnect":
                break
            if msg["type"] == "websocket.receive":
                payload = msg.get("text")
                if payload is not None:
                    # 文本帧：控制命令
                    try:
                        ctrl = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    if ctrl.get("type") == "done":
                        break
                else:
                    # 二进制帧：PCM 音频
                    raw = msg.get("bytes")
                    if raw:
                        await session.feed(raw)
    except WebSocketDisconnect:
        pass
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"[streaming] ws 异常 meeting={meeting_id if session else '?'}: {exc}")
        if session:
            try:
                await websocket.send_json({"type": "error", "message": str(exc)})
            except Exception:  # noqa: BLE001
                pass
    finally:
        if session:
            try:
                await session.close()
            except Exception:  # noqa: BLE001
                pass
            # 冲刷完成（最后一段已落库）后通知前端，前端据此再调 finishMeeting，
            # 避免「点结束时最后一句静默丢失」。连接可能已断，send 失败可忽略。
            try:
                await websocket.send_json({"type": "flushed"})
            except Exception:  # noqa: BLE001
                pass
        try:
            await websocket.close()
        except Exception:  # noqa: BLE001
            pass