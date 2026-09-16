"""AI 会议助手插件——WebSocket 流式 ASR 端点。

P3 方案：sherpa-onnx streaming zipformer（实时初稿）→ faster-whisper 二遍精修。

协议（前端 AudioWorklet → 本端点）：
- 建立连接后，客户端先发一条 JSON 文本帧：
    {"type": "hello", "meeting_id": 123, "device_id": "xxxx"}
  服务端校验会议存在 + 单录制方守卫，返回
    {"type": "ready", "sampling_rate": 16000, "base_offset": 125.0}
  （base_offset 为服务端计算的会议时间轴续录起点，接管/重连场景非 0）
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

单录制方（2026-09-11 产品决策：多设备同时录音为伪需求）：
- 同一会议同一时刻只允许一路音频流写入共享时间轴；其他设备只读观看。
- 录制权以「进程内活跃会话注册表」为准（_active_streams）：设备推流即占用，
  断流超过 STREAM_STALE_SEC（心跳判定）自动释放，他设备可接管续录。
- base_offset 不再信任客户端传值，由服务端按已有 records 计算续录起点
  （修复 B1：录制方刷新/断线重连后从 0 铺起导致时间轴重叠）。
"""
import asyncio
import json
import math
import struct
import time
import uuid
import wave
from pathlib import Path

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from sqlalchemy import func, select

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

# ── 单录制方：活跃推流会话注册表 ─────────────────────────────────────────
# meeting_id -> {"device_id": str, "last_active": float(墙钟), "end_sec": float}
# end_sec = 该会话已写入时间轴的最大绝对偏移（秒），用于他设备接管时续录起点。
# 进程内字典即可：后端为单进程 uvicorn；且仅作为「是否有人在录」的实时判据，
# 持久化的录音归属仍写 meeting.recorder_device_id（重启后若无人推流则可重新认领）。
_active_streams: dict[int, dict] = {}

# 心跳判死阈值（秒）：超过该时长未收到任何音频帧/控制帧即视为掉线，可被接管。
# 浏览器 AudioWorklet 帧间隔 <1s，留足弱网抖动余量。
STREAM_STALE_SEC = 10.0


def _active_stream(meeting_id: int) -> dict | None:
    """返回会议的活跃推流信息；已掉线（超阈值）则清理并返回 None。"""
    info = _active_streams.get(meeting_id)
    if not info:
        return None
    if time.time() - info["last_active"] > STREAM_STALE_SEC:
        _active_streams.pop(meeting_id, None)
        return None
    return info


def stream_recording_state(meeting_id: int) -> tuple[bool, str]:
    """供 HTTP 层查询：(是否有设备正在推流, 推流设备ID)。"""
    info = _active_stream(meeting_id)
    if info:
        return True, info["device_id"]
    return False, ""


def active_stream_snapshot() -> dict[int, dict]:
    """所有未失效推流会话快照（供管理端数据面板列出实时录制中的会议）。

    返回 {meeting_id: {"device_id": str, "end_sec": float, "idle_sec": float}}。
    """
    out: dict[int, dict] = {}
    now = time.time()
    for mid in list(_active_streams.keys()):
        info = _active_stream(mid)
        if info:
            out[mid] = {
                "device_id": info["device_id"],
                "end_sec": info.get("end_sec", 0),
                "idle_sec": round(now - info["last_active"], 1),
            }
    return out


async def compute_meeting_offset(db, meeting_id: int, active_end: float | None = None) -> float:
    """服务端计算会议时间轴续录起点（秒）。

    B1 修复：不再信任客户端上报的 offset。取两类来源的最大值：
    - records 表已有片段的时间轴末端 max(offset_sec + audio_duration)
    - 当前活跃推流会话（若有接管场景）的实时末端 active_end
    - meeting.audio_duration（流式/切片链路持续回写）
    """
    stmt = select(
        func.max(AimeetingMinuteRecord.offset_sec + AimeetingMinuteRecord.audio_duration)
    ).where(
        AimeetingMinuteRecord.meeting_id == meeting_id,
        AimeetingMinuteRecord.is_deleted == False,  # noqa: E712
    )
    row = (await db.execute(stmt)).scalar()
    offset = float(row or 0)
    if active_end and active_end > offset:
        offset = float(active_end)
    return offset

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
# 精修积压治理：待处理精修任务数超限则跳过新段（保实时链路，牺牲慢速设备的精修率）。
# 场景：低端设备 CPU 上 whisper beam=5 精修比出段速度慢，无界 _spawn_bg 会让
# final→refined 延迟从秒级漂移到分钟级，用户结束会议时大量段仍未精修。
_REFINE_MAX_PENDING = 3
_refine_pending = 0

# ── 静音/噪声门（反幻听）─────────────────────────────────────────────
# sherpa-onnx zipformer 对底噪敏感：安静房间里的环境噪声（实测帧 RMS 峰值 <600，
# int16 满量程 32767）会被它"幻听"出「老/爷爷/人」等单字（会议 55 复现）。
# 对策：帧能量门控——低能帧不进识别器也不进段缓存（等价于"人没说话不喂音频"），
# 语音帧带 1.5s hangover 尾巴（保留轻声句尾）；段定稿时有效语音太短直接丢弃。
# 阈值标定（100ms 帧 RMS）：真实说话 P50≈320 / P95≈2200；安静噪声 max<600。
_VOICE_RMS = 400        # 帧 RMS 高于此视为语音帧
_HANGOVER_FRAMES = 15   # 语音结束后继续放行的拖尾帧数（帧=100ms → 1.5s）
_MIN_SPEECH_SEC = 0.6   # 段内有效语音不足 0.6s 视为噪声幻听，整段丢弃


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
        self.base_offset = base_offset  # 会话起始的会议内偏移（秒，服务端计算）
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
        # 会话唯一标识：段 wav 文件名后缀，避免重连后 segment_no 重复导致同名覆盖（B2）
        self._uid = uuid.uuid4().hex[:8]
        # ── 噪声门状态（见 _VOICE_RMS 注释）──
        self._gate_open = False   # 当前帧是否放行（语音中或 hangover 拖尾内）
        self._hangover = 0        # 语音结束后剩余拖尾帧数
        self._seg_speech_sec = 0.0  # 当前段累计有效语音秒数（定稿时判噪声段）
        self._last_partial = ""   # 上次推送的 partial 文本（去重防刷屏）

    # ── 录制方注册（单录制方守卫的进程内实时判据）────────────────────
    def register(self) -> None:
        """登记为会议的活跃推流方（占用录音权）。"""
        _active_streams[self.meeting_id] = {
            "device_id": self.device_id,
            "last_active": time.time(),
            "end_sec": self.base_offset,
        }

    def heartbeat(self) -> None:
        """刷新活跃时间戳（收到任何音频/控制帧时调用）。"""
        info = _active_streams.get(self.meeting_id)
        if info and info["device_id"] == self.device_id:
            info["last_active"] = time.time()

    def unregister(self) -> None:
        """注销活跃登记（done/断线时调用），释放录音权供他设备接管。"""
        info = _active_streams.get(self.meeting_id)
        if info and info["device_id"] == self.device_id:
            _active_streams.pop(self.meeting_id, None)

    def _sync_stream_end(self) -> None:
        """把会话时间轴当前位置同步到注册表（接管时续录起点依据）。"""
        info = _active_streams.get(self.meeting_id)
        if info and info["device_id"] == self.device_id:
            info["end_sec"] = max(info["end_sec"], self.base_offset + self._elapsed_sec)
            info["last_active"] = time.time()

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
            if tail_text and self._seg_speech_sec >= _MIN_SPEECH_SEC:
                await self._finalize_segment(tail_text)
            elif tail_text:
                logger.debug(
                    f"[streaming] 收尾噪声段丢弃 meeting={self.meeting_id} "
                    f"speech={self._seg_speech_sec:.2f}s text={tail_text[:10]!r}"
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[streaming] close 冲刷失败 meeting={self.meeting_id}: {exc}")

    # ── 主循环：接收音频 ─────────────────────────────────────────────
    async def feed(self, samples: bytes):
        """处理一帧 PCM16 音频（来自 WebSocket 二进制帧），带噪声门控。

        门控策略（反幻听，见 _VOICE_RMS 注释）：按 100ms 帧算 RMS，只把
        「语音帧 + 1.5s hangover + 段内静音期补零」喂给 zipformer——噪声
        进不了初稿识别器（会议 55 实测底噪幻听「老/爷爷/人」的根因）；
        补零让 endpoint 尾部静音计时正常推进（否则说完话永远不触发定稿）。
        段缓存（wav）仍存**全量帧**：二遍精修交给 whisper vad_filter 处理，
        声纹分离也需要连续时间轴，切帧喂 ASR 只影响初稿质量（draft 可缺
        轻声字，refined 用全量音频修正）。
        段定稿时有效语音（真正超阈值的帧）不足 _MIN_SPEECH_SEC → 判为噪声
        幻听段，整段丢弃不落库。
        """
        if self.stream is None or self.closed:
            return
        if len(samples) < 2:
            return
        arr = np.frombuffer(samples, dtype=np.int16)
        if arr.size == 0:
            return
        arr_f = arr.astype(np.float32)

        self._elapsed_sec += arr.size / SAMPLE_RATE
        # 心跳 + 时间轴末端同步（单录制方判据 / 接管续录起点）
        self._sync_stream_end()
        # 段缓存收全量音频（精修 wav / 分离合并用）
        self.cur_segment_samples.extend(arr.tolist())

        FRAME = 1600  # 100ms
        voiced: list[int] = []
        filler_zeros = 0  # 门关闭时补喂的零采样（维持 endpoint 计时）
        n_full = arr_f.size // FRAME
        blocks = (
            [arr_f[i * FRAME:(i + 1) * FRAME] for i in range(n_full)]
            + ([arr_f[n_full * FRAME:]] if n_full * FRAME < arr_f.size else [])
        )
        for blk in blocks:
            rms = float(np.sqrt(np.mean(blk * blk)))
            if rms >= _VOICE_RMS:
                self._hangover = _HANGOVER_FRAMES
                self._gate_open = True
                self._seg_speech_sec += blk.size / SAMPLE_RATE
            elif self._hangover > 0:
                self._hangover -= 1
            else:
                self._gate_open = False
            if self._gate_open:
                voiced.extend(blk.astype(np.int16).tolist())
            elif self._seg_speech_sec > 0:
                # 段内已有语音 → 静音帧补零，让 endpoint 的 trailing silence 计时推进
                filler_zeros += blk.size

        if voiced:
            self.stream.accept_waveform(SAMPLE_RATE, voiced)
        if filler_zeros:
            self.stream.accept_waveform(SAMPLE_RATE, [0] * filler_zeros)

        # 解码到就绪
        while self.recognizer.is_ready(self.stream):
            self.recognizer.decode_stream(self.stream)

        result = self.recognizer.get_result(self.stream).strip()
        if result and result != self._last_partial:
            self._last_partial = result
            await self.ws.send_json({
                "type": "partial",
                "text": result,
                "segment": self.segment_no,
            })

        # endpoint 检测：一句话说完了，定稿
        if self.recognizer.is_endpoint(self.stream):
            final_text = self.recognizer.get_result(self.stream).strip()
            if final_text and self._seg_speech_sec >= _MIN_SPEECH_SEC:
                await self._finalize_segment(final_text)
            elif final_text:
                # 有效语音太短（咔哒声/短噪声诱发的幻听字）→ 整段丢弃不落库
                logger.debug(
                    f"[streaming] 噪声段丢弃 meeting={self.meeting_id} seg={self.segment_no} "
                    f"speech={self._seg_speech_sec:.2f}s text={final_text[:10]!r}"
                )
            self.recognizer.reset(self.stream)
            self.segment_no += 1
            self.cur_segment_start = self.base_offset + self._elapsed_sec
            self.cur_segment_samples = []
            self._seg_speech_sec = 0.0
            self._gate_open = False
            self._hangover = 0
            self._last_partial = ""

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
            # 维护会议级时间轴游标：audio_duration 始终为「时间轴已写到的末端秒数」。
            # 既是 B1 续录起点计算的兜底依据，也供前端/接管设备展示进度。
            new_end = max(math.ceil(end), meeting.audio_duration or 0)
            meeting.audio_duration = new_end
            # 录制权归属兜底认领（正常在 ws hello 已认领；防历史数据/异常路径为空）
            if not meeting.recorder_device_id:
                meeting.recorder_device_id = self.device_id
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
        # 文件名带会话 uid：重连后 segment_no 重新从 0 计数，仅靠 no+start 在
        # 同秒接管场景仍可能同名覆盖（B2），uid 保证每会话唯一。
        path = AUDIO_STORE_DIR / f"m{self.meeting_id}_seg{self.segment_no}_{int(start_sec)}_{self._uid}.wav"
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
        """二遍精修：用 faster-whisper 对段音频整句重解码，替换初稿。

        积压保护：待处理精修超过 _REFINE_MAX_PENDING 时跳过本段（保留初稿），
        防止慢速设备上精修无限排队、final→refined 延迟无界增长。
        """
        global _refine_pending
        if not record_id:
            return
        if _refine_pending >= _REFINE_MAX_PENDING:
            logger.warning(
                f"[streaming] 精修积压 {_refine_pending} 段超限，跳过 record={record_id}（保留初稿）"
            )
            return
        _refine_pending += 1
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
        finally:
            _refine_pending -= 1

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
    1. 客户端连接，先发 JSON hello 帧（meeting_id + device_id）
    2. 服务端校验会议 + **单录制方守卫**（他设备正在推流则拒绝），
       按已有 records 计算续录起点，回复 ready（含 base_offset）
    3. 之后音频二进制帧（PCM16 16k mono）持续发送（兼作心跳）
    4. 服务端回推 partial / final / refined 文本帧
    5. 客户端发 done 或断开 → 收尾并释放录音权
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
        if meeting_id <= 0 or len(device_id) < 8:
            await websocket.send_json({"type": "error", "message": "参数不合法"})
            await websocket.close()
            return

        # 单录制方守卫：他设备正在推流（心跳未超时）→ 拒绝，本机应转为只读观看。
        # 同设备重连（刷新/断网恢复）放行——续录由服务端计算 base_offset 接上。
        holder = _active_stream(meeting_id)
        if holder and holder["device_id"] != device_id:
            await websocket.send_json({
                "type": "error",
                "code": "recording_by_other",
                "message": "另一台设备正在录音，本页已切换为观看模式",
            })
            await websocket.close()
            return

        # 校验会议 + 服务端计算续录起点（B1：不信任客户端 offset_sec 传值）
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
            base_offset = await compute_meeting_offset(db, meeting_id)
            # 认领录音权（录制方归属：空则认领；同设备重连天然一致）
            if meeting.recorder_device_id != device_id:
                meeting.recorder_device_id = device_id
                await db.commit()

        session = StreamingSession(websocket, meeting_id, device_id, base_offset=base_offset)
        session.register()
        await session.open()
        # ready 回传服务端时间轴起点：前端据此校准本机偏移显示（不再自行硬编码）
        await websocket.send_json({
            "type": "ready",
            "sampling_rate": SAMPLE_RATE,
            "base_offset": round(base_offset, 2),
        })

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
                    # 其他文本帧也刷新心跳（如前端 ping）
                    session.heartbeat()
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
            # 先释放录音权（他设备可立即接管），再冲刷收尾
            session.unregister()
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