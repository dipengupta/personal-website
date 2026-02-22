from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase


class ContactPageTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_uses_cached_tweets_without_fetch(self):
        cached = [{"id": "1", "text": "a"}, {"id": "2", "text": "b"}]
        cache.set("x_recent_tweets_daily_20swithepennguy", cached, timeout=60)
        cache.set(
            "x_recent_tweets_daily_meta_20swithepennguy",
            {"next_refresh_at": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()},
            timeout=60,
        )

        with patch("mysite.views._fetch_recent_tweets") as fetch_mock, patch(
            "mysite.views.random.sample", side_effect=lambda seq, k: list(seq)[:k]
        ):
            response = self.client.get("/contact/")

        self.assertEqual(response.status_code, 200)
        fetch_mock.assert_not_called()
        self.assertEqual(len(response.context["tweets"]), 2)
        self.assertIn("refreshes daily", response.context["tweet_notice"])

    def test_fetches_and_caches_when_cache_empty(self):
        fetched = [
            {"id": "1", "text": "a"},
            {"id": "2", "text": "b"},
            {"id": "3", "text": "c"},
            {"id": "4", "text": "d"},
        ]
        with patch("mysite.views._fetch_recent_tweets", return_value=(fetched, "")) as fetch_mock, patch(
            "mysite.views.random.sample", side_effect=lambda seq, k: list(seq)[:k]
        ):
            response = self.client.get("/contact/")

        self.assertEqual(response.status_code, 200)
        fetch_mock.assert_called_once()
        self.assertEqual(len(response.context["tweets"]), 3)
        self.assertEqual(cache.get("x_recent_tweets_daily_20swithepennguy"), fetched)
        self.assertFalse(response.context["tweet_error"])

    def test_respects_retry_after_and_uses_last_good_cache(self):
        retry_after = datetime.now(timezone.utc) + timedelta(minutes=30)
        last_good = [{"id": "9", "text": "last-good"}]
        cache.set(
            "x_recent_tweets_daily_meta_20swithepennguy",
            {"retry_after": retry_after.isoformat()},
            timeout=60,
        )
        cache.set("x_recent_tweets_last_good_20swithepennguy", last_good, timeout=60)

        with patch("mysite.views._fetch_recent_tweets") as fetch_mock, patch(
            "mysite.views.random.sample", side_effect=lambda seq, k: list(seq)[:k]
        ):
            response = self.client.get("/contact/")

        fetch_mock.assert_not_called()
        self.assertEqual(response.context["tweets"], last_good)
        self.assertIn("cached tweets", response.context["tweet_notice"])

    def test_rate_limit_fetch_failure_sets_fallback_notice(self):
        with patch(
            "mysite.views._fetch_recent_tweets",
            return_value=([], "Rate limit hit (429). Please retry in ~15 minutes."),
        ), patch("mysite.views.random.sample", side_effect=lambda seq, k: list(seq)[:k]):
            response = self.client.get("/contact/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tweets"], [])
        self.assertEqual(response.context["tweet_error"], "")
        self.assertIn("rate-limited", response.context["tweet_notice"])

    def test_contact_page_renders_without_map_room_link(self):
        with patch("mysite.views._fetch_recent_tweets", return_value=([], "")):
            response = self.client.get("/contact/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'href="/explore/"')
