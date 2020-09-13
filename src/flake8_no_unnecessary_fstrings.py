import ast
import sys
from collections import deque

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version


class NoUnnecessaryFstringChecker(object):
    """
    A flake8 plugin to ban unnecessary f-strings.
    """

    name = "flake8-no-unnecessary-fstrings"
    version = version(name)

    message_NUF001 = "NUF001 f-string without interpolation."

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

    def check_joinedstring_has_formatted_value(self, node: ast.JoinedStr) -> bool:
        return any(isinstance(value, ast.FormattedValue) for value in ast.walk(node))

    def nuf001_msg(self, node):
        return (
            node.lineno,
            node.col_offset,
            self.message_NUF001,
            type(self),
        )

    def run(self):
        todo = deque([self.tree])
        while todo:
            node = todo.popleft()

            if isinstance(node, ast.JoinedStr):
                is_good = self.check_joinedstring_has_formatted_value(node)
                if not is_good:
                    yield self.nuf001_msg(node)
            else:
                # only visit children of non-JoinedStr nodes
                todo.extend(ast.iter_child_nodes(node))
