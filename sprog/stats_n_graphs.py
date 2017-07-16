import datetime as dt
import statistics
import re
# need to set matplotlib backend before importing pyplot,
#  else an error occurs if running without gui
import matplotlib
matplotlib.use('Agg')
import pandas
import matplotlib.pyplot as plt

plt.style.use('ggplot')


def id_from_link(link) -> str:
    """create a unique (hopefully) from permalink (for latex labels)"""
    allowedchars = "abcdefghijklmnopqrstuvwxyz"
    allowedchars += allowedchars.upper()
    allowedchars += "0123456789"
    return "".join(c for c in link if c in allowedchars)[-10:]


def prettyp_seconds(seconds) -> str:
    out = []
    if seconds > 60 * 60:
        out.append("{:.0f}h".format(seconds // (60 * 60)))
        seconds %= (60 * 60)
    if seconds > 60:
        out.append("{:.0f}m".format(seconds // 60))
        seconds %= 60
    if seconds > 0:
        out.append("{:.0f}s".format(seconds))
    return " ".join(out)


def posting_time_stats(poems) -> (str, str, str):
    diffs = [((p.datetime - dt.datetime.utcfromtimestamp(p.parents[-1]["timestamp"])).total_seconds(),
              id_from_link(p.link))
             for p in poems
             if p.parents and p.parents[-1].get("timestamp", None)]
    med_seconds = statistics.median(map(lambda x: x[0], diffs))
    min_seconds, min_link = min(diffs, key=lambda x: x[0])
    return prettyp_seconds(med_seconds), prettyp_seconds(min_seconds), min_link


def total_words(poems) -> int:
    return sum(len(re.findall(r"\w+", p.content)) for p in poems)


def make_graphs(poems) -> None:
    data = pandas.DataFrame(((p.datetime, p.gold, p.score,
                          (p.datetime - dt.datetime.utcfromtimestamp(p.parents[-1]["timestamp"])).total_seconds()
                          if p.parents and "timestamp" in p.parents[-1] else None,
                          )
                         for p in poems), columns=("t", "gold", "karma", "delay"))
    data.sort_values("t", inplace=True)
    data.set_index("t", inplace=True, drop=False)

    # poems per month
    monthsdata = data["gold"].resample("1m").count().fillna(0)
    ticks = ["{} {:02d}".format(x[0].year, x[0].month) if i == 0 or x[0].month == 1 else "{:02d}".format(x[0].month) for
             i, x in enumerate(monthsdata.items())]
    plot = monthsdata.plot.bar(figsize=(10, 4))
    plot.set_xticklabels(ticks)
    plot.set_ylabel("# of Poems")
    plot.set_xlabel("")
    plt.savefig("tmp/monthsplot.pdf", bbox_inches="tight")
    plt.close()

    # Rolling 30 day mean of poem karma
    rollplot = (data["karma"].rolling(center=False, window="30d", min_periods=5).mean()
                .resample("7d").mean().dropna().plot())
    rollplot.set_xlabel("")
    rollplot.set_ylabel("karma / poem")
    plt.savefig("tmp/rollingkarmaplot.pdf", bbox_inches="tight")
    plt.close()

    # rolling 60min mean of karma vs posting time
    timekarmaplot = (data.groupby(
        by=lambda x: dt.datetime.combine(dt.date(1970, 1, 1) if data["t"].loc[x].hour > 6 else dt.date(1970, 1, 2),
                                         data["t"].loc[x].time())
        ).mean()["karma"]
         .rolling(center=False, window="60min", min_periods=20).mean()
         .resample("6T").mean()
         .dropna().plot())
    timekarmaplot.set_ylabel("karma / poem")
    timekarmaplot.set_xlabel("posting time")
    plt.savefig("tmp/timekarmaplot.pdf", bbox_inches="tight")
    plt.close()
