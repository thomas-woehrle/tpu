import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge


# TODO refactor these methods in an utils file
def pack_array_to_int(array: list[int] | np.ndarray, op_width: int):
    """
    Creates an integer representing the elements of the array as binary. 

    Elements with lower index with be at lower significant bits - i.e. array[0] will be the LSBs
    """
    packed_value = 0
    for i, value in enumerate(array):
        if len(f"{value:b}") > op_width:
            raise ValueError(
                f"Limit of {op_width} bits. {value}=={value:b} needs {len(f"{value:b}")} bits")
        packed_value |= value << (i * op_width)

    return packed_value


def get_random_array(low: int, high: int, length: int) -> list[int]:
    """low and high are inclusive as in the python random module"""
    numpy_array = np.random.randint(low, high+1, length)
    return [int(value) for value in numpy_array]


@cocotb.test
async def test_gemm_input_manager(dut):
    clock = Clock(dut.clk, 2, "sec")
    cocotb.start_soon(clock.start())

    # synchronize clock
    await RisingEdge(dut.clk)

    await FallingEdge(dut.clk)
    for i in range(10):
        new_a_column = get_random_array(0, 255, 2)
        new_a_column_ena = get_random_array(0, 1, 2)
        new_b_row = get_random_array(0, 255, 2)
        new_b_row_ena = get_random_array(0, 1, 2)

        dut.new_a_column.value = pack_array_to_int(new_a_column, 8)
        dut.new_a_column_ena.value = pack_array_to_int(new_a_column_ena, 1)
        dut.new_b_row.value = pack_array_to_int(new_b_row, 8)
        dut.new_b_row_ena.value = pack_array_to_int(new_b_row_ena, 1)
        await FallingEdge(dut.clk)

        # TODO extend this with self-checking behavior
