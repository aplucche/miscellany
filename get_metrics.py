from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
import csv
url_base = 'https://www.pinterest.com'

with open('results.txt') as f:
    links = [url_base + item.strip() for item in f]


fieldnames = ['url', 'pins','followers']
for i, link in enumerate(links):
    print i, link
    row = {}
    r  = requests.get(link)
    data = r.content
    soup = BeautifulSoup(data, "lxml")
    pins = soup.find("div", class_="pinCount").find('span').string
    followers = soup.find("div", class_="followerCount").find('span').string
    #row['url'] = link
    print pins, followers
    '''
    row['pins'] = str(results[0].string)
    row['followers'] = str(results[1].string)
    print row
    '''