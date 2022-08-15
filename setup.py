## setup.py

"""Python Setup Manager"""

from setuptools import setup
from os.path import abspath, dirname, join

##

this_directory = dirname(abspath(__file__))
requirements_path = join(this_directory, "requirements.txt")

reqs = [line.strip('\n') for line in open(requirements_path, "r").readlines()]

##

VERSION = "0.8.0"

##

if __name__ == "__main__":
	setup(
		name="accessdata-sdk",
		version=VERSION,
		description="Python Library for AccessData's API",
		author="Thomas Vieth",
		author_email="thomas.vieth@exterro.com",
		url="https://github.com/AccessDataOps/FTK-API-SDK",
		packages=[
			"accessdata",
			"accessdata.api"
		],
		install_requires=reqs,
		setup_requites=reqs,
		package_dir={"accessdata": "accessdata"},
		include_package_data=True
	)