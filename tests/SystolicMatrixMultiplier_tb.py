import dataclasses
import os

import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles

from utils import pack_matrix_to_int, unpack_int_to_matrix


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
class Output:
    c: np.ndarray


def get_params_from_env() -> Parameters:
    params = Parameters()

    for k, v in os.environ.items():
        if k.startswith("DUT_"):
            setattr(params, k[4:], int(v))

    return params


class Test:
    def __init__(self, dut, params: Parameters, n_checks: int):
        self.dut = dut
        self.params = params
        self.n_checks = n_checks
        self.transaction_queue = Queue[tuple[Input, Output]]()
        self.input_queue = Queue[Input]()

    def get_input_from_dut(self) -> Input:
        return Input(
            reset=bool(self.dut.reset.value),
            a=unpack_int_to_matrix(
                self.dut.a.value, (self.params.N, self.params.N), self.params.OP_WIDTH),
            b=unpack_int_to_matrix(
                self.dut.b.value, (self.params.N, self.params.N), self.params.OP_WIDTH)
        )

    def get_output_from_dut(self) -> Output:
        return Output(
            c=unpack_int_to_matrix(
                self.dut.mac_manager.flat_mac_accumulators.value,
                (self.params.N, self.params.N),
                self.params.ACC_WIDTH
            )
        )

    async def monitor(self):
        await RisingEdge(self.dut.clk)
        while True:
            input = self.get_input_from_dut()

            if (input.reset):
                await ClockCycles(self.dut.clk, 1)
            else:
                await ClockCycles(self.dut.clk, STATES_PER_N * self.params.N)
            output = self.get_output_from_dut()

            # put transaction in queue
            t = (input, output)
            await self.transaction_queue.put(t)

    async def score(self):
        while True:
            t = await self.transaction_queue.get()
            if t[0].reset:
                cocotb.log.info("Asserting reset")
                assert np.all(t[1].c == 0)
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

    async def generate_input(self):
        # val_max is exclusive
        val_max = 2 ** self.params.OP_WIDTH

        for i in range(self.n_checks):
            d = Input(
                reset=True,
                a=np.random.randint(
                    0, val_max, (self.params.N, self.params.N)),
                b=np.random.randint(0, val_max, (self.params.N, self.params.N))
            )
            await self.input_queue.put(d)
            d = Input(
                reset=False,
                a=np.random.randint(
                    0, val_max, (self.params.N, self.params.N)),
                b=np.random.randint(0, val_max, (self.params.N, self.params.N))
            )
            await self.input_queue.put(d)

    async def drive_input(self):
        counter = 0
        while True:
            await FallingEdge(self.dut.clk)
            d = await self.input_queue.get()
            self.dut.reset.value = int(d.reset)
            self.dut.a.value = pack_matrix_to_int(d.a, self.params.OP_WIDTH)
            self.dut.b.value = pack_matrix_to_int(d.b, self.params.OP_WIDTH)
            if (d.reset):
                await ClockCycles(self.dut.clk, 1)
            else:
                await ClockCycles(self.dut.clk, STATES_PER_N * self.params.N)
            counter += 1


@cocotb.test
async def test_systolic_matrix_multiplier(dut):
    params = get_params_from_env()
    cocotb.log.info(params)

    clock = Clock(dut.clk, 10, "ns")
    cocotb.start_soon(clock.start())

    # Synchronize clock
    await RisingEdge(dut.clk)

    n_checks = 20
    test = Test(dut, params, n_checks)
    cocotb.start_soon(test.monitor())
    cocotb.start_soon(test.score())
    cocotb.start_soon(test.generate_input())
    cocotb.start_soon(test.drive_input())

    # Operate
    await ClockCycles(dut.clk, 1000)
