# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import os
from setuptools import setup
from setuptools import find_packages

try:
    with open('README.rst') as f:
        readme = f.read()
except IOError:
    readme = ''

def _requires_from_file(filename):
    return open(filename).read().splitlines()

# version
here = os.path.dirname(os.path.abspath(__file__))
version = next((line.split('=')[1].strip().replace("'", '')
                for line in open(os.path.join(here,
                                              'studuino',
                                              '__init__.py'))
                if line.startswith('__version__ = ')),
               '0.0.dev0')


def main():
    description = 'Python library for Studuino&ArtecRobo'

    setup(
        name='pystuduino',
        version='0.9.0',
        author='Artec Co., Ltd.',
        url='https://github.com/artec-kk/pystuduino',
        author_email='support@artec-kk.co.jp',
        maintainer='Artec Co., Ltd.',
        maintainer_email='support@artec-kk.co.jp',

        description=description,
        long_description=readme,
        packages=find_packages(),
        zip_safe=False,
        include_package_data=True,
        install_requires=['pyserial', 'numpy', 'matplotlib'],
        tests_require=[],
        setup_requires=[],
        entry_points="""
            # -*- Entry points: -*-
            [console_scripts]
            pkgdep = studuino.scripts.command:main
        """,
    )

if __name__ == '__main__':
    main()

