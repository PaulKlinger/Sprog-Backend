import datetime
from typing import List
import praw

from .md_to_latex import poem_md_to_latex, md_to_latex, title_escape, username_escape
from .reddit_helpers import get_all_parents, get_comment_from_link, get_comments, CommentMissingException, get_comment_awards
from .utility import permalink_to_full_link


class Poem(object):
    def __init__(self, timestamp, link,
                 submission_user, submission_url, submission_title,
                 parents, noimg, imgfilename, orig_content, orig_submission_content,
                 gold, silver, platinum, score):
        self.datetime = timestamp
        self.link = link
        self.submission_user = submission_user
        self.submission_url = submission_url
        self.submission_title = submission_title
        self.parents = parents
        self.noimg = noimg
        self.imgfilename = imgfilename
        self.orig_content = orig_content
        self.orig_submission_content = orig_submission_content
        self.gold = gold
        self.silver = silver
        self.platinum = platinum
        self.score = score

        self.content = None
        self.submission_content = None

    @classmethod
    def from_comment(cls, comment, is_submission=False):
        timestamp = datetime.datetime.utcfromtimestamp(comment.created_utc)
        link = permalink_to_full_link(comment.permalink)

        parents = []
        submission_url = None
        submission = None
        if not is_submission:
            submission, parent_comments = get_all_parents(comment)
            for p in parent_comments:
                silver, gold, platinum = get_comment_awards(p)
                parents.append({"author": username_escape(p.author),
                                "orig_body": p.body,
                                "link": permalink_to_full_link(p.permalink),
                                "timestamp": p.created_utc,
                                "gold": gold,
                                "silver": silver,
                                "platinum": platinum,
                                "score": p.score})

            submission_user = username_escape(submission.author)

            if not submission.is_self:
                submission_url = submission.url

            submission_title = title_escape(submission.title)
        else:
            submission_title = title_escape(comment.title)
            submission_user = username_escape(comment.author)
            if not comment.is_self:
                submission_url = comment.url

        noimg = False
        imgfilename = None
        silver, gold, platinum = get_comment_awards(comment)
        return cls(timestamp, link, submission_user, submission_url, submission_title,
                   parents, noimg, imgfilename, comment.body if not is_submission else comment.selftext,
                   submission.selftext if not is_submission else "",
                   gold, silver, platinum,
                   comment.score)

    def to_latex(self):
        self.content = poem_md_to_latex(self.orig_content, self.datetime)
        self.submission_content = md_to_latex(self.orig_submission_content)
        for parent in self.parents:
            if parent["orig_body"]:
                parent["body"] = md_to_latex(parent["orig_body"])
            else:
                print("No orig_body???")

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def get_poems(reddit: praw.Reddit, user_name: str, poems: List[Poem] = None) -> List[Poem]:
    if poems is None:
        poems = []
    newpoems = []
    known_links = {p.link for p in poems}
    now = datetime.datetime.utcnow()
    for c in get_comments(reddit, user_name):
        comment_link = permalink_to_full_link(c.permalink)
        print(comment_link)
        # print(".", end="", flush=True)
        if comment_link not in known_links:
            try:
                newpoems.append(Poem.from_comment(c))
            except Exception as e:
                print(e)
                print(len(poems))
        c_time = datetime.datetime.utcfromtimestamp(c.created_utc)
        # break if poem is older than 30 days (not when we get the first old poem)
        # this way poems which were skipped due to errors are tried again the next time
        if now - c_time > datetime.timedelta(days=30):
            break

    print()
    poems = newpoems + poems
    poems.sort(key=lambda x: x.datetime, reverse=True)
    return poems


def update_poems(reddit: praw.Reddit, user_name: str, poems: List[Poem], deleted_poems: List[Poem],
                 cutoff_age_days: int = 30) -> (List[Poem], List[Poem]):
    # TODO: add submission updating (for poems that are submissions)
    for p in poems:
        print(".", end="", flush=True)
        if (cutoff_age_days is not None
                and (datetime.datetime.today() - p.datetime) > datetime.timedelta(days=cutoff_age_days)):
            break
        try:
            c = get_comment_from_link(reddit, p.link)
            p.silver, p.gold, p.platinum = get_comment_awards(c)
            p.score = c.score
            p.orig_content = c.body

        except Exception as e:
            print("-------")
            # if comment is missing and this poem is not actually a submission
            if isinstance(e, CommentMissingException) \
                    and p.submission_user.lower() != user_name.replace("_", "\\_").lower():
                p.deleted = True
                print("Poem deleted.")
            print("Error while updating poem")
            print(p.datetime.isoformat(), p.link)
            print(e)
            print("--------")

    poems_out = [p for p in poems if not getattr(p, "deleted", False)]
    deleted_poems = [p for p in poems if getattr(p, "deleted", False)] + deleted_poems
    deleted_poems.sort(key=lambda x: x.datetime, reverse=True)
    print()
    return poems_out, deleted_poems
