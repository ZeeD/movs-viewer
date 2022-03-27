from contextlib import contextmanager
from os import listdir
from os.path import join
from tempfile import TemporaryDirectory
from typing import Any
from typing import Callable
from typing import Iterator
from typing import Type
from typing import Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.expected_conditions import all_of
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.support.expected_conditions import invisibility_of_element
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.expected_conditions import url_contains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from .constants import GECKODRIVER_PATH


def get_options(dtemp: str) -> Options:
    options = Options()

    # options.headless = True
    options.profile = FirefoxProfile()
    # set download folder
    options.profile.set_preference('browser.download.folderList', 2)
    options.profile.set_preference('browser.download.dir', dtemp)

    return options


def _w(wait: WebDriverWait,
       condition: Union[Type[element_to_be_clickable],
                        Type[presence_of_element_located],
                        Type[invisibility_of_element]],
       css_selector: str) -> Any:
    return wait.until(condition((By.CSS_SELECTOR, css_selector)))


def _c(wait: WebDriverWait, css_selector: str) -> Any:
    return _w(wait, element_to_be_clickable, css_selector)


def _p(wait: WebDriverWait, css_selector: str) -> Any:
    return _w(wait, presence_of_element_located, css_selector)


def _i(wait: WebDriverWait, css_selector: str) -> Any:
    return _w(wait, invisibility_of_element, css_selector)


def pl(wait: WebDriverWait, wd: WebDriver) -> None:
    _p(wait, '.pageLoader')
    founds = wd.find_elements(By.CSS_SELECTOR, '.pageLoader')
    wait.until(all_of(*(invisibility_of_element(found) for found in founds)))


@contextmanager
def get_movimenti(username: str,
                  password: str,
                  num_conto: str,
                  get_otp: Callable[[], str]) -> Iterator[str]:
    with TemporaryDirectory() as dtemp, \
            webdriver.Firefox(executable_path=GECKODRIVER_PATH,
                              options=get_options(dtemp)) as wd:
        wait = WebDriverWait(wd, 1000)
        # login
        wd.get(
            'https://bancoposta.poste.it/bpol/public/BPOL_ListaMovimentiAPP/index.html')
        pl(wait, wd)
        wd.find_element(By.CSS_SELECTOR, '#username').send_keys(username)
        wd.find_element(By.CSS_SELECTOR,
                        '#password').send_keys(password + Keys.RETURN)
        wait.until(url_contains(
            'https://idp-poste.poste.it/jod-idp-retail/cas/app.html'))
        pl(wait, wd)
        _c(wait, '#_prosegui').click()
        otp = get_otp()
        wd.find_element(By.CSS_SELECTOR, '#otp').send_keys(otp + Keys.RETURN)

        # choose conto and download text
        _p(wait, f'select.numconto>option[value="string:{num_conto}"]')
        pl(wait, wd)
        Select(_p(wait,
                  'select.numconto')).select_by_value(f'string:{num_conto}')

        # hide cookie banner
        wd.execute_script(
            'document.querySelector("#content-alert-cookie").style.display="none"')
        _c(wait, '#select>option[value=TESTO]')
        Select(_p(wait, '#select')).select_by_value('TESTO')

        print('prima: ', listdir(dtemp))
        _c(wait, '#downloadApi').click()
        _i(wait, '.waiting')
        print('dopo:  ', listdir(dtemp))

        yield join(dtemp, 'ListaMovimenti.txt')
