from .capsule import VpCapsule
from .port import VpPort

class VpFork(VpCapsule):
    def __init__(self, name=None):
        super().__init__(name or "fork")
        self._in = self.add_input("in")
        self._in.set_chain_callback(self._on_data)
        self._src_ports = []

    def fork(self, name=None):
        index = len(self._src_ports)
        port_name = name or f"out{index}"
        port = self.add_output(port_name)
        self._src_ports.append(port)
        return port

    async def _on_data(self, _, data):
        for port in self._src_ports:
            await port.push(data)
