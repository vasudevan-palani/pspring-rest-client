from setuptools import setup

setup(
    name='pspring-rest-client',
    version='0.0.9',
    license='TBD',
    author='Vasudevan Palani',
    author_email='vasudevan.palani@gmail.com',
    url='https://github.com/vasudevan-palani/pspring-rest-client',
    long_description="README.md",
    packages=['pspringrestclient'],
    install_requires=["pspring>=0.0.1"],
    include_package_data=True,
    description="A rest client for easier life",
)
