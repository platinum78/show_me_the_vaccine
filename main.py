import time, json, sys
from re import search

import selenium
from selenium import webdriver
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import telegram

from scripts.vaccine_watcher import VaccineWatcher
from scripts.vaccine_parser import VaccineStatus, vaccine_status_parser
from scripts.point import Point
from scripts.bounds import SearchBound

if __name__ == "__main__":
    bounds_string = sys.argv[1]
    bounds = [float(x) for x in bounds_string.split("%3B")]
    watcher = VaccineWatcher(
        bound1=Point(bounds[0], bounds[1]),
        bound2=Point(bounds[2], bounds[3]),
        search_interval=2.0,
        notify_interval=60
    )
    watcher.run_search()