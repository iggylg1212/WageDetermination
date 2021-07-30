import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import asyncio
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
import time
import pickle
import json


class WebScraper(object):

    def __init__(self):
        self.url = 'https://sa.ucla.edu/ro/public/soc'
        try:
            self.df = pd.read_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/la_scrape.csv')
        except:
            self.df = pd.DataFrame(columns=['Term','Department','Class Code','Title','Section #','Section','Enrollment Status','Waitlist Status','Units','Instructor'])

        self.start_scrape()

    def start_scrape(self):
        def getShadowRoot(host):
            shadowRoot = self.driver.execute_script("return arguments[0].shadowRoot", host)
            return shadowRoot
        
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        self.driver.get(self.url)
                                                                    
        host1 = self.driver.find_element_by_tag_name('ucla-sa-soc-app')
        root1 = getShadowRoot(host1)
        
        term_select = root1.find_element_by_id('optSelectTerm')
        term_select = Select(term_select)
        term_options = term_select.options
        for x in range(0,len(term_options)): 
            self.driver.get(self.url)
            host1 = self.driver.find_element_by_tag_name('ucla-sa-soc-app')
            root1 = getShadowRoot(host1)  

            term_select = root1.find_element_by_id('optSelectTerm')
            term_select = Select(term_select)
            term_options = term_select.options
            
            term_select.select_by_index(x) 
            time.sleep(2)

            host2 = root1.find_element_by_id('select_filter_subject')
            root2 = getShadowRoot(host2)
            
            root2.find_element_by_id('IweAutocompleteContainer').click()
            subjects = len(root2.find_element_by_id('dropdownitems').text.split('\n'))
            
            for y in range(0,subjects):

                host1 = self.driver.find_element_by_tag_name('ucla-sa-soc-app')
                root1 = getShadowRoot(host1)  

                term_select = root1.find_element_by_id('optSelectTerm')
                term_select = Select(term_select)
                term_options = term_select.options
            
                term_select.select_by_index(x) 

                time.sleep(2)
                
                host2 = root1.find_element_by_id('select_filter_subject')
                root2 = getShadowRoot(host2)
                time.sleep(2)
                root2.find_element_by_id('IweAutocompleteContainer').click()
                root2.find_element_by_id(f'option-{str(y)}').click()
                time.sleep(10)
                try:
                    root1.find_element_by_id('div_btn_go').click()
                except:
                    self.driver.get(self.url)
                    continue
                    time.sleep(10)

                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/main')))
                                
                try:
                    host1 = self.driver.find_element_by_tag_name('ucla-sa-soc-app')
                    root1 = getShadowRoot(host1)

                    pages = root1.find_element_by_id('divPagination').text.split('\n')
                    pages = [int(e) for e in pages if e.isdigit()][-1]
                except:
                    pages = 1    
                
                try: 
                    host1 = self.driver.find_element_by_tag_name('ucla-sa-soc-app')
                    root1 = getShadowRoot(host1)

                    no_results = root1.find_element_by_id('spanNoSearchResults').text
                except:
                    no_results = ''

                if no_results != '':
                    self.driver.get(self.url)
                    continue
                    time.sleep(10)
                
                counter=0
                while counter < pages:
                    host1 = self.driver.find_element_by_tag_name('ucla-sa-soc-app')
                    root1 = getShadowRoot(host1)

                    term = root1.find_element_by_id('spanSearchResultsHeader').text.replace('Your results for: ','').split(' ')[0:2]
                    term = ('').join(term)
                    dept = root1.find_element_by_id('spanSearchResultsHeader').text.replace('Your results for: ','').split(' ')[2:-1]
                    dept = ('').join(dept)
                    
                    root1.find_element_by_id('expandAll').click()
                    time.sleep(10)
                    
                    pageload = True
                    while pageload:    
                        try: 
                            results = root1.find_element_by_id('resultsTitle').get_attribute('innerHTML')
                            results = results.split('>')
                            results = [e.replace('\n            <div class="row-fluid class-title" id="','').replace('"','').strip() for e in results if 'row-fluid class-title' in e]
                            
                            for i in results:
                                if 'No results available' not in root1.find_element_by_id(f'{i}-container').text:
                                    code = i 
                                    title = root1.find_element_by_id(f'{i}-title').text
                                    
                                    time.sleep(3)
                                    i_d = root1.find_element_by_id(f'{code}-children').get_attribute('innerHTML').split('>')
                                    i_d = [e.replace('\n        <input id="','').replace('-checkbox" type="checkbox"','') for e in i_d if f'_{code}-checkbox" type="checkbox"' in e][0]
                                    i_d = i_d.split('_')[0]
                                    
                                    section = root1.find_element_by_id(f'{i_d}_{code}-section').text
                                    status = root1.find_element_by_id(f'{i_d}_{code}-status_data').text
                                    waitlist = root1.find_element_by_id(f'{i_d}_{code}-waitlist_data').text
                                    units = root1.find_element_by_id(f'{i_d}_{code}-units_data').text
                                    instructor = root1.find_element_by_id(f'{i_d}_{code}-instructor_data').text
                                    
                                    row = [term,dept,code,title,i_d,section,status,waitlist,units,instructor]
                                    row = pd.Series(row, index = self.df.columns)
                                    self.df = self.df.append(row, ignore_index=True)
                                    
                                    claim = True
                                    cap = 1
                                    while claim:
                                        try:
                                            s_i_d = str(int(i_d)+cap)

                                            section = root1.find_element_by_id(f'{s_i_d}_{code}-section').text
                                            status = root1.find_element_by_id(f'{s_i_d}_{code}-status_data').text
                                            waitlist = root1.find_element_by_id(f'{s_i_d}_{code}-waitlist_data').text
                                            units = root1.find_element_by_id(f'{s_i_d}_{code}-units_data').text
                                            instructor = root1.find_element_by_id(f'{s_i_d}_{code}-instructor_data').text
                                            
                                            row = [term,dept,code,title,i_d,section,status,waitlist,units,instructor]
                                            row = pd.Series(row, index = self.df.columns)
                                            self.df = self.df.append(row, ignore_index=True)
                                            cap +=1

                                        except:
                                            claim = False 
                                else:
                                    pass         

                            pageload=False
                            counter+=1
                            print(self.df)
                            if counter < pages:
                                root1.find_element_by_link_text(str(counter+1)).click()
                                time.sleep(5)
                            else:
                                break
                        
                        except:
                            print('i')
                            pass
                
                self.driver.get(self.url)
            
            self.df.to_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/la_scrape.csv', index=False)
                
if __name__ == '__main__':
    scraper = WebScraper()
