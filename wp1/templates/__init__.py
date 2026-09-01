from jinja2 import Environment, PackageLoader, select_autoescape


def commas(n):
    return "{:,d}".format(n)


def importance_label(value):
    """Display form of an importance rating, which is stored with a '-Class'
    suffix (e.g. b'High-Class' -> 'High-Importance'). See openzim/wp1#115."""
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    if value.endswith("-Class"):
        value = value[: -len("-Class")] + "-Importance"
    return value


env = Environment(
    loader=PackageLoader("wp1", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)
env.filters["commas"] = commas
env.filters["importance_label"] = importance_label
