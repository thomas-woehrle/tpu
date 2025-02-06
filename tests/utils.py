"""Contains utilities which can be used in the cocotb tests

Contains:
    * get_params_from_env
    * pack_matrix_to_int
    * unpack_binary_value_to_matrix
"""
import os

import numpy as np
from cocotb.binary import BinaryValue


def get_params_from_env[ParamType](paramCls: type[ParamType]) -> ParamType:
    """Accumulates DUT_... environment variables into an object

    Returns:
        The Parameter Object
    """
    params = paramCls()

    for k, v in os.environ.items():
        if k.startswith("DUT_"):
            setattr(params, k[4:], int(v))

    return params


def pack_matrix_to_int(matrix: np.ndarray, op_width: int) -> int:
    """Packs an np array into a single integer

    Currently only works with positive integers, but can easily be extended

    Args:
        matrix: The matrix to pack
        op_width: The op_width to use for each element. Fe if op_width is 8,
            then 1 becomes 0000_0001

    Raises:
        ValueError: Raised if a value in the matrix does not fit into the op_width

    Returns:
        _description_
    """
    packed_value = 0
    for i, value in enumerate(matrix.flatten()):
        # convert because numpy ints have fixed width
        value = int(value)
        if len(f"{value:b}") > op_width:
            raise ValueError(
                f"Limit of {op_width} bits. {value}=={value:b} needs {len(f"{value:b}")} bits")
        packed_value |= value << (i * op_width)

    return int(packed_value)


def unpack_binary_value_to_matrix(packed_value: BinaryValue, matrix_shape: tuple, op_width: int) -> np.ndarray | None:
    """Unpacks a BinaryValue to a matrix

    BinaryValue is the type that signals obtained from a cocotb simulation have.

    Args:
        packed_value: The value to unpack
        matrix_shape: The shape of the matrix to unpack to
        op_width: The operand width of the values. Fe if op_width is 8,
            then 0001_0001 resolves to 17 and not 1, 1

    Returns:
        The matrix as np array
    """
    # checks whether the packed_value contains "x" or "z"
    if not packed_value.is_resolvable:
        return None

    # Create an empty matrix with the given shape
    matrix = np.zeros(np.prod(matrix_shape), dtype=int)

    # Flatten the matrix shape to get the correct number of elements
    num_elements = np.prod(matrix_shape)

    for i in range(num_elements):
        # Extract the value by shifting right by (i * op_width) bits
        value = (packed_value >> (i * op_width)) & ((1 << op_width) - 1)

        # Assign the extracted value to the matrix at the corresponding position
        matrix[i] = value

    # Reshape the matrix to the original shape
    return matrix.reshape(matrix_shape)
