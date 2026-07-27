"""Fallback setup.py for older pip versions."""
from setuptools import setup, find_packages

setup(
    name="videotool",
    version="1.0.0",
    description="A CLI tool to convert video files to image sequences",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.5",
    ],
    entry_points={
        "console_scripts": [
            "videotool=videotool.__main__:main",
        ],
    },
)
