import io
import json
from urllib import error
from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from mysite.views import _fetch_recent_tweets


class _FakeHTTPResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TwitterFetchTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    @override_settings(TWITTER_BEARER_TOKEN="")
    def test_missing_bearer_token_returns_error(self):
        tweets, err = _fetch_recent_tweets("user")
        self.assertEqual(tweets, [])
        self.assertIn("Missing TWITTER_BEARER_TOKEN", err)

    @override_settings(TWITTER_BEARER_TOKEN="token", TWITTER_USER_ID="12345")
    def test_uses_configured_user_id_and_parses_tweets(self):
        tweets_payload = {
            "data": [
                {"id": "11", "text": "hello", "created_at": "2025-02-15T00:00:00Z"},
                {"id": "", "text": "skip"},
                {"id": "12"},
            ]
        }
        with patch("mysite.views.urlrequest.urlopen", return_value=_FakeHTTPResponse(tweets_payload)) as urlopen_mock:
            tweets, err = _fetch_recent_tweets("alice", max_results=5)

        self.assertEqual(err, "")
        self.assertEqual(len(tweets), 1)
        self.assertEqual(tweets[0]["id"], "11")
        self.assertEqual(tweets[0]["url"], "https://x.com/alice/status/11")
        self.assertEqual(urlopen_mock.call_count, 1)
        request_obj = urlopen_mock.call_args.args[0]
        self.assertIn("/2/users/12345/tweets?", request_obj.full_url)
        self.assertIn("max_results=5", request_obj.full_url)

    @override_settings(TWITTER_BEARER_TOKEN="token", TWITTER_USER_ID="12345")
    def test_rate_limited_tweet_fetch_returns_429_message(self):
        http_err = error.HTTPError(
            url="https://api.x.com/2/users/12345/tweets",
            code=429,
            msg="Too Many Requests",
            hdrs=None,
            fp=io.BytesIO(b'{"title":"Too Many Requests"}'),
        )
        with patch("mysite.views.urlrequest.urlopen", side_effect=http_err):
            tweets, err = _fetch_recent_tweets("alice")

        self.assertEqual(tweets, [])
        self.assertIn("Rate limit hit (429)", err)

    @override_settings(TWITTER_BEARER_TOKEN="token", TWITTER_USER_ID="")
    def test_username_lookup_http_error_returns_message(self):
        http_err = error.HTTPError(
            url="https://api.x.com/2/users/by/username/alice",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b"{}"),
        )
        with patch("mysite.views.urlrequest.urlopen", side_effect=http_err):
            tweets, err = _fetch_recent_tweets("alice")

        self.assertEqual(tweets, [])
        self.assertIn("User lookup failed (403)", err)

    @override_settings(
        TWITTER_BEARER_TOKEN="token",
        TWITTER_USER_ID="",
        TWITTER_ACCESS_TOKEN="77777-suffix",
    )
    def test_uses_numeric_access_token_prefix_as_user_id(self):
        with patch(
            "mysite.views.urlrequest.urlopen",
            return_value=_FakeHTTPResponse({"data": [{"id": "1", "text": "ok"}]}),
        ) as urlopen_mock:
            tweets, err = _fetch_recent_tweets("bob")

        self.assertEqual(err, "")
        self.assertEqual(len(tweets), 1)
        request_obj = urlopen_mock.call_args.args[0]
        self.assertIn("/2/users/77777/tweets?", request_obj.full_url)

