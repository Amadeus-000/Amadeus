from setuptools import setup, find_packages

setup(
    name="Amadeus",
    version="4.1.8",
    packages=find_packages(),
    package_data={'amadeus': ['*.json'],'faure': ['*.json']},
)