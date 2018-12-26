import shutil
import json
import datetime
import gzip
from typing import List, Union

from .poems import Poem
from .utility import datetime_to_timestamp


def save_poems_json(poems: List[Poem], filename: str, time_limit: Union[datetime.datetime, None]):
    struct = []

    for p in poems:
        for parent in p.parents:
            if "body" in parent:
                del(parent["body"])  # remove converted parent comment body to save space

        poem_data = {
            "timestamp": datetime_to_timestamp(p.datetime),
            "link": downgrade_link(p.link),
            "submission_user": p.submission_user,
            "submission_url": p.submission_url,
            "submission_title": p.submission_title,
            "noimg": p.noimg,
            "imgfilename": p.imgfilename,
            "parents": downgrade_parents(p.parents),
            "orig_content": p.orig_content,
            "orig_submission_content": p.orig_submission_content,
            "gold": p.gold,
            "silver": p.silver,
            "platinum": p.platinum,
            "score": p.score,
        }
        if time_limit is None or p.datetime > time_limit:
            struct.append(poem_data)

    try:
        shutil.copy(filename, "prev_" + filename)
    except FileNotFoundError:
        pass

    json_str = json.dumps(struct, sort_keys=True, indent=4).encode("utf-8")
    with open(filename, "wb") as f:
        f.write(json_str)

    with gzip.open(filename + ".gz", "wb") as f:
        f.write(json_str)


def downgrade_link(link: str) -> str:
    """
    Internally this program uses links with trailing slashes, as returned by new versions of praw.
    To ensure compatibility with the Android app we remove these in the json file.
    """
    if link and link[-1] == "/":
        link = link[:-1]
    return link


def downgrade_parents(parents: List[dict]) -> List[dict]:
    """
    Applies downgrade_link for all parent comments
    """
    for p in parents:
        p["link"] = downgrade_link(p["link"])
    return parents


def upgrade_link(link: str) -> str:
    """
    The permalink returned by praw used to have no trailing slash.
    We use this old version in the json file add one here to make
    sure it's consistent with new poems.
    """
    if link and link[-1] != "/":
        link += "/"
    return link


def upgrade_parents(parents: List[dict]) -> List[dict]:
    """
    Does the link upgrade of upgrade_link for all parent comments
    """
    for p in parents:
        p["link"] = upgrade_link(p["link"])
    return parents


def load_poems_json(filename: str) -> List[Poem]:
    poems = []
    try:
        with open(filename, "r") as f:
            struct = json.loads(f.read())
            if struct:
                for p in struct:
                    poems.append(Poem(
                        timestamp=datetime.datetime.utcfromtimestamp(p["timestamp"]),
                        link=upgrade_link(p["link"]),
                        submission_user=p["submission_user"],
                        submission_url=p["submission_url"],
                        submission_title=p["submission_title"],
                        parents=upgrade_parents(p["parents"]),
                        noimg=p["noimg"],
                        imgfilename=p["imgfilename"],
                        orig_content=p.get("orig_content", None),
                        orig_submission_content=p.get("orig_submission_content", None),
                        gold=p.get("gold", None),
                        silver=p.get("silver", 0),
                        platinum=p.get("platinum", 0),
                        score=p.get("score", None)
                    ))
    except FileNotFoundError:
        pass
    return poems
