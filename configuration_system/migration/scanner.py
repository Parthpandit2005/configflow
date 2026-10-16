from pathlib import Path


def validate_result_folder(result_root):
    """
    Validate the TestPro result folder.
    """

    result_root = Path(result_root)

    if not result_root.exists():
        raise FileNotFoundError(
            f"Result folder does not exist:\n{result_root}"
        )

    if not result_root.is_dir():
        raise NotADirectoryError(
            f"Path is not a directory:\n{result_root}"
        )

    return result_root


def find_ts_files(result_root):
    """
    Recursively find all TestPro TS result files.
    """

    result_root = validate_result_folder(result_root)

    ts_files = list(
        result_root.rglob("TS*")
    )

    return ts_files