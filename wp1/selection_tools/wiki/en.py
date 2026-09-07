import pathlib
from wp1.selection_tools import strip_prefix, write_tsv_rows_to_file
from wp1.selection_tools.wiki import generate_category_entries, generate_langlinks


def build_projects_list(
    projects_dir: pathlib.Path, scores_fp: pathlib.Path, all_fp: pathlib.Path
):
    projects_dir.mkdir(exist_ok=True)

    scores: dict[str, int] = {}
    with scores_fp.open() as f:
        for line in f:
            title, score = line.rstrip("\n").split("\t")
            scores[title] = int(score)

    project_file_handles = {}

    def get_project_file_handle(project: str):
        fh = project_file_handles.get(project)
        if fh is None:
            fh = (projects_dir / (project.replace("/", "_") + ".tsv.tmp")).open("w")
        return fh

    with all_fp.open() as f:
        for line in f:
            fields = line.rstrip("\n").split("\t")
            title = fields[0]
            score = int(scores.get(title, 0))
            for rating in fields[6:]:
                project = rating.split("=", 1)[0]
                get_project_file_handle(project).write(f"{title}\t{score}\n")

    for fh in project_file_handles.values():
        fh.close()

    for tmp_fp in projects_dir.glob("*.tsv.tmp"):
        entries: list[tuple[str, int]] = []
        with tmp_fp.open() as f:
            for line in f:
                title, score = line.rstrip("\n").split("\t")
                entries.append((title, int(score)))
        entries.sort(key=lambda entry: entry[1], reverse=True)

        seen: set[tuple[str, int]] = set()
        titles: list[str] = []

        for title, score in entries:
            if (title, score) not in seen:
                seen.add((title, score))
                titles.append(title)

        out_fp = projects_dir / tmp_fp.name[:-4]  # strip ".tmp"
        out_fp.write_text("\n".join(titles) + "\n")
        tmp_fp.unlink()


def get_vital_articles():
    """Generate (level, page_title) for English vital articles, levels 1-4."""
    for level in (1, 2, 3, 4):
        category = f"Wikipedia_level-{level}_vital_articles"
        for talk_title in generate_category_entries(
            "en", [category], namespace=1, max_depth=5
        ):
            article = talk_title.split(":", 1)[1].replace(" ", "_")
            yield level, article


def build_custom_selections(
    custom_dir: pathlib.Path, data_dir: pathlib.Path, tmp_dir: pathlib.Path
):
    wikivoyage_dir = custom_dir / "wikivoyage"
    wikivoyage_dir.mkdir(exist_ok=True)
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
    with (custom_dir / "medicine.tsv").open("w") as f:
        write_tsv_rows_to_file(f, medicine)

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

    with (data_dir / "en.needed" / "medicine.langlinks.tsv").open("w") as f:
        write_tsv_rows_to_file(f, generate_langlinks("en", medicine, langs))

    # Ray Charles
    rays = generate_category_entries("en", ["Ray_Charles"], 0, 3)
    with (custom_dir / "ray_charles.tsv").open("w") as f:
        write_tsv_rows_to_file(f, sorted(rays))

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
    with (custom_dir / "movies.tsv").open("w") as f:
        write_tsv_rows_to_file(f, sorted(movies))

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
        with (custom_dir / f"{name}.tsv").open("w") as f:
            write_tsv_rows_to_file(f, sorted(cats - filter_out))
