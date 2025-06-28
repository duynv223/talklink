__author__ = "DuyNV4 <duynv4@fpt.com>"

import asyncio
from enum import Enum
from .port import VpPort
from .vpobject import VpObject
from .bus import VpBus, VpBusMessage


class VpState(Enum):
    NULL = 0
    READY = 1
    PAUSED = 2
    RUNNING = 3


class VpStateTransition(Enum):
    NULL_TO_READY = (VpState.NULL, VpState.READY)
    READY_TO_PAUSED = (VpState.READY, VpState.PAUSED)
    PAUSED_TO_RUNNING = (VpState.PAUSED, VpState.RUNNING)
    RUNNING_TO_PAUSED = (VpState.RUNNING, VpState.PAUSED)
    PAUSED_TO_READY = (VpState.PAUSED, VpState.READY)
    READY_TO_NULL = (VpState.READY, VpState.NULL)

    @staticmethod
    def from_states(old, new):
        for transition in VpStateTransition:
            if transition.value == (old, new):
                return transition
        return None
    
    def to_states(self):
        return self.value


class VpCapsule(VpObject):
    def __init__(self, name=None):
        super().__init__(name)
        self._input_ports = {}
        self._output_ports = {}
        self._state = VpState.NULL
        self._bus = None

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        if not isinstance(value, VpState):
            raise ValueError("Invalid state. Must be a VpState enum.")
        old_state = self._state
        self._state = value
        self.emit_signal("state_changed", old_state=old_state, new_state=value)
        self.post_message(VpBusMessage(
            msg_type="state_changed",
            payload={"old_state": old_state.name, "new_state": value.name},
            source=self,
            timestamp=asyncio.get_event_loop().time()
        ))
    
    @property
    def bus(self):
        return self._bus

    @bus.setter
    def bus(self, value):
        if not isinstance(value, VpBus):
            raise ValueError("Bus must be a VpBus")
        self._bus = value

    def post_message(self, message):
        if self._bus:
            asyncio.create_task(self._bus.post(message))

    def add_input(self, name):
        port = VpPort(name)
        port.set_chain_callback(self._handle_input)
        self._input_ports[name] = port
        return port

    def add_output(self, name):
        port = VpPort(name)
        self._output_ports[name] = port
        return port

    def get_input(self, name):
        return self._input_ports[name]

    def get_output(self, name):
        return self._output_ports[name]

    async def _handle_input(self, name, data):
        raise NotImplementedError

    async def run(self):
        pass

    def __rshift__(self, other):
        if isinstance(other, VpPort):
            self.get_output("out").link(other)
        else:
            self.get_output("out").link(other.get_input("in"))
        return other

    async def set_state(self, new_state):
        state_order = [
            VpState.NULL,
            VpState.READY,
            VpState.PAUSED,
            VpState.RUNNING,
        ]

        try:
            current_index = state_order.index(self.state)
            target_index = state_order.index(new_state)
        except ValueError:
            print(f"[{self.name}] Invalid state: {self.state} or {new_state}.")
            return False
        
        step = 1 if target_index > current_index else -1
        for intermediate_state_index in range(current_index + step, target_index + step, step):
            intermediate_state = state_order[intermediate_state_index]
            transition = VpStateTransition.from_states(self.state, intermediate_state)
            if not transition:
                print(f"[{self.name}] Invalid state transition from {self.state.name} to {intermediate_state.name}.")
                return False
            if not await self.change_state(transition):
                return False
        return True

    async def change_state(self, transition):
        if not isinstance(transition, VpStateTransition):
            raise ValueError("Invalid transition. Must be an VpStateTransition enum.")

        old_state, new_state = transition.value

        if self.state != old_state:
            print(f"[{self.name}] Current state {self.state.name} does not match transition's old state {old_state.name}.")
            return False

        if self.state == new_state:
            print(f"[{self.name}] Already in state {new_state.name}.")
            return True

        match transition:
            case VpStateTransition.NULL_TO_READY:
                self.state = new_state
                return True
            case VpStateTransition.READY_TO_PAUSED:
                await self._activate_ports(True)
                self.state = new_state
                return True
            case VpStateTransition.PAUSED_TO_RUNNING:
                self.state = new_state
                return True
            case VpStateTransition.RUNNING_TO_PAUSED:
                self.state = new_state
                return True
            case VpStateTransition.PAUSED_TO_READY | VpStateTransition.READY_TO_NULL:
                await self._activate_ports(False)
                self.state = new_state
                return True
            case _:
                print(f"[{self.name}] Unsupported transition: {transition.name}.")
                return False

    async def _activate_ports(self, activate):
        for port in self._input_ports.values():
            await port.activate(activate)
        for port in self._output_ports.values():
            await port.activate(activate)
