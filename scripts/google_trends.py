import pandas as pd
import datetime
import numpy as np
from pytrends.request import TrendReq
import gtab
from sentence_transformers import SentenceTransformer, util
import os
import csv
import pickle
import time

uc = pd.read_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/data/uc.csv')
uc['name'] = uc.apply(lambda x: x['first_name']+' '+x['last_name'], axis=1)
uc = uc[['index','university','field','name']]

texas = pd.read_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/data/texas.csv')
texas['university'] = 'Texas'
texas = texas[['index','university','department','name']]
texas.columns = ['index','university','field','name']
texas['field'] = texas.apply(lambda x: str(x['field']).replace('[','').replace(']','').replace("'",'').replace('"',''), axis=1)

michigan = pd.read_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/data/michigan.csv')
michigan['university'] = 'Michigan'
michigan['name'] = michigan.apply(lambda x: x['first_name']+' '+x['last_name'], axis=1)
michigan = michigan[['index','university', 'APPOINTING DEPT','name']]
michigan.columns = ['index','university','field','name']

illinois = pd.read_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/data/illinois.csv')
illinois['name'] = illinois['name'].apply(lambda x: x.split(','))
illinois['name'] = illinois['name'].apply(lambda x: ((' ').join(x[1:])+' '+x[0]).replace('  ',''))
illinois = illinois[['index', 'university','department','name']]
illinois.columns = ['index', 'university','field','name']

data = pd.concat([uc,texas,michigan,illinois])
data['field'] = data['field'].astype(str)
data['name'] = data['name'].apply(lambda x: x.split(' '))
data['name'] = data['name'].apply(lambda x: [e for e in x if len(e.replace('.',''))>1])
data['name'] = data['name'].apply(lambda x: (' ').join(x))
data = data.drop_duplicates().reset_index()
data.to_csv('ok.csv', index=False)

index = pickle.load(open("index.p",'rb'))
data = data[index+1:]

pytrends = TrendReq(hl='en-US',tz=360)

try:
    trends = pd.read_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/google_trends.csv')
except:
    trends = pd.DataFrame()

##### Semantic Similarity
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
def semantic_similarity(embed, sen):
    sen = model.encode(sen)
    cosine_scores = util.pytorch_cos_sim(embed, sen)
    return float(cosine_scores[0][0])

##### Create / Set Default Anchor Bank
t = gtab.GTAB(dir_path='/Users/iggy1212 1/Desktop/Research/WageDetermination/scripts/AB')
t.set_options()
# t.set_options(pytrends_config={"geo": "", "timeframe": "2004-01-01 2021-07-01"}) 
# t.create_anchorbank()
t.set_active_gtab("google_anchorbank_geo=_timeframe=2004-01-01 2021-07-01.tsv")


# settings = initialize_VPN() 
##### Find Term / Query Anchor Bank
for index,row in data.iterrows():
    print(index)
    nq_res = pd.DataFrame()
    if row['field'] != 'nan':
        suggestions = pytrends.suggestions(row['name'])
        encode = model.encode(row['field'])
        sug_score = 0
        hi_sug = ''
        for sug in suggestions:
            if semantic_similarity(encode, sug['type']) > sug_score:
                sug_score = semantic_similarity(encode, sug['type'])
                hi_sug = sug
        if sug_score > .5:
            print(row['field'], hi_sug['type'])
            nq_res = t.new_query(hi_sug['mid'])
            if isinstance(nq_res, int) or (nq_res is None):
                nq_res = pd.DataFrame(columns=['date','max_ratio',	'max_ratio_hi',	'max_ratio_lo',	'name',	'term','index'])
                nq_res['date'] = pd.date_range(start='2004-01-01', end='2021-07-31', freq='M')
                nq_res['name'] = row['name']
                nq_res['term'] = ''
                nq_res['index'] = row['index']
                nq_res = nq_res.fillna(0)
                trends = pd.concat([trends, nq_res])
            else:
                nq_res['name'] = row['name']
                nq_res['term'] = hi_sug['mid']
                nq_res['index'] = row['index']
                nq_res = nq_res.reset_index()
                trends = pd.concat([trends, nq_res])
    if nq_res.empty:
        nq_res = t.new_query(row['name'])
        if isinstance(nq_res, int) or (nq_res is None):
            nq_res = pd.DataFrame(columns=['date','max_ratio',	'max_ratio_hi',	'max_ratio_lo',	'name',	'term','index'])
            nq_res['date'] = pd.date_range(start='2004-01-01', end='2021-07-31', freq='M')
            nq_res['name'] = row['name']
            nq_res['term'] = ''
            nq_res['index'] = row['index']
            nq_res = nq_res.fillna(0)
            trends = pd.concat([trends, nq_res])
        else:
            nq_res['name'] = row['name']
            nq_res['term'] = ''
            nq_res['index'] = row['index']
            nq_res = nq_res.reset_index()
            trends = pd.concat([trends, nq_res])
    
    pickle.dump(index, open("index.p", "wb" ))
    
    trends = trends.drop_duplicates()
    trends.to_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/google_trends.csv', index=False)

