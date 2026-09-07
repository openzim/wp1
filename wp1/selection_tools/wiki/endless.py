import pathlib
from wp1.selection_tools.constants import DATA_DIR
from wp1.selection_tools import read_lines_from_tsv_file, write_tsv_rows_to_file


def build_custom_selection(lang_code: str, custom_dir: pathlib.Path):
    base_sel = DATA_DIR / "endless" / lang_code / "base_selection"
    if not base_sel.is_file():
        return

    base_path = custom_dir.parent / base_sel.read_text().strip()
    if not base_path.is_file():
        return

    combined = read_lines_from_tsv_file(base_path)

    whitelist = DATA_DIR / "endless" / lang_code / "whitelist.tsv"
    if whitelist.is_file():
        combined += read_lines_from_tsv_file(whitelist)
    combined = list(dict.fromkeys(combined))

    blacklist = DATA_DIR / "endless" / lang_code / "blacklist.tsv"
    if blacklist.is_file():
        bl = set(read_lines_from_tsv_file(blacklist))
        combined = [t for t in combined if t not in bl]

    with (custom_dir / "endless.tsv").open("w") as f:
        write_tsv_rows_to_file(f, combined)
