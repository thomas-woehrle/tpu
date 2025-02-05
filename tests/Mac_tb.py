import dataclasses
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

from test_base import TestBase
from utils import get_params_from_env


@dataclasses.dataclass
class Parameters:
    OP_WIDTH: int = 8
    ACC_WIDTH: int = 32


@dataclasses.dataclass
class DutSnapshot:
    ena: bool
    reset: bool
    a: int
    b: int
    c: int


@dataclasses.dataclass
class Input:
    ena: bool
    reset: bool
    a: int
    b: int


class RefactoredTest(TestBase[Parameters, DutSnapshot, Input]):
    def __init__(self, dut, params: Parameters, n_checks: int, n_accumulations: int):
        self.n_accumulations = n_accumulations
        super().__init__(dut, params, n_checks)

    def get_dut_snapshot(self) -> DutSnapshot:
        return DutSnapshot(
            ena=self.dut.ena.value,
            reset=self.dut.reset.value,
            a=self.dut.a.value,
            b=self.dut.b.value,
            c=self.dut.c.value
        )

    async def wait_between_snapshots(self, first_snapshot: DutSnapshot):
        await RisingEdge(self.dut.clk)

    async def score_transaction(self, t: tuple[DutSnapshot, DutSnapshot]):
        if t[0].reset:
            assert t[1].c == 0
        elif not t[0].ena:
            assert t[1].c == t[0].c
        else:
            expected = t[0].a * t[0].b + t[0].c
            actual = t[1].c

            print("expected:", expected, "actual:", int(actual))
            assert expected == actual, (
                f"expected: {expected}, actual: {int(actual)}")

    async def generate_input(self, i: int) -> Input:
        max_value = 2 ** self.params.OP_WIDTH - 1  # inclusive
        return Input(
            ena=random.random() < 0.9,  # 90%
            reset=i % (self.n_accumulations + 1) == 0,
            a=random.randint(0, max_value),
            b=random.randint(0, max_value),
        )

    async def drive_input(self, next_input: Input):
        self.dut.reset.value = int(next_input.reset)
        self.dut.ena.value = int(next_input.ena)
        self.dut.a.value = next_input.a
        self.dut.b.value = next_input.b


@cocotb.test
async def test_mac_basic(dut):
    clock = Clock(dut.clk, 10, "ns")
    cocotb.start_soon(clock.start())

    # synchronize Clk
    await RisingEdge(dut.clk)

    n_checks = 100
    params = get_params_from_env(Parameters)
    test = RefactoredTest(dut, params, n_checks, 8)
    test.start_soon()

    # Operate
    await ClockCycles(dut.clk, 100)
