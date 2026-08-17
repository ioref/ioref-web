"""Tests for the ioref-inventory integration.

The interesting cases are all failure modes. A guide page must stay readable
when inventory is down, and the browse view must not render an outage as an
empty catalogue.
"""

from unittest.mock import patch

import httpx
from django.core.cache import cache
from django.test import TestCase

from stock.client import InventoryUnavailable, get_stock, list_parts

PART = {
    "part_number": "0020",
    "short_name": "flexible protoboard",
    "on_floor": 10,
    "in_backstock": 0,
    "total_on_hand": 10,
    "needs_restock": False,
    "unit": "each",
    "location": "Connector: Board Mount",
    "status": "active",
    "latest_price": None,
}


def _response(status, json_body=None):
    request = httpx.Request("GET", "http://inventory/api/v1/parts/0020/")
    return httpx.Response(status, json=json_body or {}, request=request)


class GetStockTests(TestCase):
    def setUp(self):
        cache.clear()

    @patch("stock.client._get")
    def test_returns_part_data(self, mock_get):
        mock_get.return_value = PART
        self.assertEqual(get_stock("0020")["on_floor"], 10)

    @patch("stock.client._get")
    def test_result_is_cached(self, mock_get):
        mock_get.return_value = PART
        get_stock("0020")
        get_stock("0020")
        # Part pages are the busiest on the site; inventory must not be in the
        # request path of every pageview.
        self.assertEqual(mock_get.call_count, 1)

    @patch("stock.client._get")
    def test_unreachable_inventory_returns_none_not_an_error(self, mock_get):
        mock_get.side_effect = httpx.ConnectError("refused")
        # The guide content is the point of the page and reads fine without stock.
        self.assertIsNone(get_stock("0020"))

    @patch("stock.client._get")
    def test_timeout_returns_none(self, mock_get):
        mock_get.side_effect = httpx.ReadTimeout("slow")
        self.assertIsNone(get_stock("0020"))

    @patch("stock.client._get")
    def test_unknown_part_is_a_cached_miss(self, mock_get):
        mock_get.side_effect = httpx.HTTPStatusError(
            "404", request=None, response=_response(404)
        )
        self.assertIsNone(get_stock("9999"))
        self.assertIsNone(get_stock("9999"))
        # A part with a guide but no stock record must not be re-requested on
        # every single pageview.
        self.assertEqual(mock_get.call_count, 1)

    @patch("stock.client._get")
    def test_server_error_returns_none_and_is_not_cached(self, mock_get):
        mock_get.side_effect = httpx.HTTPStatusError(
            "500", request=None, response=_response(500)
        )
        self.assertIsNone(get_stock("0020"))
        self.assertIsNone(get_stock("0020"))
        # Unlike a 404, a 500 is transient -- caching it would extend the outage.
        self.assertEqual(mock_get.call_count, 2)


class ListPartsTests(TestCase):
    @patch("stock.client._get")
    def test_returns_page(self, mock_get):
        mock_get.return_value = {"count": 1, "results": [PART]}
        self.assertEqual(list_parts()["count"], 1)

    @patch("stock.client._get")
    def test_outage_raises_rather_than_returning_empty(self, mock_get):
        mock_get.side_effect = httpx.ConnectError("refused")
        # The browse view has to tell "nothing matched" apart from "inventory
        # is down"; an empty list for both would silently show an empty shop.
        with self.assertRaises(InventoryUnavailable):
            list_parts()


class InventoryViewTests(TestCase):
    @patch("stock.views.list_parts")
    def test_index_renders_parts(self, mock_list):
        mock_list.return_value = {"count": 1, "results": [dict(PART)]}
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "flexible protoboard")

    @patch("stock.views.list_parts")
    def test_index_reports_outage_as_503(self, mock_list):
        mock_list.side_effect = InventoryUnavailable
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "not responding", status_code=503)

    @patch("stock.views.list_parts")
    def test_empty_result_is_not_an_outage(self, mock_list):
        mock_list.return_value = {"count": 0, "results": []}
        response = self.client.get("/inventory/?q=nothing")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No parts match")

    @patch("stock.views.get_part")
    def test_detail_404s_for_unstocked_part(self, mock_get):
        mock_get.return_value = None
        response = self.client.get("/inventory/9999/")
        self.assertEqual(response.status_code, 404)

    @patch("stock.views.get_part")
    def test_detail_renders(self, mock_get):
        mock_get.return_value = dict(PART)
        response = self.client.get("/inventory/0020/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Connector: Board Mount")
