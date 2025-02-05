import numpy as np


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


def unpack_int_to_matrix(packed_value: int, matrix_shape: tuple, op_width: int) -> np.ndarray:
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
