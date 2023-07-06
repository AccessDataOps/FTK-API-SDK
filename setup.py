## setup.py

"""Python Setup Manager"""

from setuptools import setup
from os.path import abspath, dirname, join

##

this_directory = dirname(abspath(__file__))
requirements_path = join(this_directory, "requirements.txt")

reqs = [line.strip('\n') for line in open(requirements_path, "r").readlines()]

##

VERSION = "1.0.1"

##

if __name__ == "__main__":
	setup(
		name="exterro-ftk-sdk",
		version=VERSION,
		description="Python Library for FTK API",
		author="Thomas Vieth",
		author_email="thomas.vieth@exterro.com",
		url="https://github.com/AccessDataOps/FTK-API-SDK",
		packages=[
			"exterro",
			"exterro.api"
		],
		install_requires=reqs,
		setup_requites=reqs,
		package_dir={"exterro": "exterro"},
		include_package_data=True
	)
