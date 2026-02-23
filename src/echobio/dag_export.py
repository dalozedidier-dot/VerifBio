"""Compatibility shim.

The project was renamed to **verifbio**.
This package remains as a thin wrapper for backward compatibility.
New code should import from `verifbio`.
"""

from verifbio.dag_export import *  # noqa: F401,F403
