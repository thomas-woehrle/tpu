import dataclasses

import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles

from utils import pack_matrix_to_int, unpack_int_to_matrix


@dataclasses.dataclass
class Input:
    reset: bool
    A: np.ndarray
    B: np.ndarray


@dataclasses.dataclass
class Output:
    C: np.ndarray


class Test:
    def __init__(self, dut):
        self.dut = dut
        self.transaction_queue = Queue[tuple[Input, Output]]()
        self.input_queue = Queue[Input]()

    def get_input_from_dut(self) -> Input:
        return Input(
            reset=bool(self.dut.reset.value),
            A=unpack_int_to_matrix(self.dut.A.value, (2, 2), 8),
            B=unpack_int_to_matrix(self.dut.B.value, (2, 2), 8)
        )

    def get_output_from_dut(self) -> Output:
        return Output(
            C=unpack_int_to_matrix(
                self.dut.mac_manager.flat_mac_accumulators.value, (2, 2), 32)
        )

    async def monitor(self):
        while True:
            await RisingEdge(self.dut.clk)
            input = self.get_input_from_dut()

            # wait long enough -> finetune later on
            if (input.reset):
                await FallingEdge(self.dut.clk)
            else:
                await ClockCycles(self.dut.clk, 6)
            output = self.get_output_from_dut()

            t = (input, output)
            await self.transaction_queue.put(t)

    async def score(self):
        while True:
            t = await self.transaction_queue.get()
            if t[0].reset:
                print("Asserting reset")
                assert np.all(t[1].C == 0)
            else:
                expected = t[0].A @ t[0].B
                actual = t[1].C

                print("expected:", expected, "actual:", actual)
                assert np.all(expected == actual), (
                    f"expected: {expected}, actual: {actual}")

    async def generate_input(self):
        for i in range(20):  # just producing 20 inputs -> should be finetuned
            d = Input(
                reset=True,
                A=np.random.randint(0, 255, (2, 2)),
                B=np.random.randint(0, 255, (2, 2))
            )
            await self.input_queue.put(d)
            d = Input(
                reset=False,
                A=np.random.randint(0, 255, (2, 2)),
                B=np.random.randint(0, 255, (2, 2))
            )
            await self.input_queue.put(d)

    async def drive_input(self):
        while True:
            await FallingEdge(self.dut.clk)
            d = await self.input_queue.get()
            self.dut.reset.value = int(d.reset)
            self.dut.A.value = pack_matrix_to_int(d.A, 8)
            self.dut.B.value = pack_matrix_to_int(d.B, 8)
            if (d.reset):
                await ClockCycles(self.dut.clk, 1)
            else:
                await ClockCycles(self.dut.clk, 6)


@cocotb.test
async def test_systolic_matrix_multiplier(dut):
    clock = Clock(dut.clk, 2, "sec")
    cocotb.start_soon(clock.start())

    # Synchronize clock
    await RisingEdge(dut.clk)

    test = Test(dut)
    cocotb.start_soon(test.monitor())
    cocotb.start_soon(test.score())
    cocotb.start_soon(test.generate_input())
    cocotb.start_soon(test.drive_input())

    # Operate
    await ClockCycles(dut.clk, 100)
