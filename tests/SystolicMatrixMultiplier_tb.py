import dataclasses
import os

import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

from test_base import TestBase
from utils import pack_matrix_to_int, unpack_binary_value_to_matrix

# 3 states per N are managed in the matrix multiplier
STATES_PER_N = 3


@dataclasses.dataclass
class Parameters:
    N: int = 2
    OP_WIDTH: int = 8
    ACC_WIDTH: int = 32


@dataclasses.dataclass
class Input:
    reset: bool
    a: np.ndarray
    b: np.ndarray


@dataclasses.dataclass
class DutSnapshot:
    reset: bool
    a: np.ndarray | None
    b: np.ndarray | None
    c: np.ndarray | None


def get_params_from_env() -> Parameters:
    params = Parameters()

    for k, v in os.environ.items():
        if k.startswith("DUT_"):
            setattr(params, k[4:], int(v))

    return params


class SystolicMatrixMultiplierTest(TestBase[Parameters, DutSnapshot, Input]):
    def __init__(self, dut, params, n_checks):
        super().__init__(dut, params, n_checks)

    def get_dut_snapshot(self) -> DutSnapshot:
        return DutSnapshot(
            reset=bool(self.dut.reset.value),
            a=unpack_binary_value_to_matrix(
                self.dut.a.value, (self.params.N, self.params.N), self.params.OP_WIDTH),
            b=unpack_binary_value_to_matrix(
                self.dut.b.value, (self.params.N, self.params.N), self.params.OP_WIDTH),
            c=unpack_binary_value_to_matrix(
                self.dut.mac_manager.flat_mac_accumulators.value,
                (self.params.N, self.params.N),
                self.params.ACC_WIDTH
            )
        )

    async def wait_between_snapshots(self, first_snapshot: DutSnapshot):
        if first_snapshot.reset:
            await ClockCycles(self.dut.clk, 1)
        else:
            await ClockCycles(self.dut.clk, STATES_PER_N * self.params.N)

    async def score_transaction(self, t: tuple[DutSnapshot, DutSnapshot]):
        if t[0].reset:
            cocotb.log.info("Asserting reset")
            assert np.all(t[1].c == 0)
        elif t[0].a is None or t[0].b is None:
            assert False, "a or b are None"
        else:
            expected = t[0].a @ t[0].b
            actual = t[1].c

            assert np.all(expected == actual), (
                f"""
                Calculating: \n
                {t[0].a} \n\n
                @ \n\n
                {t[0].b} \n\n

                Expected: \n
                {expected} \n
                Actual: \n
                {actual}
            """)

    async def generate_input(self, i: int) -> Input:
        # val_max is exclusive
        val_max = 2 ** self.params.OP_WIDTH
        if i % 2 == 0:
            return Input(
                reset=True,
                a=np.random.randint(
                    0, val_max, (self.params.N, self.params.N)),
                b=np.random.randint(0, val_max, (self.params.N, self.params.N))
            )
        else:
            return Input(
                reset=False,
                a=np.random.randint(
                    0, val_max, (self.params.N, self.params.N)),
                b=np.random.randint(0, val_max, (self.params.N, self.params.N))
            )

    async def drive_input(self, next_input: Input):
        self.dut.reset.value = int(next_input.reset)
        self.dut.a.value = pack_matrix_to_int(
            next_input.a, self.params.OP_WIDTH)
        self.dut.b.value = pack_matrix_to_int(
            next_input.b, self.params.OP_WIDTH)
        if (next_input.reset):
            await ClockCycles(self.dut.clk, 1)
        else:
            await ClockCycles(self.dut.clk, STATES_PER_N * self.params.N)


@cocotb.test
async def test_systolic_matrix_multiplier(dut):
    params = get_params_from_env()
    cocotb.log.info(params)

    clock = Clock(dut.clk, 10, "ns")
    cocotb.start_soon(clock.start())

    # Synchronize clock
    await RisingEdge(dut.clk)

    n_checks = 20
    test = SystolicMatrixMultiplierTest(dut, params, n_checks)
    test.start_soon()

    # Operate
    cycles_per_reset = 1
    n_cycles = n_checks * (STATES_PER_N * params.N + cycles_per_reset)
    cocotb.log.info(f"Run for {n_cycles} cycles...")
    await ClockCycles(dut.clk, n_cycles)
