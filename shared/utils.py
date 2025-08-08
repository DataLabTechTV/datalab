import inflection
from anyascii import anyascii
from slugify import slugify


def fn_sanitize(filename: str, separator: str = "_"):
    return slugify(
        inflection.underscore(
            anyascii(filename),
        ),
        separator=separator,
    )
