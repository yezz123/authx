import os
import typing as t

import setuptools

from authx import __author__, __author_email__, __license__, __version__

directory = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def parse_requirement(req_path: str) -> t.List[str]:
    with open(os.path.join(directory, "", req_path)) as f:
        contents = f.read()
        return [i.strip() for i in contents.strip().split("\n")]


setuptools.setup(
    name="authx",
    version=__version__,
    author=__author__,
    platforms=["any"],
    description="Ready to use and customizable Authentications and Oauth2 management for FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://authx.yezz.codes/",
        "Source Code": "https://github.com/yezz123/AuthX",
        "Bug Tracker": "https://github.com/yezz123/AuthX/issues",
        "Funding": "https://opencollective.com/yezz123",
    },
    packages=setuptools.find_packages(exclude=["tests"]),
    license=__license__,
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Customer Service",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        # Waiting For this PR to Merged for adding FastAPI
        # https://github.com/pypa/trove-classifiers/pull/80
        # "Framework :: FastAPI",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: Session",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=parse_requirement("requirements.txt"),
    extras_require={"dev": ["requests == 2.26.1", "uvicorn"]},
)
