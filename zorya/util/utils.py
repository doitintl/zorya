"""Misc utils."""


def fatal_code(e):
    """
    In case of a 500+ errcode do backoff.

    :param e: execption
    :return:
    """
    return e.resp.status < 500


def get_prev_idx(idx, matrix_size):
    """
    Get the previous index in the matrix.
    Args:
        idx: current index
        matrix_size: matrix size

    Returns:

    """
    if idx == 0:
        return matrix_size - 1
    else:
        return idx - 1
