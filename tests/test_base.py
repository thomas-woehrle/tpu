from abc import ABC, abstractmethod

import cocotb
from cocotb.queue import Queue
from cocotb.triggers import RisingEdge


class TestBase[ParamsType, InputType, OutputType](ABC):
    # Potentially move to just a dut type, which also types the self.dut indirectly
    def __init__(self, dut, params: ParamsType, n_checks: int):
        self.dut = dut
        self.params = params
        self.n_checks = n_checks
        self.transaction_queue = Queue[tuple[InputType, OutputType]]()
        self.input_queue = Queue[InputType]()

    @abstractmethod
    def get_input_from_dut(self) -> InputType:
        pass

    @abstractmethod
    def get_output_from_dut(self) -> OutputType:
        pass

    @abstractmethod
    async def wait_in_monitor(self, curr_input: InputType):
        pass

    @abstractmethod
    async def score_transaction(self, t: tuple[InputType, OutputType]):
        pass

    @abstractmethod
    async def generate_input(self):
        pass

    @abstractmethod
    async def drive_input(self):
        pass

    async def monitor(self):
        await RisingEdge(self.dut.clk)
        while True:
            input = self.get_input_from_dut()

            await self.wait_in_monitor(input)

            output = self.get_output_from_dut()

            # put transaction in queue
            t = (input, output)
            await self.transaction_queue.put(t)

    async def score(self):
        while True:
            t = await self.transaction_queue.get()
            await self.score_transaction(t)

    def start_soon(self):
        cocotb.start_soon(self.drive_input())
        cocotb.start_soon(self.generate_input())
        cocotb.start_soon(self.score())
        cocotb.start_soon(self.monitor())
