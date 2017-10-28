import datetime
from typing import List
import praw

from .md_to_latex import poem_md_to_latex, md_to_latex, title_escape, username_escape
from .reddit_helpers import get_all_parents, get_comment_from_link, get_comments, CommentMissingException
from .utility import permalink_to_full_link


class Poem(object):
    def __init__(self, timestamp, link,
                 submission_user, submission_url, submission_title,
                 parents, noimg, imgfilename, orig_content, orig_submission_content, gold, score):
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
                parents.append({"author": username_escape(p.author),
                                "orig_body": p.body,
                                "link": permalink_to_full_link(p.permalink),
                                "timestamp": p.created_utc,
                                "gold": p.gilded, "score": p.score})

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
        return cls(timestamp, link, submission_user, submission_url, submission_title,
                   parents, noimg, imgfilename, comment.body if not is_submission else comment.selftext,
                   submission.selftext if not is_submission else "",
                   comment.gilded, comment.score)

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
    known_links = [p.link.split("//")[1] for p in poems]
    now = datetime.datetime.utcnow()
    for c in get_comments(reddit, user_name):
        print(".", end="", flush=True)
        if permalink_to_full_link(c.permalink) not in known_links:
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


def update_poems(reddit: praw.Reddit, user_name: str, poems: List[Poem], deleted_poems: List[Poem]) -> (List[Poem], List[Poem]):
    # TODO: add submission updating (for poems that are submissions)
    for p in poems:
        print(".", end="", flush=True)
        if (datetime.datetime.today() - p.datetime) > datetime.timedelta(days=30):
            break
        try:
            c = get_comment_from_link(reddit, p.link)
            p.gold = c.gilded
            p.score = c.score
            p.orig_content = c.body
            if False:  # Don't update comments for now, takes a long time and info is not used.
                for parent in p.parents:
                    if "link" in parent and parent["link"]:
                        parent_comment = get_comment_from_link(reddit, parent["link"])
                        parent["score"] = parent_comment.score
                        parent["gold"] = parent_comment.gilded

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
