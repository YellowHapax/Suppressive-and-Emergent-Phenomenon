"""MBD-Framework Interactive Labs

Paper-focused simulation laboratories demonstrating the
Memory as Baseline Deviation framework.

Each sub-package corresponds to one paper in the MBD series.
Every lab module exposes three functions:

    describe()  -> dict   metadata, thesis abstract, paper DOI
    run(**kw)   -> dict   pure simulation returning timeseries + summary
    plot(res)   -> fig    matplotlib visualisation of run() output
"""
