# core/scheduler.py — 所有 after() 計時器集中管理


class Scheduler:
    """
    包裝 tkinter after()，依名稱管理計時器 ID，
    避免同名計時器重複觸發（double-fire）。
    """

    def __init__(self, root):
        self._root = root
        self._after_ids: dict[str, str] = {}

    def schedule(self, name: str, ms: int, callback):
        """排程一個具名計時器；若同名已存在則先取消。"""
        self.cancel(name)
        self._after_ids[name] = self._root.after(ms, lambda: self._fire(name, callback))

    def cancel(self, name: str):
        """取消具名計時器（若存在）。"""
        aid = self._after_ids.pop(name, None)
        if aid:
            self._root.after_cancel(aid)

    def cancel_all(self):
        for name in list(self._after_ids):
            self.cancel(name)

    def _fire(self, name: str, callback):
        self._after_ids.pop(name, None)
        callback()
