import shutil
from wp1.selection_tools.constants import DATA_DIR
from wp1.selection_tools.projects_list import (
    build_translated_list,
)
import pathlib
from wp1.selection_tools.wiki import en, fr, endless


def build_custom_selections(
    lang_code: str,
    scores_fp: pathlib.Path,
    data_dir: pathlib.Path,
    tmp_dir: pathlib.Path,
):
    custom_dir = data_dir / "customs"
    custom_dir.mkdir(exist_ok=True, parents=True)
    # Translate custom selections from English
    if lang_code != "en":
        langlinks_fp = tmp_dir / f"{lang_code}.langlinks.tsv"
        en_customs = data_dir / "en.needed" / "customs"
        if en_customs.is_dir():
            for src in sorted(
                project for project in en_customs.iterdir() if project.is_file()
            ):
                build_translated_list(
                    src, lang_code, scores_fp, langlinks_fp, custom_dir
                )

    # Copy hardcoded selections
    if DATA_DIR.exists():
        for src in DATA_DIR.iterdir():
            if src.is_file():
                shutil.copy(src, custom_dir / src.name)

    if lang_code == "en":
        en.build_custom_selections(custom_dir, data_dir, tmp_dir)
    elif lang_code == "fr":
        fr.build_custom_selections(custom_dir, data_dir, tmp_dir, scores_fp)

    endless.build_custom_selection(lang_code, custom_dir)
