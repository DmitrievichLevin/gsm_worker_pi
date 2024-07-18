"""Nox sessions."""
# pylint: disable=redefined-outer-name
import sys
from pathlib import Path
from textwrap import dedent

import nox

try:
    from nox_poetry import Session
    from nox_poetry import session
except ImportError:
    message = f"""\
    Nox failed to import the 'nox-poetry' package.

    Please install it using the following command:

    {sys.executable} -m pip install nox-poetry"""
    raise SystemExit(dedent(message))


package = "media_microservice"
python_versions = ["3.10"]
nox.needs_version = ">= 2021.6.6"
nox.options.sessions = (
    "export-requirements",
    "pre-commit",
    "mypy",
    "tests",
    "typeguard",
)


def activate_virtualenv_in_precommit_hooks(session: Session) -> None:
    """Activate virtualenv in hooks installed by pre-commit.

    This function patches git hooks installed by pre-commit to activate the
    session's virtual environment. This allows pre-commit to locate hooks in
    that environment when invoked from git.

    Args:
        session: The Session object.
    """
    if session.bin is None:
        return

    virtualenv = session.env.get("VIRTUAL_ENV")
    if virtualenv is None:
        return

    hookdir = Path(".git") / "hooks"
    if not hookdir.is_dir():
        return

    for hook in hookdir.iterdir():
        if hook.name.endswith(".sample") or not hook.is_file():
            continue

        text = hook.read_text()
        bindir = repr(session.bin)[1:-1]  # strip quotes
        if not (
            Path("A") == Path("a") and bindir.lower() in text.lower() or bindir in text
        ):
            continue

        lines = text.splitlines()
        if not (lines[0].startswith("#!") and "python" in lines[0].lower()):
            continue

        header = dedent(
            f"""\
            import os
            os.environ.get("VIRTUAL_ENV"] = {virtualenv!r}
            os.environ.get("PATH"] = os.pathsep.join((
                {session.bin!r},
                os.environ.get("PATH", ""),
            ))
            """
        )

        lines.insert(1, header)
        hook.write_text("\n".join(lines))


@session(name="export-requirements", python="3.11")
def exportreqs(session: Session) -> None:
    """Export Requirements."""
    args = ["export", "-f", "requirements.txt", "--output", "requirements.txt", "--without-hashes"]

    session.run("poetry", *args)


@session(name="pre-commit", python=python_versions)
def precommit(session: Session) -> None:
    """Lint using pre-commit."""
    args = session.posargs or [
        "run",
        "--show-diff-on-failure",
    ]
    session.install(
        "black",
        "darglint",
        "flake8",
        "flake8-bandit",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-rst-docstrings",
        "pep8-naming",
        "pre-commit",
        "pre-commit-hooks",
        "reorder-python-imports",
    )

    session.run("pre-commit", *args)
    if args and args[0] == "install":
        activate_virtualenv_in_precommit_hooks(session)


@session(python=python_versions)
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or ["src", "tests"]
    session.install(".")
    session.install("mypy", "pytest", "types-click")
    session.run("mypy", *args)
    if not session.posargs:
        session.run(
            "mypy",
            f"--python-executable={sys.executable}",
            "noxfile.py",
        )


@session(python=python_versions)
def tests(session: Session) -> None:
    """Run the test suite."""
    session.install(".")
    session.install("pytest", "pygments")

    session.run(
        "pytest",
        *session.posargs,
    )


@session(python=python_versions)
def typeguard(session: Session) -> None:
    """Runtime type checking using Typeguard."""
    session.install(".")
    session.install("pytest", "typeguard", "pygments")
    session.run("pytest", f"--typeguard-packages={package}", *session.posargs)
