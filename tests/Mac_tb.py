import dataclasses

import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.runner import get_runner
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles


@dataclasses.dataclass
class Snapshot:
    ena: bool
    reset: bool
    A: int
    B: int
    C: int


@dataclasses.dataclass
class Transaction[T0, T1]:
    before_snapshot: T0
    after_snapshot: T1


class Test:
    def __init__(self, dut):
        self.dut = dut
        self.queue = Queue[Transaction[Snapshot, Snapshot]]()

    def get_snapshot_from_dut(self) -> Snapshot:
        return Snapshot(
            ena=bool(self.dut.ena.value),
            reset=bool(self.dut.reset.value),
            A=self.dut.A.value.integer,
            B=self.dut.B.value.integer,
            C=self.dut.C.value.integer
        )

    async def monitor(self):
        while True:
            await RisingEdge(self.dut.clk)
            before_snapshot = self.get_snapshot_from_dut()

            await FallingEdge(self.dut.clk)
            after_snapshot = self.get_snapshot_from_dut()

            t = Transaction(before_snapshot, after_snapshot)
            await self.queue.put(t)

    async def score(self):
        while True:
            t = await self.queue.get()
            if (t.before_snapshot.ena and not t.before_snapshot.reset):
                expected = t.before_snapshot.A * t.before_snapshot.B + t.before_snapshot.C
                actual = t.after_snapshot.C

                print("expected:", expected, "actual:", actual)
                assert expected == actual, (f"expected: {
                                            expected}, actual: {actual}")

    def generate_data(self):
        pass

    def drive_data(self):
        pass


@cocotb.test
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
