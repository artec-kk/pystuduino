# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


def main():
    description = 'studuino'

    setup(
        name='studuino',
        version='0.9.0',
        author='Artec',
        url='www.artec-kk.co.jp',
        description=description,
        long_description=description,
        zip_safe=False,
        include_package_data=True,
        packages=find_packages(),
        install_requires=['pyserial', 'numpy', 'matplotlib'],
        tests_require=[],
        setup_requires=[],
    )


if __name__ == '__main__':
    main()

