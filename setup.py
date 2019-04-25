import os
from glob import glob

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='sockeye-serving',
    version='1.0.1',
    author="James Woo",
    author_email="james.e.woo@gmail.com",
    description="A containerized service for neural machine translation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jamesewoo/sockeye-serving",
    install_requires=['mxnet-model-server', 'pyyaml', 'requests'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'sockeye_serving': ['scripts/*', 'scripts/nonbreaking_prefixes/*']},
    scripts=glob(os.path.join('bin', '*')),
    data_files=[('config', glob(os.path.join('config', '*'))),
                ('notebooks', glob(os.path.join('notebooks', '*')))],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Perl",
        "Programming Language :: Unix Shell",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Unix",
        "Development Status :: 4 - Beta",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ]
)
