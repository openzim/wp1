import pathlib
from typing import IO, Any, Iterable


def read_lines_from_tsv_file(fp: pathlib.Path) -> list[str]:
    with fp.open(encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]


def _stringify(value: Any, null_value: str) -> str:
    if value is None:
        return null_value
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode("utf-8")
    return str(value)


def write_tsv_rows_to_file(
    f: IO[Any], rows: Iterable[Any], null_value: str = ""
) -> None:
    """Write rows of data to open file in TSV format"""
    for row in rows:
        line = "\t".join(_stringify(v, null_value) for v in row)
        f.write(line + "\n")


def strip_prefix(titles: set[str], prefix: str) -> set[str]:
    return {t[len(prefix) :] if t.startswith(prefix) else t for t in titles}
