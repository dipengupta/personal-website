import tweepy
import random
from django.conf import settings
from django.shortcuts import render
from django.core.cache import cache
from datetime import datetime

def displayHomePage(request):

    masterDict = {
        'key' : 'value'
    }

    return render(request, 'mysite/home.html', masterDict)


def displayProfessionalPage(request):
    return render(request, 'mysite/sect_professional.html')

def displayAcademicPage(request):
    return render(request, 'mysite/sect_academic.html')

def displayMusicPage(request):
    return render(request, 'mysite/sect_music.html')

def displayArticlesPage(request):
    return render(request, 'mysite/sect_articles.html')

def displayArticleDetail(request, article_name):
    try:
        return render(request, f'mysite/../articles/{article_name}.html')
    except TemplateDoesNotExist:
        raise Http404("Article not found.")

def displayContactPage(request):

    concerts_seen = {
        "2010/2011": ["Karnivool", "Asha Bhosle", "Katatonia", "Junkyard Groove", "The Raghu Dixit Project"],
        "2012": ["Guns N' Roses", "Simple Plan", "Thermal and a Quarter"],
        "2013": ["Baiju Dharmajan Syndicate", "Neal Morse with Mike Portnoy"],
        "2014": ["The F-16's", "Epica"],
        "2015": ["Thermal and a Quarter", "Slash with Myles Kennedy!!"],
        "2016": ["Indian Jam Project", "The Local Train (Twice)", "The Aristocrats", "Skrat", "Crown the Empire"],
        "2017": ["When Chai Met Toast", "Lagori", "YouTube Fan Fest", "Abhishek Gurung Collective", "Dream Theater", "Sparsh", "The F-16's", "Haken"],
        "2018": ["The Local Train", "Amit Trivedi & Others", "The Raghu Dixit Project", "The Local Train", "My HRC Gig"],
        "2019": ["Soulmate", "TheBasementSessions", "The Local Train", "Rhythm Shaw ft. others", "Soulmate", "The Local Train"],
        "2020": ["lol"],
        "2021": ["John Mayer live on IG :)"],
        "2022": ["John Mayer", "Josh Radnor", "Mike Dawes live on IG :)"],
        "2023": ["Khalid and Ed Sheeran", "Guns N' Roses and The Pretenders", "Eric Johnson", "Babish (Book Tour)", "Periphery and Mike Dawes", "Plini"],
        "2024": ["Cory Wong", "Juice", "SOJA and Arise Roots", "Slash", "Steel Panther", "Coheed and Cambria", "Green Day and Smashing Pumpkins", "coolcoolcool", "Grateful Dead cover show"],
        "2025": ["Buckethead"],
    }

    return render(request, 'mysite/sect_contact.html', {'collections': concerts_seen})

def handlerView404(request):
    return render(request, 'mysite/404_handler.html')


def penn_guy_tweets(request):
    # Try to get the tweets from the cache
    tweets = cache.get('penn_guy_tweet')

    if tweets is None:
        # Initialize Tweepy client for Twitter API v2
        client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )

        # Get user details for the account
        user_response = client.get_user(username="20swithepennguy")
        if user_response.data:
            user_id = user_response.data.id

            # Fetch up to 5 recent tweets to allow random selection
            tweets_response = client.get_users_tweets(
                id=user_id,
                max_results=5,
                tweet_fields=['created_at', 'text']
            )
            raw_tweets = tweets_response.data if tweets_response.data else []

            # Convert Tweepy tweet objects to a list of dictionaries.
            # Store created_at as an ISO string for caching.
            tweets = [
                {"text": tweet.text, "created_at": tweet.created_at.isoformat()}
                for tweet in raw_tweets
            ]
        else:
            tweets = []

        # Cache the processed tweets
        cache.set('penn_guy_tweet', tweets, timeout=100000)
    else:
        # Convert the created_at from ISO format string to datetime object
        # so the Django date filter can format it correctly.
        for tweet in tweets:
            if isinstance(tweet.get("created_at"), str):
                tweet["created_at"] = datetime.fromisoformat(tweet["created_at"])

    # Pass the tweets to the template context
    context = {"tweets": tweets}
    print(context)
    return render(request, "mysite/sect_tweets.html", context)

def tinker(request):
    tweet = cache.get('penn_guy_tweet')

    if tweet is None:
        # Initialize Tweepy client for Twitter API v2
        client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )

        # Get user details for the account
        user_response = client.get_user(username="20swithepennguy")

        if user_response.data:

            print("We got user_response")
            print(user_response.data)

            user_id = user_response.data.id

            print("before tweets_response")
            # Fetch up to 5 recent tweets to allow random selection
            tweets_response = client.get_users_tweets(
                id=user_id,
                max_results=5,
                tweet_fields=['created_at', 'text']
            )

            print("after tweets_response")

            tweets = tweets_response.data if tweets_response.data else []

            print("We got tweets_response")
            print(tweets_response.data)

            if tweets:
                # Randomly choose one tweet from the list
                tweet = random.choice(tweets)
            else:
                tweet = None
        else:
            tweet = None

        # Cache the selected tweet for 5 minutes (300 seconds)
        cache.set('penn_guy_tweet', tweet, timeout=300)

    # Pass the tweet to the template context
    context = {"tweets": tweet}

    return context