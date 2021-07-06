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
        self.url = 'https://www.reg.uci.edu/perl/WebSoc'
        try:
            self.df = pd.read_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/irvine_scrape.csv')
        except:
            self.df = pd.DataFrame(columns=[])

        self.start_scrape()
    
    def start_scrape(self):
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        self.driver.get(self.url)
        term_select = Select(self.driver.find_element_by_xpath("/html/body/form/table/tbody/tr[1]/td[3]/select"))
        term_options = term_select.options
        for index in range(0,len(term_options)):
            self.driver.get(self.url)
            term_select = Select(self.driver.find_element_by_xpath("/html/body/form/table/tbody/tr[1]/td[3]/select"))
            term_select.select_by_index(index)
            dep_select = Select(self.driver.find_element_by_xpath("/html/body/form/table/tbody/tr[4]/td[3]/select"))
            dep_options = dep_select.options
            for index in range(1, len(dep_options)):
                dep_select = Select(self.driver.find_element_by_xpath("/html/body/form/table/tbody/tr[4]/td[3]/select"))
                dep_select.select_by_index(index)
                self.driver.find_element_by_xpath('/html/body/form/p[2]/input[2]').click()
                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/pre')))

                given_text = self.driver.find_element_by_xpath('/html/body/pre').text
                given_text = given_text.split('\n')
                if given_text[10] == '**** No courses matched your search criteria for this term.':
                    break
                
                no_class = 0

                term = given_text[8].split('      ')[0]
                school = given_text[13].replace('#','').strip()

                line_index = [i for i, s in enumerate(given_text) if '___________________________' in s]
                dept = given_text[line_index[0]+2].strip()
                
                body = given_text[line_index[1]:]
                body = [e for e in body if not '~' in e]
                
                header_index = [i for i, s in enumerate(body) if 'CCode' in s]
                
                for i in header_index:
                    class_name = body[i-1].strip().split('      ')[-1]
                    break_index = [i for i, s in enumerate(body) if '' == s]
                    break_index = [e for e in break_index if e!=0 and e!=1]
                    for j in break_index:
                        if j > i:
                            class_block = body[i+1:j]
                            for y in range(0,len(class_block)):
                                if y < len(class_block)-2:
                                    if len(class_block[y+1].strip().split('   '))==1:
                                        prof_2 = class_block[y+1].strip()
                                        if y < len(class_block)-3:
                                            if len(class_block[y+2].strip().split('   '))==1:
                                                prof_3 = class_block[y+2].strip()
                                            else:
                                                prof_3 = ''
                                        else:
                                            prof_3 = ''
                                    else:
                                        prof_2 = ''
                                        prof_3 = ''
                                else:
                                    prof_2 = ''
                                    prof_3 = ''
                                if len(class_block[y].strip().split('   '))<4:
                                    break 
                                
                                parsing = class_block[y].strip().split('   ')
                                
                                class_code = parsing[0].split(' ')[0]
                                typ = parsing[0].split(' ')[1]
                                sec = parsing[0].split(' ')[2]
                                unit = parsing[1]
                                prof_1 = parsing[2].split(' ')
                                prof_1 = [e for e in prof_1 if ',' in e or '.' in e]
                                prof_1 = (' ').join(prof_1)
                                
                                parsing = class_block[y].strip().split(' ')
                                parsing = [e for e in parsing if e.isdigit() or e=='n/a']
                                digit_index = [i for i, s in enumerate(parsing) if s.isdigit() or s=='n/a']
                            
                                max_enrollment = parsing[digit_index[-5]]
                                enrolled = parsing[digit_index[-4]]
                                waitlisted = parsing[digit_index[-3]]
                            
                                row = [term, school, dept, class_name, prof_1, prof_2, prof_3, class_code, typ, sec, unit, max_enrollment, enrolled, waitlisted]

                                print(row)
                
                # print(no_class)
                self.driver.back()
                
            self.df.to_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/irvine_scrape.csv', index=False)

        self.driver.close()

if __name__ == '__main__':
    scraper = WebScraper()