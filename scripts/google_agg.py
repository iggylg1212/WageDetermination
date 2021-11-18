import pandas as pd

trends = pd.read_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/google_trends.csv', low_memory=False)
trends = trends.drop(columns='index')
trends['date'] = pd.to_datetime(trends['date'])

year = trends.groupby(by = [trends['date'].map(lambda x: x.year), trends['name']]).agg(
    {'max_ratio': 'mean', 'max_ratio_hi': 'mean', 'max_ratio_lo': 'mean', 'term': lambda x: x.iloc[0]}).reset_index()

year.to_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/google_cal_year.csv', index=False)

ac_year = trends.groupby(by = [trends['date'].map(lambda x: pd.Period(x, freq='Q-JUL').qyear), trends['name']]).agg(
    {'max_ratio': 'mean', 'max_ratio_hi': 'mean', 'max_ratio_lo': 'mean', 'term': lambda x: x.iloc[0]}).reset_index()

ac_year.to_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/google_ac_year.csv', index=False)
