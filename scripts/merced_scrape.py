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
import time
import pickle
import json


class WebScraper(object):

    def __init__(self):
        self.url = 'https://mystudentrecord.ucmerced.edu/pls/PROD/bwckschd.p_disp_dyn_sched'        
        try:
            self.df = pd.read_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/merced_scrape.csv')
        except:
            self.df = pd.DataFrame(columns=['Semester', 'Department', 'Course Title', 'Units', 'Instructor', 'Max. Enrollment', 'Enrollment'])
        
        self.get_data()

    def get_data(self):
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        self.driver.get(self.url)

        term_select = Select(self.driver.find_element_by_xpath('/html/body/div[3]/form/table/tbody/tr/td/select'))
        term_options = term_select.options
        
        for term in range(2,(len(term_options)+1)): 
            term_select = Select(self.driver.find_element_by_xpath('/html/body/div[3]/form/table/tbody/tr/td/select'))
            sem = self.driver.find_element_by_xpath(f'/html/body/div[3]/form/table/tbody/tr/td/select/option[{int(term)}]').text
            term_select.select_by_index(term-1)             
            self.driver.find_element_by_xpath('/html/body/div[3]/form/input[2]').click()

            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/table/tbody/tr[1]/td[1]/h2')))
            
            subjects_select = Select(self.driver.find_element_by_xpath('/html/body/div[3]/form/table[1]/tbody/tr/td[2]/select'))
            subjects_options = subjects_select.options
            
            for subject in range(1,(len(subjects_options)+1)):  
                subjects_select = Select(self.driver.find_element_by_xpath('/html/body/div[3]/form/table[1]/tbody/tr/td[2]/select'))
                dept = self.driver.find_element_by_xpath(f'/html/body/div[3]/form/table[1]/tbody/tr/td[2]/select/option[{int(subject)}]').text
                subjects_select.select_by_index(subject-1)             
                self.driver.find_element_by_xpath('/html/body/div[3]/form/input[12]').click()
                
                try:
                    WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/table[1]/caption')))
                except:
                    self.driver.back()
                    WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/form/table[1]/tbody/tr/td[1]/label/span')))
                    subjects_select = Select(self.driver.find_element_by_xpath('/html/body/div[3]/form/table[1]/tbody/tr/td[2]/select'))
                    dept = self.driver.find_element_by_xpath(f'/html/body/div[3]/form/table[1]/tbody/tr/td[2]/select/option[{int(subject)}]').text
                    subjects_select.deselect_by_index(subject-1)
                    continue

                for opt in range(0,1000):
                    try:
                        instr = self.driver.find_element_by_xpath(f'/html/body/div[3]/table[1]/tbody/tr[{str(opt+1)}]/td/table/tbody/tr[2]/td[7]').text
                        title = self.driver.find_element_by_xpath(f'/html/body/div[3]/table[1]/tbody/tr[{str(opt)}]/th/a').text
                        self.driver.find_element_by_xpath(f'/html/body/div[3]/table[1]/tbody/tr[{str(opt)}]/th/a').click()
                        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/table[1]/tbody/tr[2]/td/table')))
                        
                        unit = self.driver.find_element_by_xpath('/html/body/div[3]/table[1]/tbody/tr[2]/td').text
                        unit = unit.split('\n')
                        unit = [e for e in unit if 'Credits' in e][0]
                        max_enroll = self.driver.find_element_by_xpath('/html/body/div[3]/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[1]').text
                        actual_enroll = self.driver.find_element_by_xpath('/html/body/div[3]/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[2]').text 
                        
                        row = [sem, dept, title, unit, instr, max_enroll, actual_enroll]
                        row = pd.Series(row, index = self.df.columns)
                    
                        self.df = self.df.append(row, ignore_index=True)
                        self.driver.back()

                    except:
                        pass
                
                print(self.df)
                self.df.to_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/merced_scrape.csv', index=False)
                self.driver.back()

                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/form/table[1]/tbody/tr/td[1]/label/span')))
                subjects_select = Select(self.driver.find_element_by_xpath('/html/body/div[3]/form/table[1]/tbody/tr/td[2]/select'))
                dept = self.driver.find_element_by_xpath(f'/html/body/div[3]/form/table[1]/tbody/tr/td[2]/select/option[{int(subject)}]').text
                subjects_select.deselect_by_index(subject-1)

            self.driver.get(self.url)

        self.driver.close()    

if __name__ == '__main__':
    scraper = WebScraper()
