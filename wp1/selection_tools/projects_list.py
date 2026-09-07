import pathlib


def build_langlinks(
    lang_code: str, en_needed_dir: pathlib.Path, out_fp: pathlib.Path
) -> None:
    lines = set()
    for name in ("langlinks.tsv", "medicine.langlinks.tsv"):
        src = en_needed_dir / name
        if not src.exists():
            continue

        with src.open() as f:
            for line in f:
                line = line.rstrip("\n")
                parts = line.split("\t")
                if len(parts) == 3 and parts[1] == lang_code:
                    lines.add(line)

        with out_fp.open("w") as f:
            for line in sorted(lines):
                f.write(line + "\n")


def build_translated_titles(
    title_fp: pathlib.Path,
    lang_code: str,
    scores_fp: pathlib.Path,
    langlinks_fp: pathlib.Path,
) -> list[str]:
    titles = set()
    with title_fp.open() as f:
        for line in f:
            titles.add(line.rstrip("\n"))

    scores = {}
    with scores_fp.open() as f:
        for line in f:
            title, score = line.rstrip("\n").split("\t")
            scores[title] = int(score)

    results: dict[str, int] = {}
    with langlinks_fp.open() as f:
        for line in f:
            source, lang, target = line.rstrip("\n").split("\t")
            if lang == lang_code and source in titles:
                results[target] = scores.get(target, 0)
    return sorted(results, key=results.get, reverse=True)


def build_translated_list(
    src: pathlib.Path,
    lang_code: str,
    scores_fp: pathlib.Path,
    langlinks_fp: pathlib.Path,
    out_dir: pathlib.Path,
) -> None:
    titles = build_translated_titles(src, lang_code, langlinks_fp, scores_fp)
    (out_dir / src.name).write_text("\n".join(titles) + "\n")
