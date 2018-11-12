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
        self.BASE = "https://api.iextrading.com/1.0/{}"

    def _get_endpoint(self, entity: str, ID: List[str]) -> str:
        """
        Returns the endpoint to be used for the web request.

        Params:
            entity  : type of object being requested (e.g., 'batch', 'book', 'chart')
            ID      : name or identification string for the resource
        """

        endpoints = {
            "batch": "stock/{}/batch",
            "book": "stock/{}/book",
            "chart": "stock/{}/chart/{}",
            "collection": "stock/market/collection/{}",
            "company": "stock/{}/company",
            "crypto": "stock/market/crypto",
            "delayed quote": "stock/{}/delayed-quote",
            "dividends": "stock/{}/dividends/{}",
            "earnings": "stock/{}/earnings",
            "earnings today": "stock/market/today-earnings",
            "effective spread": "stock/{}/effective-spread",
            "financials": "stock/{}/financials",
            "upcoming ipos": "stock/market/upcoming-ipos",
            "today ipos": "stock/market/today-ipos",
            "iex threshold securities": "stock/{}/threshold-securities",
            "iex short interest": "stock/{}/short-interest",
            "key stats": "stock/{}/stats",
            "largest trades": "stock/{}/largest-trades",
            "list most active": "/stock/market/list/mostactive",
            "list gainers": "/stock/market/list/gainers",
            "list losers": "/stock/market/list/losers",
            "list iexvolume": "/stock/market/list/iexvolume",
            "list iexpercent": "/stock/market/list/iexpercent",
            "list infocus": "/stock/market/list/infocus",
            "logo": "stock/{}/logo",
            "news": "stock/{}/news/last/{}",
            "ohlc": "stock/{}/ohlc",
            "peers": "stock/{}/peers",
            "previous": "stock/{}/previous",
            "price": "stock/{}/price",
            "quote": "stock/{}/quote",
            "relevant": "stock/{}/relevant",
            "sector performance": "stock/market/sector-performance",
            "splits": "stock/{}/splits/{}",
            "time series": "stock/{}/time-series",
            "volume by venue": "stock/{}/volume-by-venue",
            "symbols": "ref-data/symbols",
            "iex corp actions": "ref-data/daily-list/symbol-directory",
            "iex dividends": "ref-data/daily-list/dividends",
            "iex next day ex div": "ref-data/daily-list/next-day-ex-date",
            "iex symbols": "ref-data/daily-list/symbol-directory",
            "tops": "tops",
            "last": "tops/last",
            "hist download": "hist",
            "deep": "deep",
            "deep book": "deep/book",
            "deep trades": "deep/trades",
            "system event": "deep/system-event",
            "trading status": "deep/trading-status",
            "operational halt": "deep/op-halt-status",
            "short sale price test status": "deep/ssr-status",
            "security event": "deep/security-event",
            "trade break": "deep/trade-breaks",
            "iex auction": "deep/auction",
            "iex official price": "deep/official-price",
            "iex stats intraday": "stats/intraday",
            "iex stats recent": "stats/recent",
            "iex stats records": "stats/records",
            "iex historical": "stats/historical",
            "iex historial daily": "stats/historical/daily",
            "market": "market",
        }

        endpoint = self.BASE.format(endpoints[entity].format(*ID))

        return endpoint

    @http_retry
    def _request(
        self, method: str, endpoint: str, params: Optional[dict] = None
    ) -> dict:
        """
        Wrapper around the requests library to validate inputs to a request,
        make the request, and handle any errors.
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

    def _comma_sep_params(
        self, data: Optional[Union[List[str], str]]
    ) -> Optional[str]:
        if data is None:
            return None
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
        Book data on a given symbol (best quote, bid/ask, trades).

        Response includes data from deep and quote. Refer to each endpoint
        for details.

        https://iextrading.com/developer/docs/#book
        """
        endpoint = self._get_endpoint("book", [symbol])
        return self._request("get", endpoint, {})

    def chart(self, symbol: str, date_range: str, **kwargs) -> dict:
        """
        Provides historically adjusted price data on a given symbol.

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
            r"2\d\d\d[01]\d[0-3]d",
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
        Currently supported collection types are sector, tag, and list.

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
        by the IEX API. Each element is a standard quote object with four
        additional keys.
        """
        endpoint = self._get_endpoint("crypto", [])
        return self._request("get", endpoint, {})

    def delayed_quote(self, symbol: str) -> dict:
        """
        Returns a 15 min delayed price quote.

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

        valid_dates = ("5y", "2y", "1y", "ytd", "6m", "3m", "1m")
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
        Returns list of upcoming IPOs and data regarding the companies.

        https://iextrading.com/developer/docs/#ipo-calendar
        """
        endpoint = self._get_endpoint("upcoming ipos", [])
        return self._request("get", endpoint, {})

    def today_ipos(self) -> dict:
        """
        Returns list of IPOs occuring today and data regarding the companies.

        https://iextrading.com/developer/docs/#ipo-calendar
        """
        endpoint = self._get_endpoint("today ipos", [])
        return self._request("get", endpoint, {})

    def iex_threshold_securities(
        self, symbol: str = "market", date: Optional[str] = None
    ) -> dict:
        """
        https://iextrading.com/developer/docs/#iex-regulation-sho-threshold-securities-list

        From the docs:
        Returns IEX-listed securities that have an aggregate fail to deliver
        position for five consecutive settlement days at a registered clearing
        agency, totaling 10,000 shares or more and equal to at least 0.5% of
        the issuer’s total shares outstanding (i.e., “threshold securities”).
        """
        valid_date = re.compile(r"^2\d\d\d[01]\d[0-3]\d$")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        endpoint = self._get_endpoint("iex threshold securities", [symbol])
        params = {"date": date}
        return self._request("get", endpoint, params)

    def iex_short_interest(
        self, symbol: str = "market", date: Optional[str] = None
    ) -> dict:
        """
        Returns information on short interest positions for IEX listed stocks.

        https://iextrading.com/developer/docs/#iex-short-interest-list
        """
        valid_date = re.compile(r"^2\d\d\d[01]\d[0-3]\d$")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        endpoint = self._get_endpoint("iex short interest", [symbol])
        params = {"date": date}
        return self._request("get", endpoint, params)

    def stats(self, symbol: str) -> dict:
        """
        Returns key stats for a given company (e.g., market cap, dividends,
        financials).

        https://iextrading.com/developer/docs/#key-stats
        """
        endpoint = self._get_endpoint("key stats", [symbol])
        return self._request("get", endpoint, {})

    def largest_trades(self, symbol: str) -> dict:
        """
        Returns recent trades for the given symbol.

        https://iextrading.com/developer/docs/#largest-trades
        """
        endpoint = self._get_endpoint("largest trades", [symbol])
        return self._request("get", endpoint, {})

    def stock_list(self, list_type: str, displayPercent: bool = False) -> dict:
        """
        Returns the requested list.

        https://iextrading.com/developer/docs/#list
        """
        valid_lists = [
            "most active",
            "gainers",
            "losers",
            "iexvolume",
            "iexpercent",
            "infocus",
        ]
        if list_type.lower() not in valid_lists:
            raise ValueError("Specified list type is not a valid choice")
        endpoint = self._get_endpoint(f"list {list_type}", [])
        params = {"displayPercent": displayPercent}
        return self._request("get", endpoint, params)

    def logo(self, symbol: str) -> dict:
        """
        Returns a link to a image file of the company's logo.

        https://iextrading.com/developer/docs/#logo
        """
        endpoint = self._get_endpoint("logo", [symbol])
        return self._request("get", endpoint, {})

    def news(self, symbol: str, last: int = 10) -> dict:
        """
        Returns a list of recent news on a given symbol. The 'last' parameter.
        specifies how many documents to return

        https://iextrading.com/developer/docs/#news
        """
        if last > 50:
            raise ValueError("'last' parameter cannot be larger than 50")
        endpoint = self._get_endpoint("news", [symbol, str(last)])
        return self._request("get", endpoint, {})

    def ohlc(self, symbol: str) -> dict:
        """
        Returns the open, high, low, and close prices for a given company.

        https://iextrading.com/developer/docs/#ohlc
        """
        endpoint = self._get_endpoint("ohlc", [symbol])
        return self._request("get", endpoint, {})

    def peers(self, symbol: str) -> dict:
        """
        Returns the peers for a given company.

        https://iextrading.com/developer/docs/#peers
        """
        endpoint = self._get_endpoint("peers", [symbol])
        return self._request("get", endpoint, {})

    def previous(self, symbol: str) -> dict:
        """
        Returns the previous day adjusted price data for a single stock.

        https://iextrading.com/developer/docs/#previous
        """
        endpoint = self._get_endpoint("previous", [symbol])
        return self._request("get", endpoint, {})

    def price(self, symbol: str) -> dict:
        """
        Returns the IEX real time price, the 15 minute delayed market price, or
        the previous close price for a single stock.

        https://iextrading.com/developer/docs/#price
        """
        endpoint = self._get_endpoint("price", [symbol])
        return self._request("get", endpoint, {})

    def quote(self, symbol: str, displayPercent: bool = False) -> dict:
        """
        Returns the latest quote for a given company.

        https://iextrading.com/developer/docs/#quote
        """
        endpoint = self._get_endpoint("quote", [symbol])
        params = {"displayPercent": displayPercent}
        return self._request("get", endpoint, params)

    def relevant(self, symbol: str) -> dict:
        """
        Returns a response similar to the peers endpoint.

        https://iextrading.com/developer/docs/#relevant
        """
        endpoint = self._get_endpoint("relevant", [symbol])
        return self._request("get", endpoint, {})

    def sector_performance(self) -> dict:
        """
        Returns data on performance of various sectors.

        https://iextrading.com/developer/docs/#sector-performance
        """
        endpoint = self._get_endpoint("sector performance", [])
        return self._request("get", endpoint, {})

    def splits(self, symbol: str, date_range: str):
        """
        Returns the list of splits for a given company over a given range.

        https://iextrading.com/developer/docs/#splits
        """
        endpoint = self._get_endpoint("splits", [symbol, date_range])

        valid_dates = ("5y", "2y", "1y", "ytd", "6m", "3m", "1m")
        if date_range not in valid_dates:
            raise ValueError("Date range given is not valid")
        return self._request("get", endpoint, {})

    def timeseries(self, symbol: str, date_range: str, **kwargs) -> dict:
        """
        An alternate way of accessing the chart endpoint.

        https://iextrading.com/developer/docs/#time-series
        """
        return self.chart(symbol, date_range, **kwargs)

    def volume_by_venue(self, symbol: str):
        """
        Returns the 5 minute delayed and 30 day average consolidated volume
        percentage of a stock, by market.

        https://iextrading.com/developer/docs/#volume-by-venue
        """
        endpoint = self._get_endpoint("volume by venue", [symbol])
        return self._request("get", endpoint, {})

    def symbols(self) -> dict:
        """
        Returns an array of symbols IEX supports for trading.

        https://iextrading.com/developer/docs/#symbols
        """
        endpoint = self._get_endpoint("symbols", [])
        return self._request("get", endpoint, {})

    def iex_corp_actions(self, date: Optional[str] = None) -> dict:
        """
        returns an array of new issues, symbol and name changes, and deleted
        issues, as well as new firms, name changes, and deleted firms for
        IEX-listed securities.

        https://iextrading.com/developer/docs/#iex-corporate-actions
        """
        valid_date = re.compile(r"^2\d\d\d[01]\d[0-3]\d$")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        endpoint = self._get_endpoint("iex corp actions", [])
        endpoint = f"{endpoint}/{date}" if date else endpoint
        return self._request("get", endpoint, {})

    def iex_dividends(self, date: Optional[str] = None) -> dict:
        """
        Returns upcoming dividend information and other corporate actions, such
        as stock splits, for IEX-listed securities.

        https://iextrading.com/developer/docs/#iex-dividends
        """
        valid_date = re.compile(r"^2\d\d\d[01]\d[0-3]\d$")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        endpoint = self._get_endpoint("iex dividends", [])
        endpoint = f"{endpoint}/{date}" if date else endpoint
        return self._request("get", endpoint, {})

    def iex_next_day_ex_div(self, date: Optional[str] = None) -> dict:
        """
        Returns dividend declarations impacting IEX-listed securities.

        https://iextrading.com/developer/docs/#iex-next-day-ex-date
        """
        valid_date = re.compile(r"^2\d\d\d[01]\d[0-3]\d$")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        endpoint = self._get_endpoint("iex next day ex div", [])
        endpoint = f"{endpoint}/{date}" if date else endpoint
        return self._request("get", endpoint, {})

    def iex_symbols(self, date: Optional[str] = None) -> dict:
        """
        Returns an array of symbols IEX listed stocks.

        https://iextrading.com/developer/docs/#iex-listed-symbol-directory
        """
        valid_date = re.compile(r"^2\d\d\d[01]\d[0-3]\d$")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        endpoint = self._get_endpoint("iex symbols", [])
        endpoint = f"{endpoint}/{date}" if date else endpoint
        return self._request("get", endpoint, {})

    def tops(self, symbols: Optional[Union[List[str], str]] = None) -> dict:
        """
        Returns IEX’s aggregated best quoted bid and offer position in near
        real time for all securities on IEX’s displayed limit order book.

        https://iextrading.com/developer/docs/#tops
        """
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("tops", [])
        return self._request("get", endpoint, params)

    def last(self, symbols: Optional[Union[List[str], str]] = None) -> dict:
        """
        Returns trade data for executions on IEX. It is a near real time,
        intraday API that provides IEX last sale price, size and time.

        https://iextrading.com/developer/docs/#last
        """
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("last", [])
        return self._request("get", endpoint, params)

    def hist(self, date: Optional[str] = None) -> dict:
        """
        Returns the link to download the HIST pcap files for a given date.

        https://iextrading.com/developer/docs/#hist
        """
        valid_date = re.compile(r"^2\d\d\d[01]\d[0-3]\d$")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        params = {"date": date}
        endpoint = self._get_endpoint("hist download", [])
        return self._request("get", endpoint, params)

    def deep(self, symbol: str) -> dict:
        """
        Returns real-time depth of book quotations direct from IEX. The depth
        of book quotations received via DEEP provide an aggregated size of
        resting displayed orders at a price and side, and do not indicate the
        size or number of individual orders at any price level. Non-displayed
        orders and non-displayed portions of reserve orders are not represented
        in DEEP.

        https://iextrading.com/developer/docs/#deep
        """
        params = {"symbols": symbol}
        endpoint = self._get_endpoint("deep", [])
        return self._request("get", endpoint, params)

    def deep_book(self, symbols: Union[List[str], str]) -> dict:
        """
        Returns IEX’s bids and asks for given symbols.

        https://iextrading.com/developer/docs/#book60
        """
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("deep book", [])
        return self._request("get", endpoint, params)

    def deep_trades(
        self, symbols: Union[List[str], str], last: int = 20
    ) -> dict:
        """
        Returns a trade report message for every individual fill.

        https://iextrading.com/developer/docs/#trades
        """
        if last > 500:
            raise ValueError("'last' parameter cannot be larger than 500")
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("deep trades", [])
        return self._request("get", endpoint, params)

    def system_event(self) -> dict:
        """
        The System event message is used to indicate events that apply to the
        market or the data feed.

        https://iextrading.com/developer/docs/#system-event
        """
        endpoint = self._get_endpoint("system event", [])
        return self._request("get", endpoint, {})

    def trading_status(self, symbols: Union[List[str], str]) -> dict:
        """
        Returns the trading status for up to 10 symbols.

        https://iextrading.com/developer/docs/#trading-status
        """
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("trading status", [])
        return self._request("get", endpoint, params)

    def operational_halt(self, symbols: Union[List[str], str]) -> dict:
        """
        Returns the operational halt status for up to 10 symbols.

        https://iextrading.com/developer/docs/#operational-halt-status
        """
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("operational halt", [])
        return self._request("get", endpoint, params)

    def short_sale_price_test_status(
        self, symbols: Union[List[str], str]
    ) -> dict:
        """
        Used to indicate when a short sale price test restriction is in effect
        for a security.

        https://iextrading.com/developer/docs/#short-sale-price-test-status
        """
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("short sale price test status", [])
        return self._request("get", endpoint, params)

    def security_event(self, symbols: Union[List[str], str]) -> dict:
        """
        Used to indicate events that apply to a security (e.g., market open
        and close).

        https://iextrading.com/developer/docs/#security-event
        """
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("security event", [])
        return self._request("get", endpoint, params)

    def trade_break(
        self, symbols: Union[List[str], str], last: int = 20
    ) -> dict:
        """
        Trade break messages are sent when an execution on IEX is broken on
        that same trading day. Trade breaks are rare and only affect
        applications that rely upon IEX execution based data.

        https://iextrading.com/developer/docs/#trade-break
        """
        if last > 500:
            raise ValueError("'last' parameter cannot be larger than 500")
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("trade break", [])
        return self._request("get", endpoint, params)

    def iex_auction(self, symbols: Union[List[str], str]) -> dict:
        """
        DEEP broadcasts an Auction Information Message every one second between
        the Lock-in Time and the auction match for Opening and Closing
        Auctions, and during the Display Only Period for IPO, Halt, and
        Volatility Auctions. Only IEX listed securities are eligible for IEX
        Auctions.

        https://iextrading.com/developer/docs/#auction
        """
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("iex auction", [])
        return self._request("get", endpoint, params)

    def iex_official_price(self, symbols: Union[List[str], str]) -> dict:
        """
        The IEX Official Opening and Closing Prices (IEX listed stocks only).

        https://iextrading.com/developer/docs/#official-price
        """
        params = {"symbols": self._comma_sep_params(symbols)}
        endpoint = self._get_endpoint("iex official price", [])
        return self._request("get", endpoint, params)

    def iex_stats_intraday(self) -> dict:
        """
        Returns stats on IEX trading volume and mkt share.

        https://iextrading.com/developer/docs/#intraday
        """
        endpoint = self._get_endpoint("iex stats intraday", [])
        return self._request("get", endpoint, {})

    def iex_stats_recent(self) -> dict:
        """
        Returns stats on IEX trading volume and mkt share. Returns a minimum of
        the last five trading days up to all trading days of the current month.

        https://iextrading.com/developer/docs/#recent
        """
        endpoint = self._get_endpoint("iex stats recent", [])
        return self._request("get", endpoint, {})

    def iex_stats_records(self) -> dict:
        """
        Returns record stats on IEX trading volume and mkt share.

        https://iextrading.com/developer/docs/#records
        """
        endpoint = self._get_endpoint("iex stats records", [])
        return self._request("get", endpoint, {})

    def iex_historical(self, date: Optional[str] = None) -> dict:
        """
        Returns historical data for all exchanges related to volume and stats.

        https://iextrading.com/developer/docs/#historical-summary
        """
        valid_date = re.compile(r"^2\d\d\d[01]\d[0-3]\d$")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        endpoint = self._get_endpoint("iex historical", [])
        endpoint = f"{endpoint}/{date}" if date else endpoint
        return self._request("get", endpoint, {})

    def iex_historical_daily(
        self, date: Optional[str] = None, last: Optional[int] = None
    ) -> dict:
        """
        Returns historical data for all exchanges related to volume and stats.

        https://iextrading.com/developer/docs/#historical-summary
        """
        if last is None and date is None:
            raise ValueError("Either 'date' or 'last' must be defined")
        if last is not None and date is not None:
            raise ValueError("Both 'date' and 'last' cannot be defined")
        if last is not None and last > 90:
            raise ValueError("'last' parameter cannot be larger than 90")
        valid_date = re.compile(r"^2\d\d\d[01]\d([0-3]\d)?$")
        if date is not None and not valid_date.search(date):
            raise ValueError("Invalid date parameter provided")
        endpoint = self._get_endpoint("iex historical daily", [])
        params = {"date": date, "last": last}
        return self._request("get", endpoint, params)

    def market(self) -> dict:
        """
        Returns near real time traded volume on the markets.

        https://iextrading.com/developer/docs/#market
        """
        endpoint = self._get_endpoint("market", [])
        return self._request("get", endpoint, {})
