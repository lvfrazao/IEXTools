API Client
==========

Usage
-----

Purpose: Interact with the IEX web API. All methods return Python dictionaries.

The web API has a large number of endpoints returning data::

   >>> from IEXTools import IEXAPI
   >>> api = IEXAPI()
   >>> meths = [d for d in dir(api) if not d.startswith('_')]
   >>> for i, j, k in zip(meths[::3], meths[1::3], meths[2::3]):
   ...     print(i.ljust(20), j.ljust(20), k.ljust(20))
   ...
   BASE                 batch                book
   chart                collections          company
   crypto               deep                 deep_book
   deep_trades          delayed_quote        dividends
   earnings             earnings_today       effective_spread
   financials           hist                 iex_auction
   iex_corp_actions     iex_dividends        iex_historical
   iex_historical_daily iex_next_day_ex_div  iex_official_price
   iex_short_interest   iex_stats_intraday   iex_stats_recent
   iex_stats_records    iex_symbols          iex_threshold_securities
   largest_trades       last                 logo
   market               news                 ohlc
   operational_halt     peers                previous
   price                quote                relevant
   sector_performance   security_event       short_sale_price_test_status
   splits               stats                stock_list
   symbols              system_event         timeout
   timeseries           today_ipos           tops
   trade_break          trading_status       upcoming_ipos


Users should consult the docstrings of a given function or IEX's docs for additional information on how to use a given endpoint. All endpoints documented in the IEX API docs are implemented in this class::

   >>> help(api.ohlc)
   Help on method ohlc in module IEX_API:
   
   ohlc(symbol: str) -> dict method of IEX_API.IEX_API instance
       Returns the open, high, low, and close prices for a given company.
   
       https://iextrading.com/developer/docs/#ohlc
   
   >>> apple_ohlc = api.ohlc('aapl')
   >>> print(IEX_API.pretty_json(apple_ohlc))
   {
       "close": {
           "price": 204.47,
           "time": 1541797200568
       },
       "high": 206.01,
       "low": 202.25,
       "open": {
           "price": 205.55,
           "time": 1541773800180
       }
   }


All symbols available on the API can be retrived using the `symbols` method::

   >>> all_symbols = api.symbols()
   >>> len(all_symbols)
   8756
   >>> api.symbols()[1]
   {'symbol': 'AA', 'name': 'Alcoa Corporation', 'date': '2018-11-09', 'isEnabled': True, 'type': 'cs', 'iexId': '12042'}

Module Docs
-----------

.. automodule:: IEXTools.IEX_API
   :members:

.. autoclass:: IEXAPI
    :members:

Indices and tables
------------------
 
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
