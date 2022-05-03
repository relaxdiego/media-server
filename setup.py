import pathlib

from setuptools import find_packages, setup

# Some options here are taken from this handy guide:
# https://realpython.com/pypi-publish-python-package/

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    version="0.1.0",
    name="media_server",
    author="Mark S. Maglana",
    author_email="mmaglana@gmail.com",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/relaxdiego/media_server",
    python_requires="~=3.9",
    package_dir={"": "src"},
    include_package_data=True,
    packages=find_packages("src"),
    # https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ],
)
