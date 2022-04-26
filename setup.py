from setuptools import setup

setup(
    name="kratky_rg_izero",
    version="0.1.0",
    description="""
    Create overlaid Kratky plots from a directory of PRIMUS SAXS data
    """,
    url="https://github.com/gpwolfe/kratky_rg_izero",
    author="Alisha Jones, PhD; Gregory Wolfe; Brian Wolfe, PhD",
    author_email="wolfe.gregory.p@gmail.com",
    packages=["kratky_rg_izero"],
    install_requires=["matplotlib", "pandas"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
)
