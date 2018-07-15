"""
This script examines a single pcap file from IEX to understand:
1. The distribution of message types
2. Provide another benchmark datapoint on Parser
3. Understand the rate at which IEX sends messages (how many messages/second)
4. Understand overall volume of messages
"""

from IEX_hist_parser.IEXparser import Parser
import IEX_hist_parser.messages as messages
from datetime import datetime, timezone
from timeit import default_timer


message_types = {
    b"\x53": {
        "str": "System Event Message",
        "cls": messages.SystemEvent,
        "fmt": "<Bq",
    },
    b"\x44": {
        "str": "Security Directory Message",
        "cls": messages.SecurityDirective,
        "fmt": "<Bq8sLqB",
    },
    b"\x48": {
        "str": "Trading Status Message",
        "cls": messages.TradingStatus,
        "fmt": "<1sq8s4s",
    },
    b"\x4f": {
        "str": "Operational Halt Status Message",
        "cls": messages.OperationalHalt,
        "fmt": "<1sq8s",
    },
    b"\x50": {
        "str": "Short Sale Price Test Status Message",
        "cls": messages.ShortSalePriceSale,
        "fmt": "<Bq8s1s",
    },
    b"\x51": {
        "str": "Quote Update Message",
        "cls": messages.QuoteUpdate,
        "fmt": "<Bq8sLqqL",
    },
    b"\x54": {
        "str": "Trade Report Message",
        "cls": messages.TradeReport,
        "fmt": "<Bq8sLqq",
    },
    b"\x58": {
        "str": "Official Price Message",
        "cls": messages.OfficialPrice,
        "fmt": "<1sq8sq",
    },
    b"\x42": {
        "str": "Trade Break Message",
        "cls": messages.TradeBreak,
        "fmt": "<1sq8sqq",
    },
    b"\x41": {
        "str": "Auction Information Message",
        "cls": messages.AuctionInformation,
        "fmt": "<1sq8sLqqL1sBLqqqq",
    },
}
DECODE_FMT = {msg[0]: message_types[msg]["fmt"] for msg in message_types}
MSG_CLS = {msg[0]: message_types[msg]["cls"] for msg in message_types}


def message_distribution(file_path):
    """
    Figure out the frequency of each message type in one pcap file.
    """
    start = default_timer()
    p = Parser(file_path)
    dist = {}
    num_messages = 0
    min_time = datetime(2019, 1, 1, tzinfo=timezone.utc)
    max_time = datetime(2016, 1, 1, tzinfo=timezone.utc)

    try:
        while True:
            cur_message = p.get_next_message()
            dist[p.message_type] = dist.get(p.message_type, 0) + 1

            if cur_message.date_time > max_time:
                max_time = cur_message.date_time
            elif cur_message.date_time < min_time:
                min_time = cur_message.date_time

            if num_messages % 10 ** 6 == 0:
                print(
                    f"Processed {num_messages:,d} messages - cur datetime = "
                    f"{cur_message.date_time}"
                )

            num_messages += 1

    except StopIteration:
        pass

    total_time = (max_time - min_time).total_seconds()
    total_hours = total_time / 3600
    msg_rate = num_messages // total_hours
    total = default_timer() - start
    bytes_read = p.bytes_read
    mb_read = bytes_read / (1024 ** 2)
    msg_rate = int(num_messages // total)
    mb_rate = mb_read / total

    print(
        f"Parsed {num_messages:,d} messages in {total:,.0f} s-- {msg_rate:,d} "
        f"msgs per second -- {mb_rate:.2f} mb/s"
    )
    print(
        f"Min Datetime = {min_time}, Max Datetime = {max_time} -- "
        f"{num_messages/total_time:,.0f} msgs/s"
    )
    for msg_type in dist:
        print("|" + MSG_CLS[msg_type].__name__.ljust(25, "."), end="|")
        print(str(dist[msg_type]).rjust(20, "."), end="|")
        print(
            (str(round(dist[msg_type] / num_messages * 100, 1)) + "%").rjust(5),
            end="|\n",
        )


if __name__ == "__main__":
    file_path = r"C:\Users\luiz_\Dropbox\Personal\Python\Programs\IEX_hist_parser\IEX_hist_parser\IEX TOPS Sample\20180103_IEXTP1_TOPS1.6.pcap"
    message_distribution(file_path)
