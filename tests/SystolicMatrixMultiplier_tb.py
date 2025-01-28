import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge


def pack_array_to_int(array: list[int], op_width: int):
    packed_value = 0
    for i, value in enumerate(array):
        if len(f"{value:b}") > op_width:
            raise ValueError(
                f"Limit of {op_width} bits. {value}=={value:b} needs {len(f"{value:b}")} bits")
        packed_value |= value << (i * op_width)

    return packed_value


@cocotb.test
async def test_systolic_matrix_multiplier(dut):
    clock = Clock(dut.clk, 2, "sec")
    cocotb.start_soon(clock.start())

    # Synchronize clock
    await RisingEdge(dut.clk)

    a = [2, 3, 1, 2]
    b = [1, 2, 4, 1]
    op_width = 8

    dut.A.value = pack_array_to_int(a, op_width)
    dut.B.value = pack_array_to_int(b, op_width)

    # Reset
    await FallingEdge(dut.clk)
    dut.reset.value = 1
    await FallingEdge(dut.clk)
    dut.reset.value = 0

    await ClockCycles(dut.clk, 10)
