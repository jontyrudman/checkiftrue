from os import environ
import tweepy
import requests
import urllib
import re


URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
TRIGGER = "@checkiftrue"


CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']
FACT_CHECK_KEY = environ['FACT_CHECK_KEY']


def get_twitter_auth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    return auth


# override tweepy.StreamListener to add logic to on_status
class IncomingTweetStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if not hasattr(status, 'retweeted_status'):
            process_tweet(status)

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False


def process_tweet(tweet):
    print("Processing tweet from " + tweet.user.screen_name +
          " containing text:\n\"" + tweet.text + "\"")
    text = re.sub(r'@\w+', '', tweet.text).strip()
    print("After removing handles: \"" + text + "\"")
    if text.startswith("claim:"):
        query = text.replace("claim:", '')
        follow_up = str("For more sources, head to " +
                        "https://toolbox.google.com/factcheck" +
                        "/explorer/search/" +
                        urllib.parse.quote(query) + ";hl=")
        reply = check_claim(query)
        if reply is None:
            reply = "No claims found on Google Fact Check"
            respond(reply, tweet)
            return
        respond(reply, tweet, follow_up)


def respond(reply, orig_tweet, follow_up=None):
    reply = str("@" + orig_tweet.user.screen_name + " " +
                reply)
    print("Responding to " + orig_tweet.id_str + " with \"" + reply + "\"")
    reply_status = api.update_status(status=reply,
                                     in_reply_to_status_id=orig_tweet.id_str)
    if follow_up is None:
        return

    follow_up = str("@" + orig_tweet.user.screen_name + " " +
                    follow_up)
    print("Following up " + reply_status.id_str + " with \"" +
          follow_up + "\"")
    api.update_status(status=follow_up,
                      in_reply_to_status_id=reply_status.id_str)


def check_claim(query):
    response = requests.get(URL, params={'key': FACT_CHECK_KEY,
                                         'query': query})
    try:
        claims = response.json()["claims"]
        claim = claims[0]
        publisher = f"{claim['claimReview'][0]['publisher']['name']}"
        rating = f"{claim['claimReview'][0]['textualRating']}"
        claim_text = f"{claim['text']}"
        if "claimant" in claim:
            claimant = f"{claim['claimant']}"
            result = str(publisher + " rates the following claim from " +
                         claimant + " as \"" + rating + "\":\n" +
                         "\"" + claim_text + "\"")
        else:
            result = str(publisher + " rates the following claim as \"" +
                         rating + "\":\n" + "\"" + claim_text + "\"")
    except KeyError:
        return None
    if len(result) > 280:
        return result[:177] + "..."
    return result


api = tweepy.API(get_twitter_auth())
streamListener = IncomingTweetStreamListener()
stream = tweepy.Stream(auth=api.auth, listener=streamListener)
stream.filter(track=[TRIGGER], is_async=True)
