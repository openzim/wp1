import pathlib
from wp1.selection_tools import strip_prefix, write_tsv_rows_to_file
from wp1.selection_tools.projects_list import build_translated_titles
from wp1.selection_tools.wiki import generate_category_entries


def build_custom_selections(
    custom_dir: pathlib.Path,
    tmp_dir: pathlib.Path,
    data_dir: pathlib.Path,
    scores_fp: pathlib.Path,
):
    # Tunisie
    tunisie = strip_prefix(
        set(
            generate_category_entries(
                "fr", ["Évaluation_des_articles_du_projet_Tunisie"], 1, 5
            )
        ),
        "Discussion:",
    )
    with (custom_dir / "tunisie.tsv").open("w") as f:
        write_tsv_rows_to_file(
            f,
            sorted(tunisie) + ["Portail:Tunisie/Index thématique"],
        )

    # Medicine = translated English + native French lists
    langlinks_file = tmp_dir / "fr.langlinks.tsv"
    translated = build_translated_titles(
        data_dir / "en.needed" / "customs" / "medicine.tsv",
        "fr",
        scores_fp,
        langlinks_file,
    )
    native = strip_prefix(
        set(
            generate_category_entries(
                "fr",
                [
                    "Évaluation_des_articles_du_projet_Soins_infirmiers_et_profession_infirmière",
                    "Évaluation_des_articles_du_projet_Premiers_secours_et_secourisme",
                    "Évaluation_des_articles_du_projet_Médecine",
                    "Évaluation_des_articles_du_projet_Anatomie",
                    "Évaluation_des_articles_du_projet_Pharmacie",
                ],
                1,
                5,
            )
        ),
        "Discussion:",
    )

    with (custom_dir / "medicine.tsv").open("w") as f:
        write_tsv_rows_to_file(f, sorted(set(translated) | native))
