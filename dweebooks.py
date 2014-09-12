import datetime
import glob
import json
import time
from random import choice

import tweepy


class Dweebooks:
    def __init__(self, files):
        self.EOS = ['.', '?', '!']
        self.delay = 60 * 60
        self.most_recent_response_id = None
        self.tweets = {}
        self.dictionary = {}
        self.seeds = []
        self.load_data(files)
        self.build_dict()

        CONSUMER_KEY = 'JBBZYreWlks6WaUGGu46JNpnP'
        CONSUMER_SECRET = 'Yl4RROho8rKT7Y1axBjDO8Ot2DR3FiBSUDVbOoWz8ydC5YsIna'
        ACCESS_TOKEN = '2647029398-y6m8U3jgPyRLq4xl4xq4GgWku4IeeFpFLwhM7e0'
        ACCESS_TOKEN_SECRET = '10nEzYXsMmCcMjPEpjuxlWetTGBDxcv2z6PrJHik4iRCW'
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)

        log('Available seeds: %s' % len(self.seeds))

    def load_data(self, files):
        """Load JSON data from tweet archives."""
        tweets = []
        files = glob.glob(files)
        for file in files:
            with open(file) as f:
                d = f.readlines()[1:]  # Twitter's JSON first line is bogus
                d = "".join(d)
                j = json.loads(d)
            for tweet in j:
                tweets.append(tweet)
        self.tweets = sorted(tweets, key=lambda k: k['id'])
        log('Found tweets: %s' % len(self.tweets))

    def build_dict(self):
        """Build a Markov chain based on a list of tokens."""
        tweet_tokens = self.list_tokens_by_tweet()
        for tweet in tweet_tokens:
            for i, token in enumerate(tweet):
                try:
                    first, second, third = tweet[i], tweet[i+1], tweet[i+2]
                except IndexError:
                    break

                key = (first, second)
                if key not in self.dictionary:
                    self.dictionary[key] = []

                self.dictionary[key].append(third)

    def list_tokens_by_tweet(self):
        """Returns a nested list of tokens making up each tweet."""
        tokens = []
        for tweet in self.tweets:
            # if len(tweet[u'entities'][u'user_mentions']) == 0:
            temp_tokens = []
            for token in tweet[u'text'].split(' '):
                if self.valid_token(token):
                    temp_tokens.append(self.strip_token(token))

            tokens.append(temp_tokens)

            try:
                first, second = temp_tokens[0], temp_tokens[1]
                self.seeds.append((first, second))
                # log('Adding seed: (%s, %s)' % (first, second))
            except IndexError:
                # log('Error analyzing seed: %s' % temp_tokens)
                pass

            # log('Adding tokens: %s' % temp_tokens)
        log('Usable tweets: %s' % len(tokens))
        return tokens

    def valid_token(self, token):
        """Determine whether a token should be placed in the dictionary."""
        # if token.lower().startswith(u'http'):
        #     log('Rejected token: %s' % token)
        #     return False
        if u'@' in token:
            # log('Rejected token: %s' % token)
            return False
        return True

    def strip_token(self, token):
        """Remove unwanted characters from an individual token."""
        if token.startswith(u'"') or token.startswith(u"'") or token.startswith(u'('):
            # log('Stripped token: %s' % token)
            token = token[1:]
        if token.endswith(u'"') or token.endswith(u"'") or token.endswith(u')'):
            # log('Stripped token: %s' % token)
            token = token[:-1]
        return token

    def generate_tweet_helper(self):
        li = [key for key in self.dictionary.keys()]
        key = choice(li)
        # key = choice(self.seeds)

        li = []
        first, second = key
        li.append(first)
        li.append(second)
        while True:
            try:
                third = choice(self.dictionary[key])
            except KeyError:
                break
            li.append(third)
            if len(third) < 1 or third[-1] in self.EOS:
                break
            # else
            key = (second, third)
            first, second = key

        return ' '.join(li)

    def generate_tweet(self, max_length=140):
        """Generate pseudorandom tweets with a maximum length."""
        new_tweet = ''
        while True:
            if len(new_tweet) < 25:
                if len(new_tweet) > 0:
                    new_tweet += ' '

                new_tweet += self.generate_tweet_helper()
            elif len(new_tweet) > max_length:
                new_tweet = self.generate_tweet_helper()
            else:
                # found acceptable length tweet
                break

        return new_tweet

    def check_mentions(self):
        """Identify new incoming mentions."""
        if self.most_recent_response_id:
            mentions = self.api.mentions(since_id=self.most_recent_response_id)
        else:
            mentions = self.api.mentions()
            self.most_recent_response_id = mentions[-1].id
            mentions = []

        for mention in mentions:
            if mention.id > self.most_recent_response_id:
                self.process_mention(mention.id)
                self.most_recent_response_id = mention.id

    def process_mention(self, id):
        """Reply to a tweet of a given id."""
        response_tweet = '@dougwt '

        length = 140 - len(response_tweet)
        response_tweet += self.generate_tweet(max_length=length)
        log('Simulated mention: %s' % response_tweet)
        # self.api.update_status(response_tweet, in_reply_to_status_id=id)

    def start(self):
        log('Starting dweebooks...')
        while True:
            # self.check_mentions()

            new_tweet = self.generate_tweet()
            self.api.update_status(new_tweet)
            log('Tweeting: %s' % new_tweet)

            time.sleep(self.delay)


def log(msg):
    timestamp = datetime.datetime.fromtimestamp(
        time.time()).strftime('%Y-%m-%d %H:%M:%S')

    print '[%s] %s' % (timestamp, msg)


def main():
    bot = Dweebooks('./data/js/tweets/*.js')
    bot.start()


if __name__ == "__main__":
    main()
