import shutil
import json
import datetime
from typing import List

from .poems import Poem
from .utility import datetime_to_timestamp


def save_poems_json(poems: List[Poem], filename: str):
    struct = []
    for p in poems:
        for parent in p.parents:
            if "body" in parent:
                del(parent["body"])  # remove converted parent comment body to save space

        struct.append({
            "timestamp": datetime_to_timestamp(p.datetime),
            "link": p.link,
            "submission_user": p.submission_user,
            "submission_url": p.submission_url,
            "submission_title": p.submission_title,
            "noimg": p.noimg,
            "imgfilename": p.imgfilename,
            "parents": p.parents,
            "orig_content": p.orig_content,
            "orig_submission_content": p.orig_submission_content,
            "gold": p.gold,
            "score": p.score,
        })
    shutil.copy(filename, "prev_" + filename)
    with open(filename, "w") as f:
        f.write(json.dumps(struct, sort_keys=True, indent=4))


def upgrade_link(link: str) -> str:
    """
    The permalink returned by praw used to have no trailing slash,
    here we add one if it wasn't there already.
    This should only be relevant the first time this runs (hopefully...).
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
                        score=p.get("score", None)
                    ))
    except FileNotFoundError:
        pass
    return poems
