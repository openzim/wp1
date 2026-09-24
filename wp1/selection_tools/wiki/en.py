import pathlib
from collections.abc import Generator
from wp1.selection_tools import strip_prefix, write_tsv_rows_to_file
from wp1.selection_tools.models import (
    ScoredTitle,
    VitalArticle,
    parse_page_score_with_ratings,
)
from wp1.selection_tools.wiki import generate_category_entries, generate_langlinks


def build_projects_list(
    projects_dir: pathlib.Path, scores_fp: pathlib.Path, all_fp: pathlib.Path
) -> None:
    projects_dir.mkdir(exist_ok=True)

    scores: dict[str, int] = {}
    with scores_fp.open(encoding="utf-8") as f:
        for line in f:
            title, score = line.rstrip("\n").split("\t")
            scores[title] = int(score)

    project_file_handles = {}

    def get_project_file_handle(project: str):
        fh = project_file_handles.get(project)
        if fh is None:
            fh = (projects_dir / (project.replace("/", "_") + ".tsv.tmp")).open(
                "w", encoding="utf-8"
            )
            project_file_handles[project] = fh
        return fh

    with all_fp.open(encoding="utf-8") as f:
        for line in f:
            row = parse_page_score_with_ratings(line)
            score = int(scores.get(row.article, 0))
            for rating in row.ratings:
                project = rating.split("=", 1)[0]
                get_project_file_handle(project).write(f"{row.article}\t{score}\n")

    for fh in project_file_handles.values():
        fh.close()

    for tmp_fp in projects_dir.glob("*.tsv.tmp"):
        entries: list[ScoredTitle] = []
        with tmp_fp.open(encoding="utf-8") as f:
            for line in f:
                title, score = line.rstrip("\n").split("\t")
                entries.append(ScoredTitle(title, int(score)))
        entries.sort(key=lambda entry: entry.score, reverse=True)

        seen: set[ScoredTitle] = set()
        titles: list[str] = []

        for entry in entries:
            if entry not in seen:
                seen.add(entry)
                titles.append(entry.title)

        out_fp = projects_dir / tmp_fp.name[:-4]  # strip ".tmp"
        out_fp.write_text("\n".join(titles) + "\n", encoding="utf-8")
        tmp_fp.unlink()


def get_vital_articles() -> Generator[VitalArticle, None, None]:
    for level in (1, 2, 3, 4):
        category = f"Wikipedia_level-{level}_vital_articles"
        for talk_title in generate_category_entries(
            "en", [category], namespace=1, max_depth=5
        ):
            article = talk_title.split(":", 1)[1].replace(" ", "_")
            yield VitalArticle(level, article)


def build_custom_selections(
    custom_dir: pathlib.Path, data_dir: pathlib.Path, tmp_dir: pathlib.Path
) -> None:
    wikivoyage_dir = custom_dir / "wikivoyage"
    wikivoyage_dir.mkdir(exist_ok=True)
    europe = generate_category_entries("en", ["Europe"], 0, 8, "wikivoyage.org")

    with (wikivoyage_dir / "europe.tsv").open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(f, sorted((title,) for title in set(europe)))

    unfiltered = strip_prefix(
        set(
            generate_category_entries(
                "en",
                [
                    "WikiProject_Women's_health_articles",
                    "WikiProject_Microbiology_articles",
                    "WikiProject_Physiology_articles",
                    "WikiProject_Medicine_articles",
                    "WikiProject_Dentistry_articles",
                    "WikiProject_Anatomy_articles",
                    "WikiProject_Pharmacology_articles",
                    "WikiProject_Sanitation_articles",
                ],
                1,
                5,
            )
        ),
        "Talk:",
    )

    medicine_filter = strip_prefix(
        set(
            generate_category_entries(
                "en",
                [
                    "WikiProject_Hospitals_articles",
                    "WikiProject_History_of_Science_articles",
                    "WikiProject_Academic_Journal_articles",
                    "WikiProject_Visual_arts_articles",
                    "WikiProject_Biography_articles",
                    "WikiProject_Companies_articles",
                ],
                1,
                5,
            )
        ),
        "Talk:",
    )

    medicine = sorted(unfiltered - medicine_filter) + [
        "Wikipedia:Books/Cancer_care",
        "Wikipedia:Books/Children's health",
        "Wikipedia:Books/Ears nose throat",
        "Wikipedia:Books/Endocrine disease",
        "Wikipedia:Books/Eye diseases",
        "Wikipedia:Books/General surgery",
        "Wikipedia:WikiProject_Medicine/Books/Heart_disease",
        "Wikipedia:Books/Infectious disease",
        "Wikipedia:Books/Medications",
        "Wikipedia:Books/Men's health",
        "Wikipedia:Books/Neurology",
        "Wikipedia:Books/Orthopedics",
        "Wikipedia:Books/Mental health",
        "Wikipedia:Books/Skin diseases",
        "Wikipedia:WikiProject_Women's_Health/Books/Women's_health",
    ]
    with (custom_dir / "medicine.tsv").open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(f, [(title,) for title in medicine])

    # Generate medicine.langlinks.tsv
    langs = [
        "ja",
        "as",
        "bn",
        "gu",
        "hi",
        "kn",
        "ml",
        "de",
        "bpy",
        "mr",
        "lo",
        "or",
        "pa",
        "ta",
        "te",
        "ur",
        "fa",
        "fr",
        "zh",
        "pt",
        "ar",
        "es",
        "it",
        "uk",
        "ru",
    ]

    with (data_dir / "en.needed" / "medicine.langlinks.tsv").open(
        "w", encoding="utf-8"
    ) as f:
        write_tsv_rows_to_file(f, generate_langlinks("en", medicine, langs))

    # Ray Charles
    rays = generate_category_entries("en", ["Ray_Charles"], 0, 3)
    with (custom_dir / "ray_charles.tsv").open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(f, sorted((title,) for title in rays))

    # Movies
    movies = strip_prefix(
        set(
            generate_category_entries(
                "en",
                [
                    "Actors_and_filmmakers_work_group_articles",
                    "WikiProject_Film_articles",
                ],
                1,
                5,
            )
        ),
        "Talk:",
    )
    with (custom_dir / "movies.tsv").open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(f, sorted((title,) for title in movies))

    # shared exclusion list (Biography + Companies)
    filter_out = strip_prefix(
        set(
            generate_category_entries(
                "en",
                [
                    "WikiProject_Biography_articles",
                    "WikiProject_Companies_articles",
                ],
                1,
                5,
            )
        ),
        "Talk:",
    )

    for name, cats in [
        ("physics", ["WikiProject_Physics_articles"]),
        ("molcell", ["WikiProject_Molecular_and_Cellular_Biology_articles"]),
        ("maths", ["WikiProject_Mathematics_articles"]),
        (
            "chemistry",
            ["WikiProject_Chemistry_articles", "WikiProject_Elements_articles"],
        ),
    ]:
        cats = strip_prefix(set(generate_category_entries("en", cats, 1, 5)), "Talk:")
        with (custom_dir / f"{name}.tsv").open("w", encoding="utf-8") as f:
            write_tsv_rows_to_file(f, sorted((title,) for title in cats - filter_out))
