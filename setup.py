import os
from glob import glob

from setuptools import setup, find_packages

setup(
    name='sockeye-serving',
    version='1.0.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    scripts=glob(os.path.join('bin', '*')),
    data_files=[('config', glob(os.path.join('config', '*'))),
                ('notebooks', glob(os.path.join('notebooks', '*'))),
                ('scripts', glob(os.path.join('scripts', '**'), recursive=True))],
    include_package_data=True
)
