from abc import ABC, abstractmethod

import cocotb
from cocotb.queue import Queue
from cocotb.triggers import FallingEdge, RisingEdge


class TestBase[ParamsType, DutSnapshotType, InputType](ABC):
    # Potentially move to just a dut type, which also types the self.dut indirectly
    def __init__(self, dut, params: ParamsType, n_checks: int):
        self.dut = dut
        self.params = params
        self.n_checks = n_checks
        self.transaction_queue = Queue[tuple[DutSnapshotType, DutSnapshotType]](
        )
        self.input_queue = Queue[InputType]()

    @abstractmethod
    def get_dut_snapshot(self) -> DutSnapshotType:
        pass

    @abstractmethod
    async def wait_between_snapshots(self, first_snapshot: DutSnapshotType):
        pass

    @abstractmethod
    async def score_transaction(self, t: tuple[DutSnapshotType, DutSnapshotType]):
        pass

    @abstractmethod
    async def generate_input(self, i: int) -> InputType:
        # could get counter or sim time as argument
        pass

    @abstractmethod
    async def drive_input(self, next_input: InputType):
        """After this coroutine finishes, it gets called again at the next FallingEdge"""
        pass

    async def start_monitor(self):
        await RisingEdge(self.dut.clk)
        while True:
            snapshot_0 = self.get_dut_snapshot()

            await self.wait_between_snapshots(snapshot_0)

            snapshot_1 = self.get_dut_snapshot()

            # put transaction in queue
            t = (snapshot_0, snapshot_1)
            await self.transaction_queue.put(t)

    async def start_scoreboard(self):
        while True:
            t = await self.transaction_queue.get()
            await self.score_transaction(t)

    async def start_input_generator(self):
        for i in range(self.n_checks):
            next_input = await self.generate_input(i)
            await self.input_queue.put(next_input)

    async def start_input_driver(self):
        while True:
            await FallingEdge(self.dut.clk)
            next_input = await self.input_queue.get()
            await self.drive_input(next_input)

    def start_soon(self):
        cocotb.start_soon(self.start_input_generator())
        cocotb.start_soon(self.start_input_driver())
        cocotb.start_soon(self.start_scoreboard())
        cocotb.start_soon(self.start_monitor())
