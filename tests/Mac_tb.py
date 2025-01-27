import cocotb
from cocotb.clock import Clock
from cocotb.runner import get_runner
from cocotb.triggers import FallingEdge, ClockCycles


@cocotb.test()
async def test_mac_basic(dut):
    clock = Clock(dut.clk, 2, "sec")
    await cocotb.start(clock.start())

    dut.reset.value = 1
    await FallingEdge(dut.clk)

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
