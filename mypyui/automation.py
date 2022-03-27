from contextlib import contextmanager
from datetime import date
from os import listdir
from os import makedirs
from shutil import move
from tempfile import TemporaryDirectory
from typing import Iterable
from typing import Iterator
from typing import NamedTuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located)
from selenium.webdriver.support.expected_conditions import url_contains
from selenium.webdriver.support.ui import WebDriverWait

from .constants import GECKODRIVER_PATH


def firefox_profile(dtemp: str) -> FirefoxProfile:
    profile = FirefoxProfile()

    # set download folder
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.dir', dtemp)

    return profile


@contextmanager
def get_movimenti(username: str, password: str) -> Iterator[str]:
    with TemporaryDirectory() as dtemp, \
            webdriver.Firefox(executable_path=GECKODRIVER_PATH,
                              firefox_profile=firefox_profile(dtemp)) as d:
        wait = WebDriverWait(d, 10)

        yield 'fake-movimenti.txt'
