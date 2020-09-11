import ast
import sys

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version


class NoUnnecessaryFstringChecker(object):
    """
    A flake8 plugin to ban unnecessary f-strings.
    """

    name = "flake8-no-unnecessary-fstrings"
    version = version("flake8-no-unnecessary-fstrings")

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

    message_NUF001 = "NUF001 No f-strings without interpolation."

    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.JoinedStr):
                if not any(
                    isinstance(value, ast.FormattedValue) for value in node.values
                ):
                    yield (
                        node.lineno,
                        node.col_offset,
                        self.message_NUF001,
                        type(self),
                    )
