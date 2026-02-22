import json
from pathlib import Path
from urllib import error, parse, request as urlrequest

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Export all tweets for an X/Twitter account to a text file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default="20swithepennguy",
            help="X/Twitter username to export (default: 20swithepennguy)",
        )
        parser.add_argument(
            "--output",
            default="",
            help="Output text file path (default: <BASE_DIR>/tweets_<username>_export.txt)",
        )
        parser.add_argument(
            "--exclude-replies",
            action="store_true",
            help="Exclude replies from the export.",
        )
        parser.add_argument(
            "--exclude-retweets",
            action="store_true",
            help="Exclude retweets from the export.",
        )

    def handle(self, *args, **options):
        username = options["username"].lstrip("@")
        output_path = options["output"] or str(
            Path(settings.BASE_DIR) / f"tweets_{username}_export.txt"
        )

        bearer_token = getattr(settings, "TWITTER_BEARER_TOKEN", "")
        if not bearer_token:
            raise CommandError("Missing TWITTER_BEARER_TOKEN in Django settings.")

        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "personal-site-export-command",
        }

        user_id = self._resolve_user_id(username, headers)
        self.stdout.write(f"Resolved @{username} to user id {user_id}")

        all_tweets = self._fetch_all_tweets(
            user_id=user_id,
            username=username,
            headers=headers,
            exclude_replies=options["exclude_replies"],
            exclude_retweets=options["exclude_retweets"],
        )

        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        self._write_export(out_file, username, user_id, all_tweets)

        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote {len(all_tweets)} tweets to {out_file}"
            )
        )

    def _api_get(self, url, headers, timeout=20):
        req = urlrequest.Request(url, headers=headers)
        try:
            with urlrequest.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise CommandError(f"HTTP {exc.code} for {url}: {body[:500]}")
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise CommandError(f"Request failed for {url}: {exc}")

    def _resolve_user_id(self, username, headers):
        user_id = getattr(settings, "TWITTER_USER_ID", "") or ""
        if user_id:
            return user_id

        cache_key = f"x_user_id_{username}"
        user_id = cache.get(cache_key) or ""
        if user_id:
            return user_id

        access_token = getattr(settings, "TWITTER_ACCESS_TOKEN", "")
        if "-" in access_token:
            token_prefix = access_token.split("-", 1)[0]
            if token_prefix.isdigit():
                return token_prefix

        lookup_url = f"https://api.x.com/2/users/by/username/{username}?user.fields=id"
        payload = self._api_get(lookup_url, headers=headers, timeout=10)
        user_data = payload.get("data") or {}
        user_id = user_data.get("id") or ""
        if not user_id:
            raise CommandError(f"Could not resolve user id for @{username}.")

        cache.set(cache_key, user_id, timeout=60 * 60 * 24 * 30)
        return user_id

    def _fetch_all_tweets(
        self,
        *,
        user_id,
        username,
        headers,
        exclude_replies=False,
        exclude_retweets=False,
    ):
        tweets = []
        next_token = None
        page_num = 0

        exclude_values = []
        if exclude_retweets:
            exclude_values.append("retweets")
        if exclude_replies:
            exclude_values.append("replies")

        while True:
            page_num += 1
            params = {
                "max_results": 100,
                "tweet.fields": "created_at",
            }
            if exclude_values:
                params["exclude"] = ",".join(exclude_values)
            if next_token:
                params["pagination_token"] = next_token

            url = f"https://api.x.com/2/users/{user_id}/tweets?{parse.urlencode(params)}"
            payload = self._api_get(url, headers=headers, timeout=20)
            page_tweets = payload.get("data") or []
            tweets.extend(page_tweets)

            meta = payload.get("meta") or {}
            result_count = meta.get("result_count", len(page_tweets))
            self.stdout.write(
                f"Fetched page {page_num}: {result_count} tweets (running total: {len(tweets)})"
            )

            next_token = meta.get("next_token")
            if not next_token:
                break

        tweets.sort(key=lambda t: (t.get("created_at", ""), t.get("id", "")))
        return tweets

    def _write_export(self, out_file, username, user_id, tweets):
        with out_file.open("w", encoding="utf-8") as fh:
            fh.write(f"X/Twitter export for @{username}\n")
            fh.write(f"User ID: {user_id}\n")
            fh.write(f"Total tweets fetched: {len(tweets)}\n\n")

            for index, tweet in enumerate(tweets, start=1):
                tweet_id = tweet.get("id", "")
                created_at = tweet.get("created_at", "")
                text = (tweet.get("text") or "").replace("\r\n", "\n").replace("\r", "\n")
                url = f"https://x.com/{username}/status/{tweet_id}" if tweet_id else ""

                fh.write(f"[{index}] {created_at} | {tweet_id}\n")
                if url:
                    fh.write(f"{url}\n")
                fh.write(text)
                fh.write("\n\n")

