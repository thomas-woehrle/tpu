import dataclasses
import random

import cocotb
from cocotb.clock import Clock
from cocotb.handle import BinaryValue
from cocotb.queue import Queue
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles


@dataclasses.dataclass
class Snapshot:
    ena: BinaryValue
    reset: BinaryValue
    a: BinaryValue
    b: BinaryValue
    c: BinaryValue


@dataclasses.dataclass
class Input:
    ena: bool
    reset: bool
    a: int
    b: int


class Test:
    def __init__(self, dut):
        self.dut = dut
        self.transaction_queue = Queue[tuple[Snapshot, Snapshot]]()
        self.input_queue = Queue[Input]()

    def get_snapshot_from_dut(self) -> Snapshot:
        return Snapshot(
            ena=self.dut.ena.value,
            reset=self.dut.reset.value,
            a=self.dut.a.value,
            b=self.dut.b.value,
            c=self.dut.c.value
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
                assert t[1].c == 0
            elif not t[0].ena:
                assert t[1].c == t[0].c
            else:
                expected = t[0].a * t[0].b + t[0].c
                actual = t[1].c

                print("expected:", expected, "actual:", actual)
                assert expected == actual, (
                    f"expected: {expected}, actual: {actual}")

    async def generate_input(self, num_accumulations: int):
        counter = 0
        while True:
            d = Input(
                ena=random.random() < 0.9,  # 90%
                reset=counter % (num_accumulations + 1) == 0,
                a=random.randint(0, 255),
                b=random.randint(0, 255)
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
            self.dut.a.value = d.a
            self.dut.b.value = d.b


@cocotb.test
async def test_mac_basic(dut):
    clock = Clock(dut.clk, 10, "ns")
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
