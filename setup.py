from setuptools import find_packages
from setuptools import setup

setup(name='mypyui',
      version='0.0.1',
      author='Vito De Tullio',
      author_email='vito.detullio@gmail.com',
      description='qt ui for movs',
      url='https://github.com/ZeeD/mypyui',
      packages=find_packages(),
      python_requires='>=3.8',
      entry_points={
          'gui_scripts': [
              'mypyui = mypyui:main'
          ]
      },
      install_requires=[
          'qtpy',
          'PySide6',
          'movs',
          'movs-merger'
      ],
      package_data={
          'mypyui': ['resources/*']
      })
