from setuptools import setup, find_packages

setup(
    name="Amadeus",
    version="4.0.12",
    packages=find_packages(),
    package_data={'amadeus': ['*.json'],'faure': ['*.json']},
)