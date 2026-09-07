from typing import IO, Any, Iterable


def write_tsv_rows_to_file(
    f: IO[Any], rows: Iterable[Any], null_value: str = "NULL"
) -> None:
    """Write rows of data to open file in TSV format"""
    for row in rows:
        line = "\t".join(null_value if v is None else str(v) for v in row)
        f.write(line + "\n")


def strip_prefix(titles: set[str], prefix: str) -> set[str]:
    return {t[len(prefix) :] if t.startswith(prefix) else t for t in titles}
