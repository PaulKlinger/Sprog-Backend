import praw
import datetime
import os.path
from mako.template import Template

from .drive_upload import upload_sprog_to_drive
from .namecheap_ftp_upload import upload_sprog_to_namecheap
from .s3_upload import upload_to_s3
from .poems import update_poems, get_poems
from .latex import create_pdf
from .json_store import load_poems_json, save_poems_json
from .stats_n_graphs import make_graphs
from .utility import suffix_strftime
from .send_fcm import send_last_poems_fcm
from .rss_feed import create_rss_feeds


class Sprog(object):
    def __init__(self, user_name: str,
                 latex_template_filename: str, html_template_filename: str, rss_template_filename: str,
                 tmpdir: str, latexfile: str, passwords: dict):
        self.user_name = user_name
        self.reddit = praw.Reddit()
        self.user = self.reddit.redditor(user_name)
        self.tmpdir = tmpdir
        self.latexfile = latexfile
        self.passwords = passwords

        self.latex_template = Template(filename=latex_template_filename)
        self.html_template = Template(filename=html_template_filename)
        self.rss_template = Template(filename=rss_template_filename, input_encoding="utf-8")

        self.poems = None
        self.pages = self.pages_small = None

    def run(self):
        self._load_update_poems()
        self._poems_to_latex()
        print("Creating graphs")
        make_graphs(self.poems)

        self.poems, self.pages, self.pages_small = create_pdf(self.tmpdir, self.latexfile, self.user_name,
                                                              self.latex_template, self.poems)
        self._make_html()
        print("Uploading to Amazon S3")
        upload_to_s3(self.tmpdir, self.passwords)
        print("Uploading to Google Drive")
        upload_sprog_to_drive()
        print("Saving Poems")
        self._save_poems()
        print("creating rss feeds")
        create_rss_feeds(self.poems[:50], self.rss_template)
        print("Uploading to Namecheap")
        upload_sprog_to_namecheap(self.tmpdir, self.passwords)
        print("Send FCM message")
        send_last_poems_fcm(self.poems)

    def _load_update_poems(self):
        self.poems = load_poems_json("poems.json")
        self.deleted_poems = load_poems_json("deleted_poems.json")
        print("updating recent poems")
        self.poems, self.deleted_poems = update_poems(self.reddit, self.user_name, self.poems, self.deleted_poems)
        print("getting new poems")
        self.poems = get_poems(self.reddit, self.user_name, self.poems)

    def _save_poems(self):
        save_poems_json(self.poems, "poems.json", None)
        save_poems_json(self.deleted_poems, "deleted_poems.json", None)

        # Last 60 days poems for App updates
        save_poems_json(self.poems, "poems_60days.json",
                        datetime.datetime.now() - datetime.timedelta(days=60))

    def _poems_to_latex(self):
        print("Converting Markdown to LaTeX")
        for p in self.poems:
            p.to_latex()

    def _make_html(self):
        print("Creating HTML")
        now = datetime.datetime.utcnow()
        next_update = now + datetime.timedelta(hours=12)
        with open(os.path.join(self.tmpdir, "sprog.html"), "w") as f:
            f.write(self.html_template.render_unicode(poems=self.poems, pages=self.pages, pages_small=self.pages_small,
                                                      suffix_strftime=suffix_strftime,
                                                      now=now, next_update=next_update))
