from typing import Any

class VpBuffer:
    def __init__(self, data: Any, ts: float = None, meta: dict = None):
        self.data = data
        self.ts = ts
        self.meta = meta or {}

    def __repr__(self):
        dtype = type(self.data).__name__
        return f"<Buffer type={dtype}, ts={self.ts}, meta={self.meta}>"
