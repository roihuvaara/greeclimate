import re

import setuptools

# Read version from __init__.py
with open("gree_versati/__init__.py", "r") as f:
    version_match = re.search(r'__version__ = "(.*?)"', f.read())
    if version_match:
        version = version_match.group(1)
    else:
        version = "1.0.0"  # Fallback version

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="gree_versati",
    python_requires=">=3.11",
    install_requires=requirements,
    author="Jukka Roihuvaara",
    author_email="",
    version=version,
    description="Discover, connect and control Gree based minisplit systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roihuvaara/greeclimate",
    packages=setuptools.find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
