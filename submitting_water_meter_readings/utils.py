#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import logging
import os.path
import sys
import time
from pathlib import Path
from typing import Tuple

# pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


TOKEN = Path(__file__).resolve().parent / 'TOKEN'
LOGIN, PASSWORD = TOKEN.read_text().splitlines()


def get_logger(name=__file__):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(message)s')

    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setFormatter(formatter)
    log.addHandler(sh)

    return log


log = get_logger()


def get_driver(headless=False) -> webdriver.Firefox:
    options = Options()
    if headless:
        options.add_argument('--headless')

    profile_directory = r'%AppData%\Mozilla\Firefox\Profiles\p75l82q1.for_mail__selenium'
    profile_directory = os.path.expandvars(profile_directory)

    driver = webdriver.Firefox(firefox_profile=profile_directory, options=options)
    # driver.implicitly_wait(5)  # seconds

    return driver


def open_web_page_water_meter(value_cold: int, value_hot: int) -> Tuple[bool, str]:
    url = 'https://mgn-city.ru/'

    value_cold = str(value_cold)
    value_hot = str(value_hot)

    driver = get_driver()
    driver.get(url)
    log.info(f'Title: {driver.title!r}')

    time.sleep(5)

    try:
        driver.find_element(By.CSS_SELECTOR, '.profile-username')
    except Exception:
        raise Exception('Похоже, нужно авторизоваться!')

    url = 'https://mgn-city.ru/SN/YourIndications'
    driver.get(url)
    log.info(f'Title: {driver.title!r}')

    time.sleep(5)

    input_cold = driver.find_element(By.CSS_SELECTOR, 'input[data-service="Холодное водоснабжение"]')
    input_cold.send_keys(value_cold)

    input_hot = driver.find_element(By.CSS_SELECTOR, 'input[data-service="ГВС (компонент х/в)"]')
    input_hot.send_keys(value_hot)

    return True, ''


if __name__ == '__main__':
    open_web_page_water_meter(123, 456)
