import dataclasses

import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.runner import get_runner
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles


@dataclasses.dataclass
class Transaction:
    input: dict
    state: dict
    next_state: dict
    next_output: dict


class Test:
    def __init__(self, dut):
        self.dut = dut
        self.queue = Queue[Transaction]()

    async def monitor(self):
        while True:
            await RisingEdge(self.dut.clk)
            A = self.dut.A.value
            B = self.dut.B.value
            accumulator = self.dut.accumulator.value

            if (self.dut.ena.value and not self.dut.reset.value):
                await FallingEdge(self.dut.clk)
                t = Transaction(
                    input={
                        "A": A,
                        "B": B,
                    },
                    state={
                        "accumulator": accumulator
                    },
                    next_state={
                        "accumulator": self.dut.accumulator.value
                    },
                    next_output={
                        "C": self.dut.C.value
                    }
                )

                await self.queue.put(t)

    async def score(self):
        while True:
            t = await self.queue.get()
            expected = t.input["A"] * t.input["B"] + t.state["accumulator"]
            actual = t.next_output["C"].integer

            print("expected:", expected, "actual:", actual)
            assert expected == actual, (
                f"expected: {expected}, actual: {actual}")

    def generate_data(self):
        pass

    def drive_data(self):
        pass


@cocotb.test()
async def test_mac_basic(dut):
    clock = Clock(dut.clk, 2, "sec")
    await cocotb.start(clock.start())

    dut.reset.value = 1
    await FallingEdge(dut.clk)

    test = Test(dut)
    await cocotb.start(test.monitor())
    await cocotb.start(test.score())

    dut.reset.value = 0
    dut.ena.value = 1
    dut.A.value = 3
    dut.B.value = 2

    await ClockCycles(dut.clk, 4)


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
