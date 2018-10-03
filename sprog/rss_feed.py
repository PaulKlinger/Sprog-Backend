from . import mistune_modified
from datetime import datetime
from email import utils


def title_snippet(content):
    words = content.replace("*", "").split(" ")
    return " ".join(words[:10]) + "..."


def username_line(username, to_html):
    if username == "deleted":
        return "<p>&mdash; (deleted)</p>"
    else:
        return to_html("&mdash; " + username)


def create_rss_feeds(poems, rss_template):
    to_html = mistune_modified.Markdown(renderer=mistune_modified.Renderer())
    format_username = lambda u: username_line(u, to_html)
    with open("sprog.rss", "wb") as f:
        f.write(
            rss_template.render_unicode(to_html=to_html, poems=poems, format_username=format_username,
                                        build_date=utils.format_datetime(datetime.now()),
                                        title_snippet=title_snippet, format_timestamp=utils.format_datetime,
                                        show_parents=True).encode("utf-8"))

    with open("sprog_no_context.rss", "wb") as f:
        f.write(rss_template.render_unicode(to_html=to_html, poems=poems, format_username=format_username,
                                            build_date=utils.format_datetime(datetime.now()),
                                            title_snippet=title_snippet, format_timestamp=utils.format_datetime,
                                            show_parents=False).encode("utf-8"))
