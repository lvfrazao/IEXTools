"""
This module defines the IEX_API class which acts as an abstraction to the IEX
REST API.

The IEX_API attempts to implement every endpoint available on the public API.

All functions of this client that calls out to the IEX API must follow the same
design pattern:
    1) Perform error checking on inputs given (e.g., if expecting certain
       arguments)
    2) Retrieve the required endpoint by calling the _get_endpoint method
    3) Build the parameters to be used by the function
    4) Route all calls to the IEX API through the _request method

Any new endpoints should subsequently be registered in the endpoints variable
of the _get_endpoint method.

#TODO make async implementation of API client
"""
import requests
import logging
import json
import re
from time import sleep
from functools import wraps
from typing import Callable, List, Optional, Union


def pretty_json(json_dict):
    pretty = json.dumps(json_dict, sort_keys=True, indent=4)
    return pretty


def http_retry(method: Callable) -> Callable:
    """
    Decorator to give a retry mechanism to methods that make HTTP calls.
    Theoretically could be used to give retry behavior for any type of method.
    Params:
        method  : method, any callable method in a class
    Returns:
        meth_wrapper    : function, the method given wrapped in the retry logic
    """
    max_tries = 5
    num_tries = 0
    base_sleep = 2

    @wraps(method)
    def meth_wrapper(self, *args, **kwargs):
        nonlocal num_tries
        while num_tries < max_tries:
            try:
                val = method(self, *args, **kwargs)
            except (
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
            ) as e:
                num_tries += 1
                if num_tries <= max_tries:
                    logging.error(
                        f"HTTP error, retrying in {base_sleep ** num_tries} "
                        f"seconds: {str(e)}"
                    )
                    sleep(base_sleep ** num_tries)
                else:
                    raise
            else:
                num_tries = 0
                return val

    return meth_wrapper


class IEX_API(object):
    def __init__(self, timeout: int = 5) -> None:
        self.timeout = timeout

    def _get_endpoint(self, entity: str, ID: List[str]) -> str:
        """
        Returns the endpoint to be used for the web request

        Params:
            entity  : type of object being requested (e.g., 'batch', 'book', 'chart')
            ID      : name or identification string for the resource
        """
        BASE = "https://api.iextrading.com/1.0/{}"

        endpoints = {
            "batch": "stock/{}/batch",  # Implemented
            "book": "stock/{}/book",  # Implemented
            "chart": "stock/{}/chart/{}",  # Implemented
            "collection": "stock/market/collection/{}",  # Implemented 
            "company": "stock/{}/company",  # Implemented
            "crypto": "stock/market/crypto",  # Implemented
            "delayed quote": "stock/{}/delayed-quote",  # Implemented
            "dividends": "stock/{}/dividends/{}",  # Implemented
            "earnings": "stock/{}/earnings",  # Implemented
            "earnings today": "stock/market/today-earnings",  # Implemented
            "effective spread": "stock/{}/effective-spread",  # Implemented
            "financials": "stock/{}/financials",  # Implemented
            "upcoming ipos": "stock/market/upcoming-ipos",  # Implemented
            "today ipos": "stock/market/today-ipos",  # Implemented
            "iex threshold securities": "stock/{}/threshold-securities",  # Implemented
            "iex short interest": "stock/{}/short-interest",  # Implemented
            "key stats": "stock/{}/stats",  # TODO
            "largest trades": "stock/{}/largest-trades",  # TODO
            "list most active": "/stock/market/list/mostactive",  # TODO
            "list gainers": "/stock/market/list/gainers",  # TODO
            "list losers": "/stock/market/list/losers",  # TODO
            "list iexvolume": "/stock/market/list/iexvolume",  # TODO
            "list iexpercent": "/stock/market/list/iexpercent",  # TODO
            "list infocus": "/stock/market/list/infocus",  # TODO
            "logo": "stock/{}/logo",  # TODO
            "news": "stock/{}/news/last/{}",  # TODO
            "ohlc": "stock/{}/ohlc",  # TODO
            "peers": "stock/{}/peers",  # TODO
            "previous": "stock/{}/previous",  # TODO
            "price": "stock/{}/price",  # TODO
            "quote": "stock/{}/quote",  # TODO
            "relevant": "stock/{}/relevant",  # TODO
            "sector performance": "stock/market/sector-performance",  # TODO
            "splits": "stock/{}/splits/{}",  # TODO
            "time series": "stock/{}/time-series",  # TODO
            "volume by venue": "stock/{}/volume-by-venue",  # TODO
            "symbols": "ref-data/symbols",  # TODO
            "iex corp actions": "ref-data/daily-list/symbol-directory",  # TODO
            "iex dividends": "ref-data/daily-list/dividends",  # TODO
            "iex next day ex div": "ref-data/daily-list/next-day-ex-date",  # TODO
            "iex symbols": "ref-data/daily-list/symbol-directory",  # TODO
            "tops": "tops",  # TODO
            "last": "last",  # TODO
            "tops last": "tops/last",  # TODO
            "hist download": "hist",  # TODO
            "deep": "deep",  # TODO
            "deep book": "deep/book",  # TODO
            "deep trades": "deep/trades",  # TODO
            "system event": "deep/system-event",  # TODO
            "trading status": "deep/trading-status",  # TODO
            "operational halt": "deep/op-halt-status",  # TODO
            "short sale price test status": "deep/ssr-status",  # TODO
            "security event": "deep/security-event",  # TODO
            "trade break": "deep/trade-breaks",  # TODO
            "iex auction": "deep/auction",  # TODO
            "iex official price": "deep/official-price",  # TODO
            "iex stats intraday": "stats/intraday",  # TODO
            "iex stats recent": "stats/recent",  # TODO
            "iex stats records": "stats/records",  # TODO
            "iex historical": "stats/historical",  # TODO
            "iex historial daily": "stats/historical/daily",  # TODO
            "market": "market",  # TODO
        }

        endpoint = BASE.format(endpoints[entity].format(*ID))

        return endpoint

    @http_retry
    def _request(
        self, method: str, endpoint: str, params: Optional[dict] = None
    ) -> dict:
        """
        Wrapper around the requests library to validate inputs to a request,
        make the request, and handle any errors
        """
        params = params if params else {}
        logging.debug(
            f"Making request for endpoint {endpoint} and parameters: {params}"
        )
        try:
            resp = requests.request(
                method, endpoint, params=params, timeout=self.timeout
            )
            logging.debug(f"Received response - status: {resp.status_code}")
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                err_resp = e.response.json()
            except json.decoder.JSONDecodeError:
                err_resp = e
            status = resp.status_code
            logging.error(
                f"API request encountered a {status} status code: {err_resp}"
            )
            raise
        else:
            return resp.json()

    def _comma_sep_params(self, data: Union[List[str], str]) -> str:
        if isinstance(data, str):
            return data
        return ",".join(data)

    def _format_params(self, params: dict) -> dict:
        return {k: self._comma_sep_params(v) for k, v in params.items()}

    def batch(
        self,
        symbols: List[str],
        types: List[str],
        range_time: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        Makes a batch request to the IEX API.
        https://iextrading.com/developer/docs/#batch-requests

        From the API docs:
        Options
        symbol
        • Use market to query multiple symbols (i.e. .../market/batch?...)

        Parameters

        types
        • Required
        • Comma delimited list of endpoints to call. The names should match the
          individual endpoint names. Limited to 10 types.

        symbols
        • Optional
        • Comma delimited list of symbols limited to 100. This parameter is
          used only if market option is used.

        range
        • Optional
        • Used to specify a chart range if chart is used in types parameter.

        *
        • Optional
        • Parameters that are sent to individual endpoints can be specified in
          batch calls and will be applied to each supporting endpoint.
        """
        params = {}
        _symbols = [symbols] if isinstance(symbols, str) else symbols
        if len(_symbols) > 1:
            ID = ["market"]
            params["symbols"] = self._comma_sep_params(_symbols)
        else:
            ID = _symbols

        params["types"] = self._comma_sep_params(types)
        if "chart" in types:
            params["range"] = self._comma_sep_params(range_time)
        endpoint = self._get_endpoint("batch", ID)
        params.update(self._format_params(kwargs))
        return self._request("get", endpoint, params)

    def book(self, symbol: str) -> dict:
        """
        Book data on a given symbol (best quote, bid/ask, trades)
        https://iextrading.com/developer/docs/#book

        Response includes data from deep and quote. Refer to each endpoint
        for details.
        """
        endpoint = self._get_endpoint("book", [symbol])
        return self._request("get", endpoint, {})

    def chart(self, symbol: str, date_range: str, **kwargs) -> dict:
        """
        Provides historically adjusted price data on a given symbol
        https://iextrading.com/developer/docs/#chart
        """
        valid_dates = (
            "5y",
            "2y",
            "1y",
            "ytd",
            "6m",
            "3m",
            "1m",
            "1d",
            r"2\d\d\d[01]\d[0-3]\d",
            "dynamic",
        )

        valid_params = {
            "chartReset"
            "chartSimplify"
            "chartInterval"
            "changeFromClose"
            "chartLast"
        }

        date_pattern = re.compile(
            f'({"|".join([f"^{date}$" for date in valid_dates])})'
        )
        if not date_pattern.search(date_range):
            raise ValueError(
                "Date range must match the following regex: "
                f"{date_pattern.pattern}"
            )

        if not set(kwargs.keys()) <= valid_params:
            non_valid = set(kwargs.keys()) - valid_params
            raise ValueError(f"Parameters passed not valid: {non_valid}")

        endpoint = self._get_endpoint("chart", [symbol, date_range])
        params = self._format_params(kwargs)
        return self._request("get", endpoint, params)

    def collections(self, collectiontype: str, collection_name: str) -> dict:
        """
        Returns an array of quote objects for a given collection type.
        Currently supported collection types are sector, tag, and list

        https://iextrading.com/developer/docs/#collections
        """
        endpoint = self._get_endpoint("collection", [collectiontype])
        params = {"collectionName": collection_name}
        return self._request("get", endpoint, params)

    def company(self, symbol: str) -> dict:
        """
        Returns basic information on the given company.

        https://iextrading.com/developer/docs/#company
        """
        endpoint = self._get_endpoint("company", [symbol])
        return self._request("get", endpoint, {})

    def crypto(self) -> dict:
        """
        Returns quotes on crypto currencies.
        https://iextrading.com/developer/docs/#crypto

        From the docs:
        This will return an array of quotes for all Cryptocurrencies supported
        by the IEX API. Each element is a standard quote object with four additional keys.
        """
        endpoint = self._get_endpoint("crypto", [])
        return self._request("get", endpoint, {})

    def delayed_quote(self, symbol: str) -> dict:
        """
        Returns a 15 min delayed price quote

        https://iextrading.com/developer/docs/#delayed-quote
        """
        endpoint = self._get_endpoint("delayed quote", [symbol])
        return self._request("get", endpoint, {})

    def dividends(self, symbol: str, date_range: str) -> dict:
        """
        Returns dividend information over a given date range for a given
        company.

        https://iextrading.com/developer/docs/#dividends
        """
        endpoint = self._get_endpoint("dividends", [symbol, date_range])

        valid_dates = (
            "5y",
            "2y",
            "1y",
            "ytd",
            "6m",
            "3m",
            "1m",
        )
        if date_range not in valid_dates:
            raise ValueError("Date range given is not valid")
        return self._request("get", endpoint, {})

    def earnings(self, symbol: str) -> dict:
        """
        Return earnings information for four most recent quarters for a given
        company.

        https://iextrading.com/developer/docs/#earnings
        """
        endpoint = self._get_endpoint("earnings", [symbol])
        return self._request("get", endpoint, {})

    def earnings_today(self) -> dict:
        """
        Returns information on companies announcing earnings today.

        https://iextrading.com/developer/docs/#earnings-today
        """
        endpoint = self._get_endpoint("earnings today", [])
        return self._request("get", endpoint, {})

    def effective_spread(self, symbol: str) -> dict:
        """
        Returns data on the effective spread, eligible volume, and price
        improvement of a given stock.

        https://iextrading.com/developer/docs/#effective-spread
        """
        endpoint = self._get_endpoint("effective spread", [symbol])
        return self._request("get", endpoint, {})

    def financials(self, symbol: str, period: Optional[str] = None) -> dict:
        """
        Returns financial data for a given company over the four most recent
        reported quarters.

        https://iextrading.com/developer/docs/#financials
        """
        endpoint = self._get_endpoint("financials", [symbol])

        if period not in ("annual", "quarter") and period is not None:
            raise ValueError("Invalid period provided")
        params = {"period": period}
        return self._request("get", endpoint, params)

    def upcoming_ipos(self) -> dict:
        """
        Returns list of upcoming IPOs and data regarding the companies

        https://iextrading.com/developer/docs/#ipo-calendar
        """
        endpoint = self._get_endpoint("upcoming ipos", [])
        return self._request("get", endpoint, {})

    def today_ipos(self) -> dict:
        """
        Returns list of IPOs occuring today and data regarding the companies

        https://iextrading.com/developer/docs/#ipo-calendar
        """
        endpoint = self._get_endpoint("today ipos", [])
        return self._request("get", endpoint, {})

    def iex_threshold_securities(self, symbol: str = "market", date: Optional[str] = None) -> dict:
        """
        https://iextrading.com/developer/docs/#iex-regulation-sho-threshold-securities-list

        From the docs:
        Returns IEX-listed securities that have an aggregate fail to deliver
        position for five consecutive settlement days at a registered clearing
        agency, totaling 10,000 shares or more and equal to at least 0.5% of
        the issuer’s total shares outstanding (i.e., “threshold securities”). 
        """
        valid_date = re.compile(r"2\d\d\d[01]\d[0-3]\d")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        endpoint = self._get_endpoint("iex threshold securities", [symbol])
        params = {"date": date}
        return self._request("get", endpoint, params)

    def iex_short_interest(self, symbol: str = "market", date: Optional[str] = None) -> dict:
        """
        Returns information on short interest positions for IEX listed stocks

        https://iextrading.com/developer/docs/#iex-short-interest-list
        """
        valid_date = re.compile(r"2\d\d\d[01]\d[0-3]\d")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        endpoint = self._get_endpoint("iex short interest", [symbol])
        params = {"date": date}
        return self._request("get", endpoint, params)
