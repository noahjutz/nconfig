from setuptools import setup
setup(
    name="nconfig",
    version="0.1",
    py_modules=["nconfig"],
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts":
            ["nconfig=nconfig:main"]
    },
)