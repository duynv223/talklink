import asyncio
from vpipe.core.capsule import VpCapsule
from vpipe.core.bus import VpBus

class VpComposite(VpCapsule):
    def __init__(self, name=None):
        super().__init__(name)
        self._capsules = []
        self._input_ports = {}
        self._output_ports = {}
        self._sbus = VpBus(self.name + "-sbus" if name else None)
        self._sbus.add_watch(self._sbus_message_handler)

    def add(self, capsule):
        self._capsules.append(capsule)
        capsule.bus = self._sbus

    def adds(self, *capsules):
        for capsule in capsules:
            self.add(capsule)
    
    def get_capsule(self, name):
        for capsule in self._capsules:
            if capsule.name == name:
                return capsule
        return None

    def remove(self, capsule):
        if capsule in self._capsules:
            self._capsules.remove(capsule)
    
    async def change_state(self, transition):
        current_state, next_state = transition.to_states()
        for capsule in self._capsules:
            if not await capsule.set_state(next_state):
                return False
        return await super().change_state(transition)

    def expose_input(self, name, internal_port):
        self._input_ports[name] = internal_port

    def expose_output(self, name, internal_port):
        self._output_ports[name] = internal_port

    async def _sbus_message_handler(self, message):
        self.post_message(message)

    async def _activate_ports(self, activate):
        # Ignore activation for composite capsules
        pass