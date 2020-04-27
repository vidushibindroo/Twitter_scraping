from bs4 import BeautifulSoup
import requests
import sys
import json



def get_tweets(tweet):
    tweet_text_box = tweet.find("p", {"class": "TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"})
    images_in_tweet_tag = tweet_text_box.find_all("a", {"class": "twitter-timeline-link u-hidden"})
    tweet_text = tweet_text_box.text
    for image_in_tweet_tag in images_in_tweet_tag:
        tweet_text = tweet_text.replace(image_in_tweet_tag.text, '')

    return tweet_text

def current_tweet(soup):
    tweets_list = list()
    tweets = soup.find_all("li", {"data-item-type": "tweet"})
    for tweet in tweets:
        tweet_data = None
        try:
            tweet_data = get_tweets(tweet)
        except Exception as e:
            continue
          

        if tweet_data:
            tweets_list.append(tweet_data)
            print("#", end="")
            sys.stdout.flush()

    return tweets_list


def get_data(username, soup):
    tweets_list = list()
    tweets_list.extend(current_tweet(soup))

    next_ = soup.find("div", {"class": "stream-container"})["data-min-position"]

    while True:
        next_url = "https://twitter.com/i/profiles/show/" + username + \
                   "/timeline/tweets?include_available_features=1&" \
                   "include_entities=1&max_position=" + next_ + "&reset_error_state=false"

        next_response = None
        try:
            next_response = requests.get(next_url)
        except Exception as e:
            # in case there is some issue with request. None encountered so far.
            print(e)
            return tweets_list

        tweets_data = next_response.text
        tweets_obj = json.loads(tweets_data)
        if not tweets_obj["has_more_items"] and not tweets_obj["min_position"]:
            # using two checks here bcz in one case has_more_items was false but there were more items
            print("\nNo more tweets returned")
            break
        next_ = tweets_obj["min_position"]
        html = tweets_obj["items_html"]
        soup = BeautifulSoup(html, 'lxml')
        tweets_list.extend(current_tweet(soup))

    return tweets_list



def save_data(username, tweets):
    filename = username+"_twitter.json"
    print("\nSaving data in file " + filename)
    data = dict()
    data["tweets"] = tweets
    with open(filename, 'w') as fh:
        fh.write(json.dumps(data,indent= 4))

    return filename


def get_username():
    
    if len(sys.argv) < 2:
        usage()
    username = sys.argv[1].strip().lower()
    

    return username


def start(username = None):
    username = get_username()
    url = "http://www.twitter.com/" + username
    print("\n\nDownloading tweets for " + username)
    response = None
    try:
        response = requests.get(url)
    except Exception as e:
        print(repr(e))
        sys.exit(1)
    
    
    soup = BeautifulSoup(response.text, 'lxml')

    
    tweets = get_data(username, soup)
    save_data(username, tweets)
    print(str(len(tweets))+" tweets.")
    
start()
    




