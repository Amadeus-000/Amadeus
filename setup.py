from setuptools import setup, find_packages

setup(
    name="amadeus",
    version="4.0.4",
    packages=find_packages(),
    package_data={'amadeus': ['*.json']},
)