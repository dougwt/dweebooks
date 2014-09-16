#!/usr/bin/python
"""
A simple twitter bot that tweets at regular intervals and responds to mentions.

Tweets are generated using markov chains based on previous tweets.
"""
import datetime
import glob
import json
import logging
import sys
import time
from random import choice

import tweepy


class Dweebooks:
    """Twitter bot that tweets at regular intervals & responds to mentions."""
    def __init__(self, files):
        self.EOS = ['.', '?', '!']
        self.delay = 60 * 60
        self.most_recent_response_id = None
        self.tweets = {}
        self.dictionary = {}
        self.seeds = []
        self.load_data(files)
        self.build_dict()

        # TODO: add support for config files
        CONSUMER_KEY = 'JBBZYreWlks6WaUGGu46JNpnP'
        CONSUMER_SECRET = 'Yl4RROho8rKT7Y1axBjDO8Ot2DR3FiBSUDVbOoWz8ydC5YsIna'
        ACCESS_TOKEN = '2647029398-y6m8U3jgPyRLq4xl4xq4GgWku4IeeFpFLwhM7e0'
        ACCESS_TOKEN_SECRET = '10nEzYXsMmCcMjPEpjuxlWetTGBDxcv2z6PrJHik4iRCW'
        self.URL_TOKENS = True
        self.USERNAME_TOKENS = False

        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.username = self.auth.get_username()
        self.api = tweepy.API(self.auth)
        self.listener = None
        self.stream = None

        logging.basicConfig(filename=self.username+'.log', level=logging.DEBUG)

        self.log('Available seeds: %s' % len(self.seeds))

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
        self.log('Found tweets: %s' % len(self.tweets))

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
                # self.log('Adding seed: (%s, %s)' % (first, second))
            except IndexError:
                # self.log('Error analyzing seed: %s' % temp_tokens)
                pass

            # self.log('Adding tokens: %s' % temp_tokens)
        self.log('Usable tweets: %s' % len(tokens))
        return tokens

    def valid_token(self, token):
        """Determine whether a token should be placed in the dictionary."""
        # Filter urls
        if not self.URL_TOKENS and token.lower().startswith(u'http'):
            # self.log('Rejected token: %s' % token) TODO: debug log
            return False

        # Filter mentions
        if not self.USERNAME_TOKENS and u'@' in token:
            # self.log('Rejected token: %s' % token) TODO: debug log
            return False

        return True

    def strip_token(self, token):
        """Remove unwanted characters from an individual token."""
        if token.startswith(u'"') or token.startswith(u"'") or token.startswith(u'('):
            # self.log('Stripped token: %s' % token)
            token = token[1:]
        if token.endswith(u'"') or token.endswith(u"'") or token.endswith(u')'):
            # self.log('Stripped token: %s' % token)
            token = token[:-1]
        return token

    def generate_tweet(self, max_length=140):
        """Generate pseudorandom tweets with a maximum length."""
        new_tweet = ''
        while True:
            if len(new_tweet) < 25:            # tweet too short; extend it
                if len(new_tweet) > 0:
                    new_tweet += ' '  # add space prefix for next substring
                new_tweet += self.generate_markov_string()
            elif len(new_tweet) > max_length:  # tweet too long; start over

                new_tweet = self.generate_markov_string()
            else:                              # acceptable-length tweet found
                break
        return new_tweet

    def generate_markov_string(self):
        """Generate a string based on the markov dictionary."""
        # Choose a random key to start the chain
        li = [key for key in self.dictionary.keys()]
        key = choice(li)

        # Add the chosen key and its successor to the string
        first, second = key
        li.append(first)
        li.append(second)

        while True:
            # lookup current key in dictionary
            try:
                third = choice(self.dictionary[key])
            except KeyError:
                # no successor found
                # we've reached the end of this markov chain
                break

            # successor found, append and check for End-of-String symbols
            li.append(third)
            if len(third) < 1 or third[-1] in self.EOS:
                break

            # advance key to the next pair of tokens for the next loop
            key = (second, third)
            first, second = key

        return ' '.join(li)

    def process_mention(self, status):
        """Reply to a mention status."""
        # don't respond to tweets made by our own account
        if status.user.screen_name == self.username:
            return True

        self.log('Stream detected mention: ' + status.text)

        # prefix response with mention's username
        new_tweet = '@%s ' % status.user.screen_name

        # add any additional usernames mentioned in the tweet
        for user in status.entities['user_mentions']:
            if user['screen_name'] != self.username:  # don't include ourselves
                new_tweet += '@%s ' % user['screen_name']

        # generate the response text
        new_tweet += self.generate_tweet(max_length=(140 - len(new_tweet)))

        # make it happen, cap'n
        self.api.update_status(new_tweet, status.id)
        self.log('Tweeting: %s' % new_tweet)

    def start(self):
        """Start dweebooks bot."""
        self.log('Starting dweebooks...')

        # Setup async StreamListener to monitor mentions
        self.listener = MentionListener(self)
        self.stream = tweepy.Stream(self.auth, self.listener)
        self.stream.userstream(_with='user', replies='all', async=True)

        while True:
            new_tweet = self.generate_tweet()      # generate tweet text
            self.api.update_status(new_tweet)      # publish tweet
            self.log('Tweeting: %s' % new_tweet)   # update log

            time.sleep(self.delay)                 # sleep until next tweet

    def log(self, msg):
        """Write a message to the dweebooks log."""
        timestamp = datetime.datetime.fromtimestamp(
            time.time()).strftime('%Y-%m-%d %H:%M:%S')

        print u'[%s] %s' % (timestamp, msg)
        sys.stdout.flush()


class MentionListener(tweepy.StreamListener):
    ''' Handles data received from the stream. '''
    def __init__(self, bot, *args, **kwargs):
        super(MentionListener, self).__init__(*args, **kwargs)
        self.bot = bot

    def on_status(self, status):
        self.bot.process_mention(status)

        return True  # To continue listening

    def on_error(self, status_code):
        self.bot.log('Got an error with status code: ' + str(status_code))

        return True  # To continue listening

    def on_timeout(self):
        self.bot.log('Timeout...')

        return True  # To continue listening

    def on_friends(self, friends):
        self.bot.log('Received friends list.')
        self.bot.friends = friends

        return True  # To continue listening


def main():
    bot = Dweebooks('./data/js/tweets/*.js')
    bot.start()


if __name__ == "__main__":
    main()
