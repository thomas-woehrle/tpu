import dataclasses

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


class Test:
    def __init__(self, dut):
        self.dut = dut
        self.queue = Queue[tuple[Snapshot, Snapshot]]()

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
            await self.queue.put(t)

    async def score(self):
        while True:
            t = await self.queue.get()
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

    def generate_data(self):
        pass

    def drive_data(self):
        pass


@cocotb.test
async def test_mac_basic(dut):
    clock = Clock(dut.clk, 2, "sec")
    cocotb.start_soon(clock.start())

    # synchronize Clk
    await RisingEdge(dut.clk)

    # Start Monitor and Score
    test = Test(dut)
    cocotb.start_soon(test.monitor())
    cocotb.start_soon(test.score())

    # Reset
    await FallingEdge(dut.clk)
    dut.reset.value = 1
    dut.A.value = 3
    dut.B.value = 2

    # Activate Normal Operation
    await FallingEdge(dut.clk)
    dut.reset.value = 0
    dut.ena.value = 1

    # Operate for 4 ClockCycles
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
