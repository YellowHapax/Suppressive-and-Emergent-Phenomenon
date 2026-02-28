"""
mbd — Memory as Baseline Deviation
====================================
A computational framework for personality dynamics, adversarial horizon
engineering, and the mathematics of psychological captivity and recovery.

Papers 1–8 by Brandon Everett (ORCID: 0000-0001-7521-5469).
DOI index: https://doi.org/10.5281/zenodo.18652919
"""

__version__ = "0.8.0"
__author__ = "Brandon Everett"
__orcid__ = "0000-0001-7521-5469"

__all__ = ["KERNEL", "ALEPH", "VECTORS", "aleph", "describe"]


def __getattr__(name: str):
    """Lazy import from mbd.paper8 to avoid circular-import warning
    when running `python -m mbd.paper8` directly."""
    if name in __all__:
        import mbd.paper8 as _p8
        return getattr(_p8, name)
    raise AttributeError(f"module 'mbd' has no attribute {name!r}")
