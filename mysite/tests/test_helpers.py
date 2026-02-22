from datetime import datetime, timezone

from django.test import SimpleTestCase

from mysite.views import _next_daily_refresh_utc, _parse_utc_iso


class HelperFunctionTests(SimpleTestCase):
    def test_parse_utc_iso_valid(self):
        dt = _parse_utc_iso("2025-02-15T07:00:00+00:00")
        self.assertEqual(dt, datetime(2025, 2, 15, 7, 0, tzinfo=timezone.utc))

    def test_parse_utc_iso_invalid_or_empty(self):
        self.assertIsNone(_parse_utc_iso(None))
        self.assertIsNone(_parse_utc_iso(""))
        self.assertIsNone(_parse_utc_iso("not-a-date"))

    def test_next_daily_refresh_same_day_when_before_refresh(self):
        now_utc = datetime(2025, 2, 15, 6, 30, tzinfo=timezone.utc)
        refresh = _next_daily_refresh_utc(now_utc, 7)
        self.assertEqual(refresh, datetime(2025, 2, 15, 7, 0, tzinfo=timezone.utc))

    def test_next_daily_refresh_next_day_when_at_or_after_refresh(self):
        at_refresh = datetime(2025, 2, 15, 7, 0, tzinfo=timezone.utc)
        after_refresh = datetime(2025, 2, 15, 8, 0, tzinfo=timezone.utc)
        self.assertEqual(
            _next_daily_refresh_utc(at_refresh, 7),
            datetime(2025, 2, 16, 7, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            _next_daily_refresh_utc(after_refresh, 7),
            datetime(2025, 2, 16, 7, 0, tzinfo=timezone.utc),
        )

