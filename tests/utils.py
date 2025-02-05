import os

import numpy as np
from cocotb.binary import BinaryValue


def get_params_from_env[ParamType](paramCls: type[ParamType]) -> ParamType:
    params = paramCls()

    for k, v in os.environ.items():
        if k.startswith("DUT_"):
            setattr(params, k[4:], int(v))

    return params


def pack_matrix_to_int(matrix: np.ndarray, op_width: int) -> int:
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
    # if the passed packed_value is a string it means it is "x" or "z"
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
