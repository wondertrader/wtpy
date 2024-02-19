#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree

from setuptools import setup, Command, Distribution

NAME = 'wtpy'
DESCRIPTION = 'Python Sub Framework Of WonderTrader'
URL = 'https://github.com/wondertrader/wtpy'
EMAIL = 'silencesword@foxmail.com'
AUTHOR = 'Wesley Liu'
REQUIRES_PYTHON = '>=3.7.0'
VERSION = '0.9.10'

REQUIRED = [
    'numpy', 
    'pandas',
    'chardet',
    'pyyaml',
    'pyquery',      # WtHotPicker引用的模块
    'xlsxwriter',   # WtBtAnalyst引用的模块
    'deap',         # WtCtaGAOptimizer引用的模块
    'psutil',       # WatchDog引用的模块
    'fastapi',      # WtMonSvr引用的模块
    'uvicorn',      # WtMonSvr引用的模块
    'itsdangerous', # WtMonSvr引用的模块
    'websockets>=9.1'    # WtMonSvr引用的模块
]

EXTRAS = {}

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}
about['__version__'] = VERSION
    
class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True

class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=['wtpy'],
    install_requires=REQUIRED,
    package_data={"": [
        "*"
    ]},
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    cmdclass={
        'upload': UploadCommand
    }
)