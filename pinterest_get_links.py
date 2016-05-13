"""
    Pinterest User Scraper
    ~~~~~~~~~~~~~~~~~~~~~~~
    Get links for all Pinterest boards associated with a user.  Uses selenium to
    account for Pinterest's infinite scrolling
    Usage::
        python pinterest_get_links.py https://www.pinterest.com/aboutdotcom/ >> results.txt
"""

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
import click

@click.command()
@click.option('--scrollamt', default=10, help='Number of pages to scroll', type=int)
@click.argument('url')
def get_pinterest_links(url, scrollamt):
    browser = webdriver.Firefox()
    browser.get(url)
    for x in xrange(scrollamt):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
    soup = BeautifulSoup(browser.page_source, "lxml")
    results = soup.find_all("a", class_="boardLinkWrapper")
    for link in results:
        print(link.get('href'))

if __name__ == '__main__':
    get_pinterest_links(['https://www.pinterest.com/aboutdotcom/'])