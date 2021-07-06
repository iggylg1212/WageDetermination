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
import time
import pickle
import json


class WebScraper(object):

    def __init__(self):
        self.url = ['https://classes.berkeley.edu/search/site?f%5B0%5D=im_field_term_name%3A2176&f%5B1%5D=im_field_term_name%3A2010&f%5B2%5D=im_field_term_name%3A2208&f%5B3%5D=im_field_term_name%3A583&f%5B4%5D=im_field_term_name%3A839&f%5B5%5D=im_field_term_name%3A582&f%5B6%5D=im_field_term_name%3A589&f%5B7%5D=im_field_term_name%3A618&f%5B8%5D=im_field_term_name%3A1961&f%5B9%5D=im_field_term_name%3A1174&f%5B10%5D=im_field_term_name%3A851&f%5B11%5D=im_field_term_name%3A770&f%5B12%5D=im_field_term_name%3A865&f%5B13%5D=im_field_term_name%3A774&f%5B14%5D=im_field_term_name%3A789&f%5B15%5D=im_field_term_name%3A831']
        for i in range(1,4456):
            add_on = f'https://classes.berkeley.edu/search/site?page={str(i)}&f%5B0%5D=im_field_term_name%3A2176&f%5B1%5D=im_field_term_name%3A2010&f%5B2%5D=im_field_term_name%3A2208&f%5B3%5D=im_field_term_name%3A583&f%5B4%5D=im_field_term_name%3A839&f%5B5%5D=im_field_term_name%3A582&f%5B6%5D=im_field_term_name%3A589&f%5B7%5D=im_field_term_name%3A618&f%5B8%5D=im_field_term_name%3A1961&f%5B9%5D=im_field_term_name%3A1174&f%5B10%5D=im_field_term_name%3A851&f%5B11%5D=im_field_term_name%3A770&f%5B12%5D=im_field_term_name%3A865&f%5B13%5D=im_field_term_name%3A774&f%5B14%5D=im_field_term_name%3A789&f%5B15%5D=im_field_term_name%3A831'
            self.url.append(add_on)
        self.url = [self.url[i:i + 8] for i in range(0, len(self.url), 8)]

        self.df = pd.DataFrame(columns=['Title','Semester','Instr 1','Instr 2','Department','School','Min. Units','Enrolled','Max. Enrollment','Waitlisted','Max. Waitlisted'])
        asyncio.run(self.main())

    async def extract_page(self, html):
        soup = BeautifulSoup(html, 'lxml')
        data = None
        main_row = []
        while data is None:
            try:
                data = soup.find_all("div", {"class": "handlebarData theme_is_whitehot"})
                for i in range(0,len(data)):
                    data[i] = str(data[i]).replace('&quot;','')
                    data_proc = [e+'}\' ' for e in data[i].split('}\' ') if e]
                    ## Semester ##
                    try:
                        semester = data_proc[3].split(',')[0].replace('data-node=\'{\"termName\":','').replace('data-term-details=\"{sessionDescription:','').replace('data-term-details=\'{sessionDescription:','')
                    except:
                        semester = None
                    ## Title ##
                    try:
                        title = data_proc[2].split(',')
                        title = [e for e in title if 'displayName' in e][0].replace('\"displayName\":','').replace('displayName:','')
                    except:
                        title = None
                    ### Department ##
                    try:
                        dept = data_proc[2].split('},')
                        dept = [e for e in dept if "academicOrganization" in e][0].split(',')
                        dept = [e for e in dept if 'formalDescription' in e][0].replace('\"formalDescription\":','').replace('formalDescription:','')
                    except:
                        dept = None
                    #### School ###
                    try:
                        school = data_proc[2].split('},')
                        school = [e for e in school if "academicGroup" in e][0].split(',')
                        school = [e for e in school if 'formalDescription' in e][0].replace('\"formalDescription\":','').replace('formalDescription:','')
                    except:
                        school = None
                    #### Instructor ###
                    try:
                        instr = data_proc[2].split(',')
                        instr_1 = [e for e in instr if "formattedName" in e][0].replace('\"formattedName\":','').replace('formattedName:','')
                        try:
                            assn_n = [e for e in instr if "assignmentNumber" in e][-1].replace('\"assignedInstructors\":[{\"assignmentNumber\":','').replace('\"assignmentNumber\":','').replace('{','')
                            instr_2 = [e for e in instr if "formattedName" in e and assn_n!='1' ][-1].replace('\"formattedName\":','').replace('formattedName:','')
                        except:
                            instr_2 = None
                    except:
                        instr_1 = None
                        instr_2 = None
                    #### Units #####
                    try:
                        whole = data_proc[2].split('},')
                        allowed = ['units:','minUnits:','\"units\":','\"minUnits\":']

                        def allowable(str):
                            truth = False
                            for i in allowed:
                                if i in str:
                                    truth = True
                                    break
                            return truth
                        try:
                            units = [str(e) for e in whole if allowable(e)][0].split(',')[1].replace('\"value\":{\"fixed":{\"units":','').replace('}','').replace('value:{fixed:{units:','').replace('\"value\":{\"range\":{\"minUnits\":','').replace('value:{range:{minUnits:','').replace('\"value\":{\"discrete\":{\"units\":[','').replace('value:{discrete:{units:[','')
                        except:
                            units = [str(e) for e in whole if 'allowedUnits' in str(e)][0].split(',')
                            units = [str(e) for e in units if 'minimum' in str(e)][0].replace('\"allowedUnits\":{\"minimum\":','').replace('allowedUnits:{minimum:','')

                        if units.isdigit() == False:
                            units = None
                    except:
                        units = None
                    #### Enrollment ####
                    try:
                        enroll_data = data[i].split(' ')
                        enroll_data = [string for string in enroll_data if 'data-enrollment' in string][0].split(',')
                        enroll = [string for string in enroll_data if 'enrolledCount' in string][0].replace('\"enrolledCount\":','')
                        capacity = [string for string in enroll_data if 'maxEnroll' in string][0].replace('\"maxEnroll\":','')
                        waitlisted = [string for string in enroll_data if 'waitlistedCount' in string][0].replace('\"waitlistedCount\":','')
                        waitlist_max = [string for string in enroll_data if 'maxWaitlist' in string][0].replace('\"maxWaitlist\":','')
                    except:
                        enroll = None
                        capacity = None
                        waitlisted = None
                        waitlist_max = None

                    row = [title, semester, instr_1, instr_2, dept, school, units, enroll, capacity, waitlisted, waitlist_max]
                    main_row.append(row)
            except:
                pass
        return main_row

    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                html = await response.text()
                rows = await self.extract_page(html)
                return rows
        except Exception as e:
            print(str(e))

    async def main(self):
        counter=0
        for urls in self.url:
            tasks = []
            async with aiohttp.ClientSession() as session:
                for url in urls:
                    tasks.append(self.fetch(session, url))

                htmls = await asyncio.gather(*tasks)
                for rows in htmls:
                    for row in rows:
                        row = pd.Series(row, index = self.df.columns)
                        self.df = self.df.append(row, ignore_index=True)
            counter+=1
            print(f'Percent done: {counter*100*8/4456}')

        self.df['Title'] = self.df['Title'].apply(lambda x: str(x).replace('"',''))
        self.df['Semester'] = self.df['Semester'].apply(lambda x: str(x).replace('"',''))
        self.df['Instr 1'] = self.df['Instr 1'].apply(lambda x: str(x).replace('"',''))
        self.df['Instr 2'] = self.df['Instr 2'].apply(lambda x: str(x).replace('"',''))
        self.df['Department'] = self.df['Department'].apply(lambda x: str(x).replace('"',''))
        self.df['School'] = self.df['School'].apply(lambda x: str(x).replace('"',''))
        self.df = self.df.reset_index(drop=True)

        self.df.to_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/berkeley_scrape.csv', index=False)

if __name__ == '__main__':
    scraper = WebScraper()
