#!/usr/bin/env python3

from os import path

from setuptools import setup, find_packages

setup(
    name='ef',
    use_scm_version=True,
    license="MIT",
    description="Ef is a software for simulation of charged particles dynamics.",
    long_description=open(path.join(path.dirname(__file__), 'README.md'), encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='',
    author_email='',
    url='https://github.com/epicf/ef_python',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'ef = ef.main:main'
        ]
    },
    zip_safe=True,
    python_requires='>=3.6',
    setup_requires=['setuptools_scm', 'setuptools>=38.6.0', 'wheel>=0.31.0', 'twine>=1.11.0'],  # md description support
    install_requires=['numpy', 'h5py', 'matplotlib', 'rowan', 'sympy', 'simpleeval', 'scipy', 'jupyter'],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic:: Scientific / Engineering:: Physics'
    ],
    keywords=''
)
