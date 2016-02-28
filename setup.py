from distutils.core import setup

setup(
    # Application name:
    name="Deploy",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Olivier Boucher",
    author_email="info@olivierboucher.com",

    # Packages
    packages=["app"],

    # Include additional files into the package
    include_package_data=True,

    # Scripts

    scripts=['bin/run'],

    # Details
    url="https://github.com/OlivierBoucher/Deploy",

    #
    # license="LICENSE.txt",
    description="Useful towel-related stuff.",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "paramiko",
        "gitpython",
        "jsonschema"
    ],
)