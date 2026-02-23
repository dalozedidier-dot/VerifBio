"""Compatibility shim.

The project was renamed to **verifbio**.
This package remains as a thin wrapper for backward compatibility.
New code should import from `verifbio`.
"""

from verifbio import __version__  # noqa: F401
