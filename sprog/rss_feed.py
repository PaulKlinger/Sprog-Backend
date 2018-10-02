from . import mistune_modified
from datetime import datetime


def title_snippet(content):
    words = content.split(" ")
    return " ".join(words[:10]) + "..."


def create_rss_feeds(poems, rss_template):
    converter = mistune_modified.Markdown(renderer=mistune_modified.Renderer())
    with open("sprog.rss", "wb") as f:
        f.write(rss_template.render_unicode(converter=converter, poems=poems, build_date=datetime.now().isoformat(),
                                            title_snippet=title_snippet, show_parents=True).encode("utf-8"))

    with open("sprog_no_context.rss", "wb") as f:
        f.write(rss_template.render_unicode(converter=converter, poems=poems, build_date=datetime.now().isoformat(),
                                            title_snippet=title_snippet, show_parents=False).encode("utf-8"))
