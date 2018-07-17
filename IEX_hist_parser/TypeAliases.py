from typing import Union
from . import messages

AllMessages = Union[
    messages.ShortSalePriceSale,
    messages.TradeBreak,
    messages.AuctionInformation,
    messages.TradeReport,
    messages.OfficialPrice,
    messages.SystemEvent,
    messages.SecurityDirective,
    messages.TradingStatus,
    messages.OperationalHalt,
    messages.QuoteUpdate,
]
