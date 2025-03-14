import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="gree_versati",
    python_requires=">=3.11",
    install_requires=requirements,
    author="Clifford Roche",
    author_email="",
    version="2.1.2",
    description="Discover, connect and control Gree based minisplit systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmroche/greeclimate",
    packages=setuptools.find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
