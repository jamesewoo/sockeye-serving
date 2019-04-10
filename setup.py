from glob import glob
from os.path import splitext, basename

from setuptools import setup, find_packages

setup(
    name='sockeye-serving',
    version='1.0.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True
)
