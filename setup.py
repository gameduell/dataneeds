from setuptools import setup, find_packages

setup(
    name = "declares",
    version = "0.1",
    packages = find_packages(),
    scripts = [],
    package_data = {
        '': ['*.txt', '*.rst'],
    },

    # metadata for upload to PyPI
    author = "wabu",
    author_email = "wabu@fooserv.net",
    description = "declarative approch to your data",
    license = "MIT",
    keywords = "declarative python data dask",
    url = "https://github.com/gameduell/declares",
)
