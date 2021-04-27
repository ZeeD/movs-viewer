from distutils.core import Command
from distutils.core import Distribution
from distutils.core import Extension
from sys import argv
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Type
from typing import Union

def setup(*,
          name: str = '',
          version: str = '',
          description: str = '',
          long_description: str = '',
          author: str = '',
          author_email: str = '',
          maintainer: str = '',
          maintainer_email: str = '',
          url: str = '',
          download_url: str = '',
          packages: List[str] = [],
          py_modules: List[str] = [],
          scripts: List[str] = [],
          ext_modules: List[Extension] = [],
          classifiers: List[str] = [],
          distclass: Type[Distribution] = Distribution,
          script_name: str = argv[0],
          script_args: List[str] = [],
          options: Dict[str, str] = {},
          license: str = '',
          keywords: Union[List[str], str] = [],
          platforms: Union[List[str], str] = [],
          cmdclass: Dict[str, Command] = {},
          data_files: List[str] = [],
          package_dir: Dict[str, str] = {},
          extra_require: Dict[str, List[str]] = {},
          package_data: Dict[str, List[str]] = {},
          python_requires: Optional[str] = None,
          install_requires: List[str] = [],
          entry_points: Dict[Literal['console_scripts'], List[str]]) -> None:
    ...


def find_packages() -> List[str]:
    ...
