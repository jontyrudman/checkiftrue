import tweepy

def get_auth():
    consumer_key = 'XXXX' 
    consumer_secret = 'XXXX' 
    access_token = 'XXX' 
    access_token_secret = 'XXXX'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return auth
