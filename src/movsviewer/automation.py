from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import all_of
from selenium.webdriver.support.expected_conditions import (
    element_to_be_clickable,
)
from selenium.webdriver.support.expected_conditions import (
    invisibility_of_element,
)
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
)
from selenium.webdriver.support.expected_conditions import url_contains
from selenium.webdriver.support.wait import WebDriverWait

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterator


logger = getLogger(__name__)


def get_options(dtemp: str) -> FirefoxOptions:
    profile = FirefoxProfile()
    # set download folder
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.dir', dtemp)

    options = FirefoxOptions()
    options.profile = profile
    return options


def _w(
    wait: WebDriverWait[Firefox],
    condition: 'Callable[[tuple[str,str]],Callable[[Firefox],bool|WebElement]]',
    css_selector: str,
) -> WebElement:
    ret = wait.until(condition((By.CSS_SELECTOR, css_selector)))
    if not isinstance(ret, WebElement):
        raise TypeError
    return ret


def _c(
    wait: WebDriverWait[Firefox], action: ActionChains, css_selector: str
) -> WebElement:
    ret = _w(wait, element_to_be_clickable, css_selector)
    action.move_to_element(ret)
    return ret


def _p(wait: WebDriverWait[Firefox], css_selector: str) -> WebElement:
    return _w(wait, presence_of_element_located, css_selector)


def _i(wait: WebDriverWait[Firefox], css_selector: str) -> WebElement:
    return _w(wait, invisibility_of_element, css_selector)


def pl(wait: WebDriverWait[Firefox], wd: Firefox) -> None:
    _p(wait, '.pageLoader')
    founds = wd.find_elements(By.CSS_SELECTOR, '.pageLoader')
    wait.until(all_of(*(invisibility_of_element(found) for found in founds)))


@contextmanager
def get_movimenti(num_conto: str) -> 'Iterator[Path]':
    with (
        TemporaryDirectory() as dtemp,
        Firefox(options=get_options(dtemp)) as wd,
    ):
        wait = WebDriverWait(wd, 1000)
        action = ActionChains(wd)

        # login
        wd.get('https://bancoposta.poste.it')
        wait.until(url_contains('https://securelogin.poste.it'))
        wd.find_element(By.CSS_SELECTOR, '#truste-consent-required2').click()
        wait.until(url_contains('https://bancoposta.poste.it'))

        # usare xpath document.querySelectorAll('.link-lever')
        # e testo: "Conto BancoPosta 001030700957"
        text = f'Conto BancoPosta  {num_conto}'
        logger.info('text: %s', text)

        pdtemp = Path(dtemp)

        logger.info('prima: %s', list(pdtemp.iterdir()))
        _c(
            wait,
            action,
            '[ng-click="formatoDownload=\'EXCEL\';downloadMovimenti();"]',
        ).click()
        logger.info('dopo:  %s', list(pdtemp.iterdir()))

        yield pdtemp / 'ListaMovimenti.txt'
