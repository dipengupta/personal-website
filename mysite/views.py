import json
import logging
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib import error, parse, request as urlrequest

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.core.cache import cache
from django.template import TemplateDoesNotExist
from .travel_data import travel_page_context

logger = logging.getLogger(__name__)

def _parse_utc_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _next_daily_refresh_utc(now_utc, refresh_hour_utc):
    next_refresh = now_utc.replace(
        hour=refresh_hour_utc, minute=0, second=0, microsecond=0
    )
    if now_utc >= next_refresh:
        next_refresh += timedelta(days=1)
    return next_refresh


def _fetch_recent_tweets(username, max_results=30):
    """
    Fetch recent tweets for a username via X/Twitter API v2.
    Returns (tweets, error_message).
    """
    bearer_token = getattr(settings, "TWITTER_BEARER_TOKEN", "")
    if not bearer_token:
        return [], "Missing TWITTER_BEARER_TOKEN in settings."

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "personal-site-contact-page",
    }

    # Avoid the username lookup endpoint when possible (it is commonly rate-limited).
    # Priority:
    # 1) explicit TWITTER_USER_ID
    # 2) cached id from a prior lookup
    # 3) numeric prefix of TWITTER_ACCESS_TOKEN
    # 4) username lookup (last resort)
    user_id = getattr(settings, "TWITTER_USER_ID", "")
    if not user_id:
        user_id = cache.get(f"x_user_id_{username}") or ""

    if not user_id:
        access_token = getattr(settings, "TWITTER_ACCESS_TOKEN", "")
        if "-" in access_token:
            token_prefix = access_token.split("-", 1)[0]
            if token_prefix.isdigit():
                user_id = token_prefix

    if not user_id:
        user_lookup_url = (
            f"https://api.x.com/2/users/by/username/{username}"
            "?user.fields=id"
        )
        user_req = urlrequest.Request(user_lookup_url, headers=headers)

        try:
            with urlrequest.urlopen(user_req, timeout=8) as response:
                user_payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            logger.warning("User lookup failed (%s): %s", exc.code, body)
            return [], f"User lookup failed ({exc.code})."
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            logger.warning("User lookup failed: %s", exc)
            return [], "User lookup request failed."

        user_data = user_payload.get("data") or {}
        user_id = user_data.get("id")
        if user_id:
            cache.set(f"x_user_id_{username}", user_id, timeout=60 * 60 * 24 * 30)

    if not user_id:
        return [], "Could not resolve the X account."

    query = parse.urlencode(
        {
            "max_results": max_results,
            "tweet.fields": "created_at",
            "exclude": "retweets,replies",
        }
    )
    tweets_url = f"https://api.x.com/2/users/{user_id}/tweets?{query}"
    tweets_req = urlrequest.Request(tweets_url, headers=headers)

    try:
        with urlrequest.urlopen(tweets_req, timeout=8) as response:
            tweets_payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        logger.warning("Tweet fetch failed (%s): %s", exc.code, body)
        if exc.code == 429:
            return [], "Rate limit hit (429). Please retry in ~15 minutes."
        return [], f"Tweet fetch failed ({exc.code})."
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("Tweet fetch failed: %s", exc)
        return [], "Tweet fetch request failed."

    tweets_data = tweets_payload.get("data") or []
    tweets = []
    for tweet in tweets_data:
        tweet_id = tweet.get("id")
        text = tweet.get("text")
        if not tweet_id or not text:
            continue
        tweets.append(
            {
                "id": tweet_id,
                "text": text,
                "created_at": tweet.get("created_at"),
                "url": f"https://x.com/{username}/status/{tweet_id}",
            }
        )

    return tweets, ""

def displayHomePage(request):
    home_image_dir = Path(settings.BASE_DIR) / "mysite" / "static" / "images" / "home"
    allowed_exts = {".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP"}
    home_images = []

    if home_image_dir.exists():
        for image_path in sorted(home_image_dir.iterdir()):
            if not image_path.is_file() or image_path.name.startswith("."):
                continue
            if image_path.suffix not in allowed_exts:
                continue

            display_name = image_path.stem.replace("_", " ").replace("-", " ").strip()
            alt_text = f"Dipen photo - {display_name}" if display_name else "Dipen profile photo"
            home_images.append(
                {
                    "static_path": f"images/home/{image_path.name}",
                    "alt": alt_text,
                }
            )

    random.shuffle(home_images)

    masterDict = {
        "home_images": home_images,
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
        "2025": ["Buckethead", "Periphery"],
    }

    username = "20swithepennguy"
    cache_key = f"x_recent_tweets_daily_{username}"
    meta_cache_key = f"x_recent_tweets_daily_meta_{username}"
    last_good_cache_key = f"x_recent_tweets_last_good_{username}"
    refresh_hour_utc = int(getattr(settings, "TWEET_CACHE_REFRESH_HOUR_UTC", 7))
    refresh_hour_utc = min(max(refresh_hour_utc, 0), 23)

    recent_tweets = cache.get(cache_key) or []
    cache_meta = cache.get(meta_cache_key) or {}
    next_refresh_at = _parse_utc_iso(cache_meta.get("next_refresh_at"))
    retry_after = _parse_utc_iso(cache_meta.get("retry_after"))
    now_utc = datetime.now(timezone.utc)

    tweet_error = ""
    tweet_notice = ""

    should_refresh = False
    if not recent_tweets:
        should_refresh = True
    elif next_refresh_at and now_utc >= next_refresh_at:
        should_refresh = True

    if retry_after and now_utc < retry_after:
        should_refresh = False

    if should_refresh:
        fetched_tweets, tweet_error = _fetch_recent_tweets(username=username, max_results=100)
        if fetched_tweets:
            recent_tweets = fetched_tweets
            next_refresh_at = _next_daily_refresh_utc(now_utc, refresh_hour_utc)
            cache.set(cache_key, recent_tweets, timeout=60 * 60 * 24 * 8)
            cache.set(last_good_cache_key, recent_tweets, timeout=60 * 60 * 24 * 30)
            cache.set(
                meta_cache_key,
                {"next_refresh_at": next_refresh_at.isoformat(), "retry_after": ""},
                timeout=60 * 60 * 24 * 8,
            )
            tweet_notice = (
                f"Tweet pool is cached and refreshes daily around {refresh_hour_utc:02d}:00 UTC."
            )
        else:
            retry_after = now_utc + timedelta(hours=1)
            if not next_refresh_at:
                next_refresh_at = _next_daily_refresh_utc(now_utc, refresh_hour_utc)
            cache.set(
                meta_cache_key,
                {
                    "next_refresh_at": next_refresh_at.isoformat(),
                    "retry_after": retry_after.isoformat(),
                },
                timeout=60 * 60 * 24 * 8,
            )
            if "429" in tweet_error:
                tweet_notice = "Live tweet fetch is temporarily rate-limited. Showing fallback timeline."
                tweet_error = ""
            elif not recent_tweets and not tweet_error:
                tweet_notice = "No cached tweets yet. Showing fallback timeline for now."

    if not recent_tweets:
        stale_tweets = cache.get(last_good_cache_key) or []
        if stale_tweets:
            recent_tweets = stale_tweets
            tweet_notice = "Showing cached tweets while the next refresh is pending."

    if recent_tweets and not tweet_notice:
        tweet_notice = (
            f"Tweet pool is cached and refreshes daily around {refresh_hour_utc:02d}:00 UTC."
        )
    elif not recent_tweets and retry_after and now_utc < retry_after and not tweet_notice:
        tweet_notice = "Tweet cache is warming up. Showing fallback timeline for now."

    tweets_to_show = []
    if recent_tweets:
        tweets_to_show = random.sample(recent_tweets, k=min(3, len(recent_tweets)))

    return render(
        request,
        'mysite/sect_contact.html',
        {
            'collections': concerts_seen,
            'tweets': tweets_to_show,
            'tweet_username': username,
            'tweet_error': tweet_error,
            'tweet_notice': tweet_notice,
        }
    )


def displayTravelsPage(request):
    return render(request, "mysite/sect_travels.html", travel_page_context())

def handlerView404(request):
    return render(request, 'mysite/404_handler.html', status=404)
