from setuptools import setup

setup(
    name="typer-speed-test",
    version="1.0.0",
    description="A sleek terminal-based typing speed test app built with Python and curses.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Bhavish",
    py_modules=["typer", "stats_manager", "texts"],
    install_requires=[
        "windows-curses; sys_platform == 'win32'",
    ],
    entry_points={
        "console_scripts": [
            "typer=typer:cli",
            "speedtyper=typer:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console :: Curses",
    ],
    python_requires=">=3.7",
)
