import datetime
import statistics
import pandas
import matplotlib.pyplot as plt
from collections import Counter

plt.style.use('ggplot')


def id_from_link(link):
    """create a unique (hopefully) from permalink (for latex labels)"""
    allowedchars = "abcdefghijklmnopqrstuvwxyz"
    allowedchars += allowedchars.upper()
    allowedchars += "0123456789"
    return "".join(c for c in link if c in allowedchars)[-10:]


def prettyp_seconds(seconds):
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


def posting_time_stats(poems):
    diffs = [((p.datetime - datetime.datetime.utcfromtimestamp(p.parents[-1]["timestamp"])).total_seconds(),
              id_from_link(p.link))
             for p in poems
             if p.parents and p.parents[-1].get("timestamp", None)]
    med_seconds = statistics.median(map(lambda x: x[0], diffs))
    min_seconds, min_link = min(diffs, key=lambda x: x[0])
    return prettyp_seconds(med_seconds), prettyp_seconds(min_seconds), min_link


def make_graphs(poems):
    months = [p.datetime.strftime("%Y %m") for p in poems]
    # initialize all months from min to max to zero to account for ones without poems
    # (this is not actually needed yet)
    minyear, minmonth = map(int, min(months).split(" "))
    maxyear, maxmonth = map(int, max(months).split(" "))
    counts = Counter({"{:02d} {:02d}".format(y, m): 0
                      for m in range(1, 13)
                      for y in range(minyear, maxyear + 1)
                      if not ((y == minyear and m < minmonth)
                              or (y == maxyear and m > maxmonth))})
    counts.update(months)
    data = list(counts.items())
    data.sort(key=lambda x: x[0])
    df = pandas.DataFrame(x[1] for x in data)
    plot = df.plot.bar(legend=False, figsize=(10, 4))
    ticks = [x[0] if i == 0 or x[0][-2:] == "01" else x[0][-2:] for i, x in enumerate(data)]
    plot.set_xticklabels(ticks)
    plot.set_ylabel("# of Poems")
    plt.savefig("tmp/monthsplot.pdf", bbox_inches="tight")
