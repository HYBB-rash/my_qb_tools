# tg_logging.py
import logging
import queue
import threading
import time
from typing import Iterable

import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
SENTINEL = object()


class TelegramHandler(logging.Handler):
    """把日志发到 Telegram。内部用队列+后台线程，避免阻塞主流程。
    支持优雅退出：close()/logging.shutdown() 时会阻塞直至把队列里的消息发完。
    """

    def __init__(
        self,
        token: str,
        chat_id: str,
        level: int = logging.INFO,
        *,
        max_queue: int = 200,
        chunk_chars: int = 3900,  # TG 单条消息上限 4096，留点余量
        timeout_sec: float = 4.0,  # 单次请求超时
        rate_limit_sec: float = 0.1,  # 轻微限速，防止触发 TG 限流
        drop_oldest_on_full: bool = True,
    ):
        super().__init__(level)
        self.token = token
        self.chat_id = chat_id
        self.chunk_chars = chunk_chars
        self.timeout_sec = timeout_sec
        self.rate_limit_sec = rate_limit_sec
        self.drop_oldest_on_full = drop_oldest_on_full

        self._q: "queue.Queue[object]" = queue.Queue(max_queue)
        self._stop = threading.Event()
        self._worker = threading.Thread(
            target=self._run, daemon=True, name="TelegramHandlerWorker"
        )
        self._session = requests.Session()
        self._worker.start()

    # ---------- logging.Handler 接口 ----------

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)  # 用外部设置的 Formatter
            for chunk in self._chunk(msg, self.chunk_chars):
                self._enqueue(chunk)
        except Exception:
            # 不要在这里 logging，避免递归；交给父类做标准错误处理
            self.handleError(record)

    def flush(self) -> None:  # type: ignore[override]
        """阻塞直到队列中的消息全部发送完成。"""
        try:
            self._q.join()
        except Exception:
            pass

    def close(self) -> None:  # type: ignore[override]
        try:
            # 先把当前队列里的消息全部发送
            self.flush()
        finally:
            # 投递哨兵让工作线程优雅退出；同时设停止标志
            try:
                self._q.put_nowait(SENTINEL)
            except Exception:
                pass
            self._stop.set()
            if self._worker.is_alive():
                # 等一会，防止网络抖动导致收尾太慢（可按需调小/调大）
                self._worker.join(timeout=5)
        super().close()

    # ---------- 内部实现 ----------

    def _enqueue(self, item: object) -> None:
        try:
            self._q.put_nowait(item)
        except queue.Full:
            if self.drop_oldest_on_full:
                # 丢弃最旧的一条，确保 put 不阻塞；注意要配对 task_done 以免 join() 卡住
                try:
                    _ = self._q.get_nowait()
                    self._q.task_done()
                except queue.Empty:
                    pass
                try:
                    self._q.put_nowait(item)
                except queue.Full:
                    # 如果还满，干脆丢弃本条
                    pass
            else:
                # 直接丢弃本条
                pass

    def _run(self):
        url = TELEGRAM_API.format(token=self.token)
        while True:
            try:
                item = self._q.get(timeout=0.5)
            except queue.Empty:
                # 若已请求停止且队列为空，允许线程退出
                if self._stop.is_set():
                    break
                continue

            if item is SENTINEL:
                self._q.task_done()
                break

            text = str(item)
            try:
                self._session.post(
                    url,
                    data={"chat_id": self.chat_id, "text": text},
                    timeout=self.timeout_sec,
                )
                if self.rate_limit_sec > 0:
                    time.sleep(self.rate_limit_sec)
            finally:
                self._q.task_done()

    @staticmethod
    def _chunk(s: str, n: int) -> Iterable[str]:
        if len(s) <= n:
            return [s]
        return (s[i : i + n] for i in range(0, len(s), n))
