"""Compatibility shim.

The project was renamed to **verifbio**.
This package remains as a thin wrapper for backward compatibility.
New code should import from `verifbio`.
"""

from verifbio.exporters import *  # noqa: F401,F403
