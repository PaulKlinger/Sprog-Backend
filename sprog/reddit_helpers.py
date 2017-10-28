import praw


def get_all_parents(obj):
    parents = []
    assert isinstance(obj, praw.models.reddit.comment.Comment)
    p = obj
    while True:
        p = p.parent()
        print(p.id)
        if isinstance(p, praw.models.reddit.submission.Submission):
            parents.reverse()
            return p, parents

        parents.append(p)


class CommentMissingException(Exception):
    pass


def get_comment_from_link(reddit: praw.Reddit, link: str) -> praw.models.reddit.comment.Comment:
    comment_id = link.split("/")[-1]
    c = reddit.comment(comment_id)
    if not isinstance(c, praw.models.reddit.comment.Comment) or c.permalink not in link \
            or c.body in ("[deleted]", "[removed]") or c.body is None:
        raise CommentMissingException("Comment does not exist")
    return c


def get_comments(reddit: praw.Reddit, user_name: str):
    user = reddit.redditor(user_name)
    comments = user.comments.new()
    yield from comments
