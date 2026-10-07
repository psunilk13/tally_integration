from setuptools import setup, find_packages

setup(
	name="tally_integration",
	version="0.0.1",
	description="Tally Integration for ERPNext",
	author="Your Name",
	author_email="your.email@example.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=[
		"requests>=2.25.0",
	]
)
