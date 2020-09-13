import sys
from inspect import cleandoc
from typing import Optional, Sequence, Tuple, Union

import pytest

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


class Scenario:
    msg = "NUF001 f-string without interpolation."

    PASS = "PASS"
    FAIL = "FAIL"

    should = None

    def __init__(
        self,
        name: str,
        python: str,
        expects: Optional[Sequence] = None,
        xfail: Union[str, bool] = False,
    ) -> None:
        self.name = name
        self.python = cleandoc(python)
        self.xfail = xfail

        if self.should is self.PASS:
            expects = expects or ()
        elif self.should is self.FAIL:
            expects = expects or (self.expects_msg(),)

        self.expects = expects or ()

    def __repr__(self) -> str:
        return self.name

    @property
    def test_name(self) -> str:
        prefix = "allow" if self.should is self.PASS else "disallow"
        return f"{prefix} {self.name}"

    @classmethod
    def expects_msg(cls, line: int = 1, col: int = 1) -> str:
        return f"./example.py:{line}:{col}: {cls.msg}"

    @classmethod
    def expects_msgs(cls, *lines_cols: Tuple[int, int]):
        return [cls.expects_msg(l, c) for (l, c) in lines_cols]


class PassingScenario(Scenario):
    should = Scenario.PASS


class FailingScenario(Scenario):
    should = Scenario.FAIL


# NUF001

scenarios = [
    FailingScenario("singlequote", "f''"),
    FailingScenario("doublequote", 'f""'),
    FailingScenario("doublequote", 'f""""""'),
    FailingScenario("doublequote", "f''''''"),
    PassingScenario("braces", '"{}"'),
    PassingScenario("braces", '"{{}}"'),
    PassingScenario("braces", '"{{}}".format(1)'),
    PassingScenario(
        "formatted value",
        """
        thing = 1
        f"{thing}"
        """,
    ),
    PassingScenario(
        "multiline formatted value",
        """
        asdf = 1
        (
            "thing"
            f"{asdf}"
        )
        """,
    ),
    FailingScenario(
        "multiline formatted value",
        """
        (
            "thing"
            f"asdf"
        )""",
        expects=[Scenario.expects_msg(2, 5)],
    ),
    PassingScenario("regular format", '"{val}".format(1)'),
    PassingScenario(
        "inner format string '.3f'",
        """
        import time
        import_start = time.time()
        import_end = time.time()
        cmd_name = "hi how are you?"
        f"{0.123456789:.3f}"
        f'Took {import_end - import_start:.3f} to import {cmd_name}'
        """,
    ),
    FailingScenario(
        "double bad strings",
        """
        f''
        f''
        """,
        expects=[Scenario.expects_msg(1, 1), Scenario.expects_msg(2, 1)],
    ),
    FailingScenario(
        "nested fstrings with no format",
        """
        f"{f''}"
        """,
        xfail="nested fstrings is not yet detected",
    ),
    PassingScenario(
        "nested fstrings with format",
        """
        a = 3
        f'{f"{a}"}'
        """,
    ),
]


@pytest.mark.parametrize("scenario", scenarios, ids=lambda s: s.test_name)
def test_NUF001(scenario, flake8dir):
    if scenario.xfail:
        pytest.xfail(
            scenario.xfail if isinstance(scenario.xfail, str) else "known failure"
        )

    flake8dir.make_example_py(cleandoc(scenario.python))
    result = flake8dir.run_flake8()
    assert result.out_lines == list(scenario.expects)
