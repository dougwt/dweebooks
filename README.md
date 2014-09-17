# dweebooks
A simple twitter bot that tweets at regular intervals and responds to mentions. All tweets are pseudorandom text based on Markov chains of archived tweets.

- [Requirements](#requirements)
- [Setup](#setup)
- [Configuration](#configuration)
    - [config.sample.json](#configsamplejson)
    - [API Keys](#api-keys)
        - [CONSUMER_SECRET](#consumer_secret)
        - [CONSUMER_KEY](#consumer_key)
        - [ACCESS_TOKEN](#access_token)
        - [ACCESS\_TOKEN_SECRET](#access\_token_secret)
    - [Options](#options)
        - [ARCHIVE_PATH](#archive_path)
        - [DELAY](#delay)
        - [URL_TOKENS](#url_tokens)
        - [USERNAME_TOKENS](#username_tokens)
- [Demo](#demo)

## Requirements

* Python 2.x
* [tweepy](http://www.tweepy.org), the easy-to-use Python library for accessing the Twitter API

## Setup

1. Replace the `data` subdirectory with the contents of your Twitter archive, which may be downloaded from the [Twitter settings](https://twitter.com/settings/account) page.
2. Create a `config.json` file containing your Twitter API keys.
3. Run `dweebooks.py`

## Configuration

Before dweebooks can connect to twitter successfully, some configuration values must be set in `config.json`. A [sample configuration](config.sample.json) is provided for your convenience. 

### config.sample.json

    {
        "CONSUMER_KEY"          : "",
        "CONSUMER_SECRET"       : "",
        "ACCESS_TOKEN"          : "",
        "ACCESS_TOKEN_SECRET"   : "",
        "ARCHIVE_PATH"          : "./data/js/tweets/*.js",
        "DELAY"                 : 60,
        "URL_TOKENS"            : true,
        "USERNAME_TOKENS"       : false
    }

### API Keys

The following API keys are provided by Twitter when creating a [Twitter App](http://apps.twitter.com). ***Reminder:** Secret keys allow access to your twitter account and should be kept secret. Don't publish them!*

##### CONSUMER_SECRET

This should be the string listed as `API key` under Application settings on the API Keys tab of the Twitter Apps website.

##### CONSUMER_KEY

This should be the string listed as `API secret` under Application settings on the API Keys tab of the Twitter Apps website.

##### ACCESS_TOKEN

This should be the string listed as `Access token` under Your access tokens on the API Keys tab of the Twitter Apps website.

##### ACCESS\_TOKEN_SECRET

This should be the string listed as `Access token secret` under Your access tokens on the API Keys tab of the Twitter Apps website.

### Options

The following configuration options are also specified within the configuration file:

##### ARCHIVE_PATH

The path to scan for JSON files extracted from your [Twitter Archive](## Instructions).

*Recommended:* `./data/js/tweets/*.js`

##### DELAY

The number of minutes to wait between tweets (excluding replies).

##### URL_TOKENS

This boolean option controls whether or not previously tweeted URLs contained within the scanned archive should be included when generating new tweets.

- `true`: include URLs
- `false`: don't include URLs

##### USERNAME_TOKENS

This boolean option controls whether or not previously tweeted usernames contained within the scanned archive should be included when generating new tweets.

- `true`: include usernames
- `false`: don't include usernames

## Demo

A live demo of dweebooks can be interacted with on twitter at [@dougwt_ebooks](https://twitter.com/dougwt_ebooks).
