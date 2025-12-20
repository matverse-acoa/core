from setuptools import find_packages, setup

setup(
    name="acoa-core",
    version="1.0.0b0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[],
)
