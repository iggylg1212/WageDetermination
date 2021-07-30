import requests
import os
import json
import pandas as pd

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")

def create_url(users='', user=True, next_token='', start_time=''):
    if user:
        usernames = f"usernames={users}"
        user_fields = "user.fields=created_at,public_metrics,location"
        url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
    else: 
        tweet_fields = 'tweet.fields=public_metrics,created_at'
        start_time = f'&start_time={start_time}'
        if next_token == '':
            url = 'https://api.twitter.com/2/users/{}/tweets?{}&expansions=author_id&max_results=100{}'.format(users,tweet_fields,start_time)
        else:
            next_token = f'pagination_token={next_token}'
            url = 'https://api.twitter.com/2/users/{}/tweets?{}&expansions=author_id&max_results=100&{}{}'.format(users,tweet_fields, next_token,start_time)

    return url

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    # r.headers["User-Agent"] = "v2UserLookupPython"
    return r

def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth,)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def main():
    df = pd.DataFrame(columns=['name','username','location','id','acct_created_at','followers_count','following_count','tweet_count','listed_count','text','created_at','retweet_count','reply_count','like_count','quote_count'])

    url = create_url(users='m_urquiola')
    json_response = connect_to_endpoint(url)
    name = json_response['data'][0]['name']
    username = json_response['data'][0]['username']
    try:
        location = json_response['data'][0]['location']
    except:
        location = ''
    id = json_response['data'][0]['id']
    acct_created_at = json_response['data'][0]['created_at']
    followers_count = json_response['data'][0]['public_metrics']['followers_count']
    following_count = json_response['data'][0]['public_metrics']['following_count']
    tweet_count = json_response['data'][0]['public_metrics']['tweet_count']
    listed_count = json_response['data'][0]['public_metrics']['listed_count']
    print(tweet_count)

    url = create_url(users=id, user=False, start_time = acct_created_at)
    json_response = connect_to_endpoint(url)
    for i in range(0,len(json_response['data'])):
        text = json_response['data'][i]['text']
        created_at = json_response['data'][i]['created_at']
        retweet_count = json_response['data'][i]['public_metrics']['retweet_count']
        reply_count = json_response['data'][i]['public_metrics']['reply_count']
        like_count = json_response['data'][i]['public_metrics']['like_count']
        quote_count = json_response['data'][i]['public_metrics']['like_count']

        row = [name,username,location,id,acct_created_at,followers_count,following_count,tweet_count,listed_count,text,created_at,retweet_count,reply_count,like_count,quote_count]
        row = pd.Series(row, index = df.columns)
        df = df.append(row, ignore_index=True)
    
    try: 
        next_token = json_response['meta']['next_token']
    except:
        next_token = ''
    
    while next_token != '':
        url = create_url(users=id, user=False, next_token=next_token, start_time= acct_created_at)
        json_response = connect_to_endpoint(url)
        for i in range(0,len(json_response['data'])):
            text = json_response['data'][i]['text']
            created_at = json_response['data'][i]['created_at']
            retweet_count = json_response['data'][i]['public_metrics']['retweet_count']
            reply_count = json_response['data'][i]['public_metrics']['reply_count']
            like_count = json_response['data'][i]['public_metrics']['like_count']
            quote_count = json_response['data'][i]['public_metrics']['like_count']

            row = [name,username,location,id,acct_created_at,followers_count,following_count,tweet_count,listed_count,text,created_at,retweet_count,reply_count,like_count,quote_count]
            row = pd.Series(row, index = df.columns)
            df = df.append(row, ignore_index=True)
        
        try: 
            next_token = json_response['meta']['next_token']
        except:
            next_token = ''

    return df

if __name__ == "__main__":
    df = main().drop_duplicates()
    df.to_csv('/Users/iggy1212 1/Desktop/Research/WageDetermination/outputs/twitter_timeline.csv')
    print(df)