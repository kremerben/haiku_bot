import json
import random

import requests  # for local development
import sys
import time
import tweepy

from credentials import *  # use this one for testing

HAIKU_API = "https://haiku.kremer.dev"

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
tweepy_api = tweepy.API(auth)


def respond(err, res=None):
    print(res)  # adds the generated Haiku to the CloudWatch logs
    return {
        "statusCode": 400 if err else 200,
        "body": err.message if err else json.dumps(res),
        "headers": {"Content-Type": "application/json",},
    }


def lambda_handler(event, context):

    pg = HaikuBot()
    return respond(None, pg.run())


class HaikuBot:
    def __init__(self, woeid: int = 23424977):
        self.woeid = woeid
        self.trends = self.get_twitter_trends(self.woeid)

    def run(self):
        keywords = self.trends
        keyword = random.choice(
            [keyword for keyword in keywords if keyword.isalpha() and keyword[1:].islower()]
        )
        generated_haiku = self.request_haiku(keyword)
        full_haiku = self.format_haiku(keyword, generated_haiku)

        tweepy_api.update_status(" \n".join(full_haiku))
        print(" \n".join(full_haiku))

    def request_haiku(self, keyword):
        r = requests.get(HAIKU_API, {"keyword": keyword})
        return r.json()

    def parse_trends(self, full_trend):
        results = []
        if " " in full_trend:
            return full_trend.split(" ")
        # elif multiple capitals, split on those.

    def get_twitter_trends(self, woeid: int = 23424977):
        trends = tweepy_api.trends_place(woeid)
        keywords = []
        for trend in trends[0]["trends"]:
            name = trend["name"]
            if name[0] == "#":
                name = name[1:]
            keywords.append(name)
        return keywords

    def format_haiku(self, keyword, generated_haiku: list):
        return ["#" + keyword, "-" * 2 * len(keyword)] + generated_haiku


def main():
    """ To run this python script locally:
    format:  $ python3 create_tweet.py
    """

    pg = HaikuBot()
    print(pg.run())


if __name__ == "__main__":
    main()
