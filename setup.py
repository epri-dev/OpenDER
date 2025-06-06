# Copyright © 2023 Electric Power Research Institute, Inc. All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met: 
# · Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# · Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# · Neither the name of the EPRI nor the names of its contributors may be used 
#   to endorse or promote products derived from this software without specific
#   prior written permission.

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


setup(
    name='opender',
    version='2.2.0',
    license='BSD',
    description='Open-source Distributed Energy Resources (DER) Model that represents IEEE Standard 1547-2018 '
                'requirements for steady-state and dynamic analyses',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    long_description_content_type='text/x-rst',
    author='Yiwei Ma, Wei Ren, Paulo Radatz, Jithendar Anandan',
    author_email='yma@epri.com, wren@epri.com, pradatz@epri.com',
    url='https://github.com/epri-dev/opender',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
    project_urls={

        # 'Changelog': 'https://py_dss_interface.readthedocs.io/en/latest/changelog.html', #TODO change
        # 'Issue Tracker': 'https://github.com/PauloRadatz/py_dss_interface/issues', #TODO change
        'Homepage': 'https://www.epri.com/OpenDER',
        'Model Specification': 'https://www.epri.com/research/products/000000003002030962'
        # 'Documentation': 'https://py_dss_interface.readthedocs.io/', #TODO change
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=3.7',
    install_requires=["numpy", "matplotlib", "pandas"],
    extras_require={
           "dev": ["pytest", "pytest-cov"], #"sphinx-rtd-theme", "nbsphinx", "black", "pre-commit", "tox", "twine", "sdist", "wheel"]
    },
)
