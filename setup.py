import glob
import os
import typing

import setuptools


setuptools.setup(name='mypyui',
                 version='0.0.1',
                 author='Vito De Tullio',
                 author_email='vito.detullio@gmail.com',
                 description='qt ui for movs',
                 url='https://github.com/ZeeD/mypyui',
                 packages=setuptools.find_packages(),
                 python_requires='>=3.8',
                 entry_points={
                     'console_scripts': [
                         'mypyui = mypyui:main'
                     ]
                 },
                 install_requires=[
                     'PySide2',
                     'movs'
                 ],
                 package_data={
                     'resources': glob.glob('static/**', recursive=True)
                 })
