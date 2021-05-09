"""Misc utils."""
import google.auth


def get_project_id():
    """
    Get the project if from the default env.
    """
    _, project_id = google.auth.default()
    return project_id


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
