import dataclasses
import random

import cocotb
from cocotb.clock import Clock
from cocotb.handle import BinaryValue
from cocotb.queue import Queue
from cocotb.runner import get_runner
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles


@dataclasses.dataclass
class Snapshot:
    ena: BinaryValue
    reset: BinaryValue
    A: BinaryValue
    B: BinaryValue
    C: BinaryValue


@dataclasses.dataclass
class Input:
    ena: bool
    reset: bool
    A: int
    B: int


class Test:
    def __init__(self, dut):
        self.dut = dut
        self.transaction_queue = Queue[tuple[Snapshot, Snapshot]]()
        self.input_queue = Queue[Input]()

    def get_snapshot_from_dut(self) -> Snapshot:
        return Snapshot(
            ena=self.dut.ena.value,
            reset=self.dut.reset.value,
            A=self.dut.A.value,
            B=self.dut.B.value,
            C=self.dut.C.value
        )

    async def monitor(self):
        while True:
            await RisingEdge(self.dut.clk)
            before_snapshot = self.get_snapshot_from_dut()

            await FallingEdge(self.dut.clk)
            after_snapshot = self.get_snapshot_from_dut()

            t = (before_snapshot, after_snapshot)
            await self.transaction_queue.put(t)

    async def score(self):
        while True:
            t = await self.transaction_queue.get()
            if t[0].reset:
                assert t[1].C == 0
            elif not t[0].ena:
                assert t[1].C == t[0].C
            else:
                expected = t[0].A * t[0].B + t[0].C
                actual = t[1].C

                print("expected:", expected, "actual:", actual)
                assert expected == actual, (
                    f"expected: {expected}, actual: {actual}")

    async def generate_input(self, num_accumulations: int):
        counter = 0
        while True:
            d = Input(
                ena=random.random() < 0.9,  # 90%
                reset=counter % (num_accumulations + 1) == 0,
                A=random.randint(0, 255),
                B=random.randint(0, 255)
            )
            await self.input_queue.put(d)
            await FallingEdge(self.dut.clk)
            counter += 1

    async def drive_input(self):
        while True:
            await FallingEdge(self.dut.clk)
            d = await self.input_queue.get()
            self.dut.reset.value = int(d.reset)
            self.dut.ena.value = int(d.ena)
            self.dut.A.value = d.A
            self.dut.B.value = d.B


@cocotb.test
async def test_mac_basic(dut):
    clock = Clock(dut.clk, 2, "sec")
    cocotb.start_soon(clock.start())

    # synchronize Clk
    await RisingEdge(dut.clk)

    # Start Monitor, Scoreboard, Input Generator and Input Driver
    # Input Generator should generate reset as first input
    test = Test(dut)
    cocotb.start_soon(test.monitor())
    cocotb.start_soon(test.score())
    cocotb.start_soon(test.generate_input(4))
    cocotb.start_soon(test.drive_input())

    # Operate
    await ClockCycles(dut.clk, 100)


def main():
    simulator = get_runner("icarus")
    simulator.build(
        sources=["../Mac.v"],
        hdl_toplevel="Mac",
        clean=True,
        waves=True
    )
    simulator.test(
        hdl_toplevel="Mac",
        test_module="Mac_tb",
        waves=True
    )


if __name__ == "__main__":
    main()
