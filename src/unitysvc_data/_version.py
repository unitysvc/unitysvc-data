"""Single source of truth for the package version.

The canonical version lives in ``pyproject.toml``'s ``[project]`` table
— that's what PyPI, ``pip install``, and ``pip show`` read. This
module asks ``importlib.metadata`` for the installed distribution's
version so downstream code can ``from unitysvc_data import __version__``
without the two values ever drifting apart.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("unitysvc-data")
except PackageNotFoundError:  # pragma: no cover
    # Running from a checkout that hasn't been ``pip install``-ed.
    __version__ = "0.0.0+unknown"

