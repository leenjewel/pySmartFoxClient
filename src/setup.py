#!/usr/bin/env python

import distutils.core
import os

extensions = []

version = "0.1"

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
django_dir = 'it'

def fullsplit(path, result=None):
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

for dirpath, dirnames, filenames in os.walk(django_dir):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

distutils.core.setup(
    name="pySmartFoxClient",
    version=version,
    packages = packages,
    package_data = {},
    data_files = data_files,
    ext_modules = extensions,
    author="leenjewel",
    author_email="leenjewel@gmail.com",
    url="https://github.com/leenjewel/pySmartFoxClient",
    download_url="https://github.com/leenjewel/pySmartFoxClient",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="pySmartFoxClient is a client for SmartFoxServer.",
)
