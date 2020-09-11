import sys

import pytest
from inspect import cleandoc

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version

python_3_6_plus = pytest.mark.skipif(sys.version_info < (3, 6), reason="Python 3.6+")


def test_version(flake8dir):
    result = flake8dir.run_flake8(["--version"])
    version_string = "flake8-no-unnecessary-fstrings: " + version(
        "flake8-no-unnecessary-fstrings"
    )
    assert version_string in result.out_lines[0]


# assert helpers


PASS = object()
FAIL = object()


class Scenario:
    msg = "NUF001 No f-strings without interpolation."

    def __init__(self, name, python, should=None, expects=None):
        self.name = name
        self.python = cleandoc(python)
        self.should = should

        if should is PASS:
            expects = expects or ()

        if should is FAIL:
            expects = expects or (self.expects_msg(),)

        self.expects = expects or ()

    def __repr__(self):
        return self.name

    @property
    def test_name(self):
        prefix = "" if self.should is PASS else "no "
        return f"{prefix}catch {self.name}"

    @classmethod
    def expects_msg(cls, line=1, col=1):
        return f"./example.py:{line}:{col}: {cls.msg}"


# NUF001

scenarios = [
    Scenario("singlequote", "f''", should=FAIL),
    Scenario("doublequote", 'f""', should=FAIL),
    Scenario("braces", '"{}"', should=PASS),
    Scenario("braces", '"{{}}"', should=PASS),
    Scenario("braces", '"{{}}".format(1)', should=PASS),
    Scenario(
        "formatted value",
        """
        thing = 1
        f"{thing}"
        """,
        should=PASS,
    ),
    Scenario(
        "multiline formatted value",
        """
        asdf = 1
        (
            "thing"
            f"{asdf}"
        )
        """,
        should=PASS,
    ),
    Scenario(
        "multiline formatted value",
        """
        (
            "thing"
            f"asdf"
        )""",
        should=FAIL,
        expects=[Scenario.expects_msg(2, 5)],
    ),
    Scenario("regular format", '"{val}".format(1)', should=PASS),
]


@pytest.mark.parametrize("scenario", scenarios, ids=lambda s: s.test_name)
def test_NUF001(scenario, flake8dir):
    flake8dir.make_example_py(cleandoc(scenario.python))
    result = flake8dir.run_flake8()
    assert result.out_lines == list(scenario.expects)
