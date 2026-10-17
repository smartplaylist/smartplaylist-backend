import unittest
from datetime import date

from models.requests import EARLIEST_RELEASE
from models.requests import KeyParam
from models.requests import RangeParam
from models.requests import ReleaseDateParam
from models.requests import SavePlaylistRequest
from models.requests import TrackSearchParams
from pydantic import ValidationError

# The query the website builds with its default form values.
WEBSITE_DEFAULTS = dict(
    nam="",
    gen="",
    rel="2022-01-01",
    tem="80,210",
    pop="0,100",
    map="0,100",
    maf="1,50000000",
    dan="0,100",
    ene="0,100",
    spe="0,100",
    aco="0,100",
    ins="0,100",
    liv="0,100",
    val="0,100",
    key="any,any",
    order="rel,des",
    limit=250,
)

TRACK_ID = "4uLU6hMCjMI75M1A2tKUQC"


class RangeParamTest(unittest.TestCase):
    def test_a_min_max_pair_is_parsed_into_inclusive_bounds(self):
        self.assertEqual(RangeParam.from_string("10,90").bounds(), [10, 90])

    def test_tempo_above_one_hundred_is_accepted(self):
        self.assertEqual(RangeParam.from_string("80,210").bounds(), [80, 210])

    def test_follower_counts_in_the_millions_are_accepted(self):
        self.assertEqual(
            RangeParam.from_string("1,50000000").bounds(), [1, 50_000_000]
        )

    def test_an_empty_value_falls_back_to_the_default_range(self):
        self.assertEqual(RangeParam.from_string("").bounds(), [0, 100])

    def test_a_maximum_below_the_minimum_is_rejected(self):
        with self.assertRaises(ValueError):
            RangeParam.from_string("90,10")

    def test_a_negative_bound_is_rejected(self):
        with self.assertRaises(ValueError):
            RangeParam.from_string("-1,10")

    def test_a_single_number_is_rejected(self):
        with self.assertRaises(ValueError):
            RangeParam.from_string("10")

    def test_a_non_numeric_bound_is_rejected(self):
        with self.assertRaises(ValueError):
            RangeParam.from_string("abc,10")

    def test_an_empty_bound_is_rejected(self):
        with self.assertRaises(ValueError):
            RangeParam.from_string("80,")


class KeyParamTest(unittest.TestCase):
    def test_any_on_both_sides_spans_every_key(self):
        self.assertEqual(KeyParam.from_string("any,any").bounds(), [0, 12])

    def test_a_single_key_is_passed_through_as_both_bounds(self):
        self.assertEqual(KeyParam.from_string("5,5").bounds(), [5, 5])

    def test_a_key_above_twelve_is_rejected(self):
        with self.assertRaises(ValueError):
            KeyParam.from_string("0,13")

    def test_a_key_without_a_pair_is_rejected(self):
        with self.assertRaises(ValueError):
            KeyParam.from_string("1")


class ReleaseDateParamTest(unittest.TestCase):
    def test_a_release_date_keeps_its_day_precision(self):
        self.assertEqual(
            ReleaseDateParam.from_string("2023-06-15").after, date(2023, 6, 15)
        )

    def test_no_release_date_means_no_lower_bound(self):
        self.assertEqual(ReleaseDateParam.from_string("").after, EARLIEST_RELEASE)

    def test_a_date_in_another_format_is_rejected(self):
        with self.assertRaises(ValueError):
            ReleaseDateParam.from_string("15/06/2023")

    def test_a_year_offset_range_is_rejected(self):
        with self.assertRaises(ValueError):
            ReleaseDateParam.from_string("0,100")


class TrackSearchParamsTest(unittest.TestCase):
    def test_the_website_default_query_is_accepted(self):
        params = TrackSearchParams.from_query_params(**WEBSITE_DEFAULTS)
        self.assertEqual(params.limit, 250)

    def test_filters_carry_the_values_the_website_sent(self):
        filters = TrackSearchParams.from_query_params(**WEBSITE_DEFAULTS).filters()
        self.assertEqual(filters["tempo"], [80, 210])
        self.assertEqual(filters["main_artist_followers"], [1, 50_000_000])
        self.assertEqual(filters["release"], [date(2022, 1, 1)])
        self.assertEqual(filters["key"], [0, 12])

    def test_trailing_commas_are_stripped_from_name_and_genres(self):
        params = TrackSearchParams.from_query_params(
            **{**WEBSITE_DEFAULTS, "nam": "drake,", "gen": "pop,rock,"}
        )
        self.assertEqual(params.name, "drake")
        self.assertEqual(params.genres, "pop,rock")

    def test_both_spellings_of_descending_order_are_accepted(self):
        for order in ("rel,des", "rel,desc", "pop,asc"):
            with self.subTest(order=order):
                params = TrackSearchParams.from_query_params(
                    **{**WEBSITE_DEFAULTS, "order": order}
                )
                self.assertEqual(params.order, order)

    def test_an_unknown_order_field_is_rejected(self):
        with self.assertRaises(ValueError):
            TrackSearchParams.from_query_params(
                **{**WEBSITE_DEFAULTS, "order": "tempo,desc"}
            )

    def test_a_limit_above_one_thousand_is_rejected(self):
        with self.assertRaises(ValueError):
            TrackSearchParams.from_query_params(**{**WEBSITE_DEFAULTS, "limit": 1001})

    def test_a_name_longer_than_two_hundred_characters_is_rejected(self):
        with self.assertRaises(ValueError):
            TrackSearchParams.from_query_params(**{**WEBSITE_DEFAULTS, "nam": "a" * 201})


class SavePlaylistRequestTest(unittest.TestCase):
    def test_the_payload_the_website_sends_is_accepted(self):
        request = SavePlaylistRequest.parse_obj(
            {"accessToken": "token", "ids": [TRACK_ID]}
        )
        self.assertEqual(request.access_token, "token")
        self.assertEqual(request.track_ids, [TRACK_ID])
        self.assertIsNone(request.playlist_name)

    def test_field_names_work_as_well_as_aliases(self):
        request = SavePlaylistRequest(access_token="token", track_ids=[TRACK_ID])
        self.assertEqual(request.track_ids, [TRACK_ID])

    def test_an_empty_track_list_is_rejected(self):
        with self.assertRaises(ValidationError):
            SavePlaylistRequest.parse_obj({"accessToken": "token", "ids": []})

    def test_a_truncated_track_id_is_rejected(self):
        with self.assertRaises(ValidationError):
            SavePlaylistRequest.parse_obj({"accessToken": "token", "ids": ["short"]})

    def test_a_missing_access_token_is_rejected(self):
        with self.assertRaises(ValidationError):
            SavePlaylistRequest.parse_obj({"ids": [TRACK_ID]})

    def test_more_tracks_than_a_playlist_can_hold_are_rejected(self):
        with self.assertRaises(ValidationError):
            SavePlaylistRequest.parse_obj(
                {"accessToken": "token", "ids": [TRACK_ID] * 10001}
            )


if __name__ == "__main__":
    unittest.main()
