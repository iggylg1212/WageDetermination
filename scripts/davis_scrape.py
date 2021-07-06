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
        self.url = 'https://registrar-apps.ucdavis.edu/courses/search/index.cfm'
        try:
            self.df = pd.read_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/davis_scrape.csv')
        except:
            self.df = pd.DataFrame(columns=['Title','Department','Semester','Instructor','Units','Enrolled','Max. Enrollment'])

        self.start_scrape()
    def start_scrape(self):
        counter = 0
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        self.driver.get(self.url)
        term_select = Select(self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div/div/div/div/div/div/div/div/div/div/div/table/tbody/tr[2]/td[1]/form[2]/div[1]/table/tbody/tr/td[1]/h1/span/select"))
        term_options = term_select.options
        for index in range(2, 
        #len(term_options)
         7):
            self.driver.get(self.url)
            term_select = Select(self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div/div/div/div/div/div/div/div/div/div/div/table/tbody/tr[2]/td[1]/form[2]/div[1]/table/tbody/tr/td[1]/h1/span/select"))
            term_select.select_by_index(index)
            dep_select = Select(self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div/div/div/div/div/div/div/div/div/div/div/table/tbody/tr[2]/td[1]/form[2]/div[3]/table/tbody/tr[2]/td/h1/select"))
            dep_options = dep_select.options
            for index in range(1, len(dep_options)):
                dep_select.select_by_index(index)
                self.driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div/div/div/div/div/div/div/div/div/div/table/tbody/tr[2]/td[1]/form[2]/div[8]/table/tbody/tr/td/h1/input[5]').click()
                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div/div/div/div/div/div/div/div/div/div/div/table/tbody/tr[2]/td[1]/div/h2/table/tbody/tr[1]/td')))
                
                try:
                    no_cla = int(self.driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div/div/div/div/div/div/div/div/div/div/table/tbody/tr[2]/td[1]/div/h2/table/tbody/tr[1]/td').text.replace(' CRN\'s found.',''))
                    counter += no_cla
                    for i in range(0,no_cla*2):
                        try:
                            self.driver.find_element_by_xpath(f'/html/body/div[4]/div/div/div/div/div/div/div/div/div/div/div/div/div/table/tbody/tr[2]/td[1]/div/h2/table/tbody/tr[{str(i)}]/td[6]/a').click()
                            
                            while self.driver.find_element_by_xpath('/html/body/div[9]').text == 'Course Summary\n Loading...':
                                time.sleep(.05)
                            
                            given_text = self.driver.find_element_by_xpath('/html/body/div[9]').text.split('\n')
                            try:
                                title = given_text[1]
                            except:
                                title = ''
                            try:
                                dept = [e for e in given_text if 'Subject Area' in e][0].replace('Subject Area: ','')
                            except:
                                dept = ''
                            try:
                                term = [e for e in given_text if 'Term' in e][0].replace('Term: ','')
                            except:
                                term = ''
                            try:
                                instr = [e for e in given_text if 'Instructor' in e][0].replace('Instructor: ','')
                            except:
                                instr = ''
                            try:
                                units = [e for e in given_text if 'Units' in e][0].replace('Units: ','')
                            except:
                                units = ''
                            try:
                                enroll = [e for e in given_text if 'Available Seats' in e][0].replace('Available Seats: ','')
                            except:
                                enroll = ''
                            try:
                                max_enroll = [e for e in given_text if 'Maximum Enrollment' in e][0].replace('Maximum Enrollment: ','')
                            except:
                                max_enroll = ''

                            row = [title,dept,term,instr,units,enroll,max_enroll]
                            row = pd.Series(row, index = self.df.columns)
                            self.df = self.df.append(row, ignore_index=True)
                            
                            try:
                                self.driver.find_element_by_xpath('/html/body/div[8]/div[1]/div/div/div[2]').click()
                            except:
                                self.driver.find_element_by_xpath('/html/body/div[9]/div[1]/div/div/div[2]').click()
                        
                        except:
                            pass
                except:
                    pass
            
                print(self.df)
                print(counter)
            self.df.to_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/davis_scrape.csv', index=False)

        self.driver.close()

if __name__ == '__main__':
    scraper = WebScraper()
