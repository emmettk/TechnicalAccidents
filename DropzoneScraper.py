# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 18:31:51 2018

@author: ekrupczak

Webscraping Dropzone.com Fatality reports
Example page: http://www.dropzone.com/fatalities/Detailed/9.shtml

#Adapted from: https://realpython.com/python-web-scraping-practical-introduction/
"""
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re
import pandas as pd

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
    
def get_fatality(url):
    raw_html = simple_get(url)
    if raw_html == None: return None
    else:
        html = BeautifulSoup(raw_html, 'html.parser')
    #    for h3 in html.select('h3'):
    #        print(h3)
    #    for label in html.select('label'):
    #        print(label)
    
        data = {}
        
        for label in html.findAll(['label', {'class': 'name'}]):
    #        print(label)
            regex = '(?:<label class="name" for="Title">)([^<>]+)(?:\:</label)'
            key = re.findall(regex, str(label))
            if len(key) >0:
                regex2 = '(?:'+str(label)+'\n<div class="value">\n)(.*)'
    #            print(regex2)
                value = re.findall(regex2, str(html))
    #            print(key[0], value[0].strip())
                try:
                    data[key[0]] = value[0].strip()
                except IndexError:
                    data[key[0]] = None
        desc_tag = '<label class="name" for="Title"><h3>Description</h3></label>\n<div class="value">\n'
        regex3 = '(?:'+desc_tag+')(.*)(?:LESSONS)'
        desc = re.findall(regex3, str(html), re.DOTALL)
    #    print(regex3, desc)
        #Some awkward overly-specific data cleaning because my regex isn't quite right
        data['Description'] = desc[0].replace("<p>", " ").replace("</p>"," ").replace("\n"," ").replace('</div>', '').replace('<!--','').strip()
        for key, value in data.items():
            if value == '</div>':
                data[key] = None
        return data
        
if __name__ == "__main__":
    fatality_database = pd.DataFrame()
    url_base= 'http://www.dropzone.com/fatalities/Detailed/'
    for casenumber in range(1, 1000):
        url = url_base+str(casenumber)+'.shtml'
        try:
            data = get_fatality(url)
        except IndexError: print('Problem with scraping', url)
        if data != None:
            print(casenumber)
            data['CaseNumber'] = casenumber
            fatality_database = fatality_database.append(pd.DataFrame(data, index = [casenumber]))
    fatality_database.to_csv('SkydivingFatalities2004to2017.csv')
        
    
    
