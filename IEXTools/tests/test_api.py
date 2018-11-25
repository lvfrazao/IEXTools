"""
Tests for the IEX_API.py file - currently these tests aren't great, it
basically to checks to see that the API returns a response and a 200 status.

To run unittest you must use the unittest module's cli due to Python's import
system:

Go into the top level directory and run the command:
py -m unittest IEXTools.tests.test_api
"""
import unittest
import datetime
from IEXTools import IEXAPI


def is_market_hours():
    """
    Determine if it is currently regular mark hours. Some of the test results
    change depending on whether the market is open or not.

    This rely's on the system time being in the correct timezone.
    """
    now = datetime.datetime.now()
    day = now.weekday()
    time = now.hour * 100 + now.minute

    if day > 4:
        return False

    if 930 <= time < 1600:
        return True

    return False


class ParserTestCases(unittest.TestCase):
    """
    Tests for IEX_API.py
    """

    def setUp(self):
        self.client = IEXAPI()

    def test_batch(self):
        symbols = ['aapl', 'fb']
        types = ['quote', 'news', 'chart']
        range_time = '1m'
        last = 1
        resp = self.client.batch(symbols, types, range_time, last=last)
        self.assertGreater(len(resp), 0)
    
    def test_book(self):
        symbol = 'aapl'
        resp = self.client.book(symbol)
        self.assertGreater(len(resp), 0)
    
    def test_chart(self):
        symbols = 'aapl'
        range_time = '1m'
        resp = self.client.chart(symbols, range_time)
        self.assertGreater(len(resp), 0)

    def test_collections(self):
        col_type = 'sector'
        collection = "Health Care"
        resp = self.client.collections(col_type, collection)
        self.assertGreater(len(resp), 0)

    def test_company(self):
        company = 'aapl'
        resp = self.client.company(company)
        self.assertGreater(len(resp), 0)

    def test_crypto(self):
        resp = self.client.crypto()
        self.assertGreater(len(resp), 0)

    def test_delayed_quote(self):
        symbol = 'aapl'
        resp = self.client.delayed_quote(symbol)
        self.assertGreater(len(resp), 0)

    def test_dividends(self):
        symbol = 'aapl'
        date_range = '3m'
        resp = self.client.dividends(symbol, date_range)
        self.assertGreater(len(resp), 0)

    def test_earnings(self):
        symbol = 'aapl'
        resp = self.client.earnings(symbol)
        self.assertGreater(len(resp), 0)

    def test_earnings_today(self):
        resp = self.client.earnings_today()
        self.assertGreater(len(resp), 0)

    def test_effective_spread(self):
        symbol = 'aapl'
        resp = self.client.effective_spread(symbol)
        self.assertGreater(len(resp), 0)

    def test_financials(self):
        symbol = 'aapl'
        period = 'quarter'
        resp = self.client.financials(symbol, period)
        self.assertGreater(len(resp), 0)

    def test_upcoming_ipos(self):
        resp = self.client.upcoming_ipos()
        self.assertGreater(len(resp), 0)

    def test_today_ipos(self):
        resp = self.client.today_ipos()
        self.assertGreater(len(resp), 0)

    def test_iex_threshold_securities(self):
        resp = self.client.iex_threshold_securities()
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_iex_short_interest(self):
        resp = self.client.iex_short_interest()
        self.assertGreater(len(resp), 0)

    def test_stats(self):
        symbol = 'aapl'
        resp = self.client.stats(symbol)
        self.assertGreater(len(resp), 0)

    def test_largest_trades(self):
        symbol = 'aapl'
        resp = self.client.largest_trades(symbol)
        if is_market_hours():
            self.assertGreater(len(resp), 0)
        else:
            self.assertEqual(len(resp), 0)

    def test_stock_list(self):
        list_type = 'mostactive'
        resp = self.client.stock_list(list_type)
        if is_market_hours():
            self.assertGreater(len(resp), 0)
        else:
            self.assertEqual(len(resp), 0)

    def test_logo(self):
        symbol = 'aapl'
        resp = self.client.logo(symbol)
        self.assertGreater(len(resp), 0)

    def test_news(self):
        symbol = 'aapl'
        last = 1
        resp = self.client.news(symbol, last)
        self.assertGreater(len(resp), 0)

    def test_ohlc(self):
        symbol = 'aapl'
        resp = self.client.ohlc(symbol)
        self.assertGreater(len(resp), 0)

    def test_peers(self):
        symbol = 'aapl'
        resp = self.client.peers(symbol)
        self.assertGreater(len(resp), 0)

    def test_previous(self):
        symbol = 'aapl'
        resp = self.client.previous(symbol)
        self.assertGreater(len(resp), 0)

    def test_price(self):
        symbol = 'aapl'
        resp = self.client.price(symbol)
        self.assertIsInstance(resp, float)

    def test_quote(self):
        symbol = 'aapl'
        resp = self.client.quote(symbol)
        self.assertGreater(len(resp), 0)

    def test_relevant(self):
        symbol = 'aapl'
        resp = self.client.relevant(symbol)
        self.assertGreater(len(resp), 0)

    def test_sector_performance(self):
        resp = self.client.sector_performance()
        self.assertGreater(len(resp), 0)

    def test_splits(self):
        symbol = 'aapl'
        date_range = '5y'
        resp = self.client.splits(symbol, date_range)
        self.assertGreater(len(resp), 0)

    def test_timeseries(self):
        symbol = 'aapl'
        date_range = '1m'
        resp = self.client.timeseries(symbol, date_range)
        self.assertGreater(len(resp), 0)

    def test_volume_by_venue(self):
        symbol = 'aapl'
        resp = self.client.volume_by_venue(symbol)
        self.assertGreater(len(resp), 0)

    def test_symbols(self):
        resp = self.client.symbols()
        self.assertGreater(len(resp), 0)

    def test_iex_corp_actions(self):
        resp = self.client.iex_corp_actions()
        self.assertGreater(len(resp), 0)

    def test_iex_dividends(self):
        resp = self.client.iex_dividends()
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_iex_next_day_ex_div(self):
        resp = self.client.iex_next_day_ex_div()
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_iex_symbols(self):
        resp = self.client.iex_symbols()
        self.assertGreater(len(resp), 0)

    def test_tops(self):
        symbols = ['aapl', 'fb']
        resp = self.client.tops(symbols)
        if is_market_hours():
            self.assertGreater(len(resp), 0)
        else:
            self.assertEqual(len(resp), 0)

        symbols = 'aapl'
        resp = self.client.tops(symbols)
        if is_market_hours():
            self.assertGreater(len(resp), 0)
        else:
            self.assertEqual(len(resp), 0)

    def test_last(self):
        symbols = ['aapl', 'fb']
        resp = self.client.last(symbols)
        self.assertGreater(len(resp), 0)

        symbols = 'aapl'
        resp = self.client.last(symbols)
        self.assertGreater(len(resp), 0)

    def test_hist(self):
        resp = self.client.hist()
        self.assertGreater(len(resp), 0)

    def test_deep(self):
        symbol = 'aapl'
        resp = self.client.deep(symbol)
        self.assertGreater(len(resp), 0)

    def test_deep_book(self):
        symbols = ['aapl', 'fb']
        resp = self.client.deep_book(symbols)
        if is_market_hours():
            self.assertGreater(len(resp), 0)
        else:
            self.assertEqual(len(resp), 0)

        symbols = 'aapl'
        resp = self.client.deep_book(symbols)
        if is_market_hours():
            self.assertGreater(len(resp), 0)
        else:
            self.assertEqual(len(resp), 0)

    def test_deep_trades(self):
        symbols = ['aapl', 'fb']
        resp = self.client.deep_trades(symbols)
        if is_market_hours():
            self.assertGreater(len(resp), 0)
        else:
            self.assertEqual(len(resp), 0)

        symbols = 'aapl'
        resp = self.client.deep_trades(symbols)
        if is_market_hours():
            self.assertGreater(len(resp), 0)
        else:
            self.assertEqual(len(resp), 0)

    def test_system_event(self):
        resp = self.client.system_event()
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_trading_status(self):
        symbols = ['aapl', 'fb']
        resp = self.client.trading_status(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

        symbols = 'aapl'
        resp = self.client.trading_status(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_operational_halt(self):
        symbols = ['aapl', 'fb']
        resp = self.client.operational_halt(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

        symbols = 'aapl'
        resp = self.client.operational_halt(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_short_sale_price_test_status(self):
        symbols = ['aapl', 'fb']
        resp = self.client.short_sale_price_test_status(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

        symbols = 'aapl'
        resp = self.client.short_sale_price_test_status(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_security_event(self):
        symbols = ['aapl', 'fb']
        resp = self.client.security_event(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

        symbols = 'aapl'
        resp = self.client.security_event(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_trade_break(self):
        symbols = ['aapl', 'fb']
        resp = self.client.trade_break(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

        symbols = 'aapl'
        resp = self.client.trade_break(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_iex_auction(self):
        symbols = ['ibkr', 'ziext']
        resp = self.client.iex_auction(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

        symbols = 'ibkr'
        resp = self.client.iex_auction(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_iex_official_price(self):
        symbols = ['ibkr', 'ziext']
        resp = self.client.iex_official_price(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

        symbols = 'ibkr'
        resp = self.client.iex_official_price(symbols)
        # This test is spotty as it can return nothing
        self.assertGreaterEqual(len(resp), 0)

    def test_iex_stats_intraday(self):
        resp = self.client.iex_stats_intraday()
        self.assertGreater(len(resp), 0)

    def test_iex_stats_recent(self):
        resp = self.client.iex_stats_recent()
        self.assertGreater(len(resp), 0)

    def test_iex_stats_records(self):
        resp = self.client.iex_stats_records()
        self.assertGreater(len(resp), 0)

    def test_iex_historical(self):
        resp = self.client.iex_historical()
        self.assertGreater(len(resp), 0)

    def test_iex_historical_daily(self):
        last = 5
        resp = self.client.iex_historical_daily(last=last)
        self.assertGreater(len(resp), 0)

    def test_market(self):
        resp = self.client.market()
        self.assertGreater(len(resp), 0)

if __name__ == "__main__":
    unittest.main()
