from IEX_hist_parser.IEXparser import Parser
from IEX_hist_parser.messages import MessageDecoder
from datetime import datetime, timezone
from timeit import default_timer


def hourly_message_distribution(file_path):
    """
    Figure out the frequency of each message type in one pcap file by hour.
    """
    start = default_timer()
    dist = {}
    cur_hour = None
    num_messages = 0
    min_time = datetime(2019, 1, 1, tzinfo=timezone.utc)
    max_time = datetime(2016, 1, 1, tzinfo=timezone.utc)

    with Parser(file_path) as p:
        for message in p:
            cur_hour = message.date_time.hour
            if not dist.get(cur_hour):
                dist[cur_hour] = {}
            dist[cur_hour][p.message_type] = (
                dist[cur_hour].get(p.message_type, 0) + 1
            )

            if message.date_time > max_time:
                max_time = message.date_time
            elif message.date_time < min_time:
                min_time = message.date_time

            if num_messages % 10 ** 6 == 0:
                print(
                    f"Processed {num_messages:,d} messages - cur datetime = "
                    f"{message.date_time}"
                )

            num_messages += 1

    total_time = (max_time - min_time).total_seconds()
    total_hours = total_time / 3600
    msg_rate = num_messages // total_hours
    total = default_timer() - start
    bytes_read = p.bytes_read
    mb_read = bytes_read / (1024 ** 2)
    msg_rate = int(num_messages // total)
    mb_rate = mb_read / total
    MSG_CLS = MessageDecoder().MSG_CLS

    print(
        f"Parsed {num_messages:,d} messages in {total:,.0f} s-- {msg_rate:,d} "
        f"msgs per second -- {mb_rate:.2f} mb/s"
    )
    print(
        f"Min Datetime = {min_time}, Max Datetime = {max_time} -- "
        f"{num_messages/total_time:,.0f} msgs/s"
    )
    for hour in dist:
        print(f"{hour} to {hour + 1}")
        for msg_type in dist[hour]:
            print("|" + MSG_CLS[msg_type].__name__.ljust(25, "."), end="|")
            print(str(dist[hour][msg_type]).rjust(20, "."), end="|")
            print(
                (
                    str(round(dist[hour][msg_type] / num_messages * 100, 1))
                    + "%"
                ).rjust(5),
                end="|\n",
            )


if __name__ == "__main__":
    file_path = r"C:\Users\luiz_\Dropbox\Personal\Python\Programs\IEX_hist_parser\IEX_hist_parser\IEX TOPS Sample\20180103_IEXTP1_TOPS1.6.pcap"
    hourly_message_distribution(file_path)
