"""Tests for the ioref-inventory integration.

SimpleTestCase throughout: there is no database to set up. Stock lives in
ioref-inventory and the guides are files.

The interesting cases are all failure modes. A guide page must stay readable
when inventory is down, and the browse view must not render an outage as an
empty catalogue.
"""

from unittest.mock import patch

import httpx
from django.core.cache import cache
from django.test import SimpleTestCase

from stock.client import (
    InventoryUnavailable,
    get_stock,
    list_categories,
    list_groups_by_category,
    list_ungrouped_parts_by_category,
    list_parts,
)

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


class GetStockTests(SimpleTestCase):
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


class ListPartsTests(SimpleTestCase):
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


class ListCategoriesTests(SimpleTestCase):
    @patch("stock.client._get")
    def test_returns_the_list(self, mock_get):
        mock_get.return_value = {"results": [{"slug": "power", "name": "Power"}]}
        self.assertEqual(list_categories()[0]["slug"], "power")

    @patch("stock.client._get")
    def test_outage_raises_rather_than_returning_empty(self, mock_get):
        """An empty list here reads as "no categories exist", not "inventory
        is down" -- the same distinction list_parts() already draws."""
        mock_get.side_effect = httpx.ConnectError("refused")
        with self.assertRaises(InventoryUnavailable):
            list_categories()


class ListGroupsByCategoryTests(SimpleTestCase):
    @patch("stock.client._get")
    def test_returns_the_groups(self, mock_get):
        mock_get.return_value = {"results": [{"slug": "resistor", "name": "Resistors"}]}
        self.assertEqual(list_groups_by_category("power")[0]["slug"], "resistor")

    @patch("stock.client._get")
    def test_outage_raises_rather_than_returning_empty(self, mock_get):
        """An outage must not render as an empty category."""
        mock_get.side_effect = httpx.ConnectError("refused")
        with self.assertRaises(InventoryUnavailable):
            list_groups_by_category("power")


class ListUngroupedPartsByCategoryTests(SimpleTestCase):
    @patch("stock.client._get")
    def test_requests_only_ungrouped_parts(self, mock_get):
        mock_get.return_value = {"results": [PART]}
        self.assertEqual(list_ungrouped_parts_by_category("input"), [PART])
        mock_get.assert_called_once_with(
            "/api/v1/parts/",
            {"category": "input", "ungrouped": "true", "limit": 200},
        )

    @patch("stock.client._get")
    def test_outage_raises(self, mock_get):
        mock_get.side_effect = httpx.ConnectError("refused")
        with self.assertRaises(InventoryUnavailable):
            list_ungrouped_parts_by_category("input")


class InventoryViewTests(SimpleTestCase):
    def test_index_redirects_to_inventory_application(self):
        response = self.client.get("/inventory/")
        self.assertRedirects(
            response,
            "https://inventory.ioref.org/",
            status_code=301,
            fetch_redirect_response=False,
        )

    def test_index_preserves_filters(self):
        response = self.client.get("/inventory/?group=fasteners&q=bolt")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response["Location"],
            "https://inventory.ioref.org/?group=fasteners&q=bolt",
        )

    def test_detail_redirects_to_inventory_part(self):
        response = self.client.get("/inventory/0020/")
        self.assertRedirects(
            response,
            "https://inventory.ioref.org/parts/0020/",
            status_code=301,
            fetch_redirect_response=False,
        )
