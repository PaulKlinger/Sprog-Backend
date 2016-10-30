__author__ = 'Paul'
import praw
from mako.template import Template
import subprocess
import datetime
import os
import pypandoc
import requests
import shutil
import re
import json
import statistics
import boto3

from stats_n_graphs import id_from_link, posting_time_stats, make_graphs
from utility import suffix_strftime
from drive_upload import upload_sprog_to_drive

user_name = "Poem_for_your_sprog"
template = Template(filename="sprog.tex.mako")
index_template = Template(filename="sprog.html.mako")
latexfile = "sprog.tex"
tmpdir = "tmp"
comment_limit = None

AWS_ACCESS_KEY = "***REMOVED***"
AWS_SECRET_KEY = "***REMOVED***"

r = praw.Reddit(user_agent="Python:Sprog:dev (by /u/Almoturg)")


def get_parent(obj):
    assert type(obj) == praw.objects.Comment
    if obj.is_root:
        return obj.submission
    return r.get_info(thing_id=obj.parent_id)


def username_escape(author):
    if author is None:
        return "(deleted user)"
    else:
        return author.name.replace("_", "\_")


def title_escape(title):
    rep = [("_", "\\_"), ("&", "\&"), ("&amp;", "\\&"), ("$", "\\$"), ("\\(", "("),
           ("\\)", ")"), ("#", "\\#"), ("%", "\\%"),
           ]
    for o, n in rep:
        title = title.replace(o, n)
    return title


def get_all_parents(obj):
    parents = []
    assert type(obj) == praw.objects.Comment
    p = obj
    while True:
        p = get_parent(p)
        print(p.id)
        if type(p) == praw.objects.Submission:
            parents.reverse()
            return p, parents

        parents.append(p)


def md2latex(md):
    # remove whitespace between [title] and (url) in link (reddit ignores this)
    md = re.sub(r"\[([^\]]*?)\]\s+\(http", "[\1](http", md)
    # if \n is not added md="." causes an error
    return pypandoc.convert_text("\n" + md, "latex", format="md")


class Poem(object):
    def __init__(self, timestamp, link, content,
                 submission_user, submission_content, submission_url, submission_title,
                 parents, noimg, imgfilename, orig_content, orig_submission_content, gold, score):
        self.datetime = timestamp
        self.link = link
        self.content = content
        self.submission_user = submission_user
        self.submission_content = submission_content
        self.submission_url = submission_url
        self.submission_title = submission_title
        self.parents = parents
        self.noimg = noimg
        self.imgfilename = imgfilename
        self.orig_content = orig_content
        self.orig_submission_content = orig_submission_content
        self.gold = gold
        self.score = score

    @classmethod
    def from_comment(cls, comment, is_submission=False):
        timestamp = datetime.datetime.utcfromtimestamp(comment.created_utc)
        link = comment.permalink

        parents = []
        submission_url = None
        if not is_submission:
            submission, parent_comments = get_all_parents(comment)
            for p in parent_comments:
                parents.append({"author": username_escape(p.author), "body": md2latex(p.body),
                                "orig_body": p.body, "link": p.permalink, "timestamp": p.created_utc,
                                "gold": p.gilded, "score": p.score})

            submission_user = username_escape(submission.author)
            submission_content = md2latex(submission.selftext)

            if not submission.is_self:
                submission_url = submission.url

            # workaround for 2013-12-18 21:14:00 post
            submission_content = submission_content.replace("\\($\\)", "\$")

            submission_title = title_escape(submission.title)
            content = md2latex(comment.body)
        else:
            submission_title = title_escape(comment.title)
            submission_content = ""
            submission_user = username_escape(comment.author)
            if not comment.is_self:
                submission_url = comment.url
            content = md2latex(comment.selftext)

        noimg = False
        imgfilename = None
        return cls(timestamp, link, content, submission_user, submission_content, submission_url, submission_title,
                   parents, noimg, imgfilename, comment.body if not is_submission else comment.selftext,
                   submission.selftext if not is_submission else "",
                   comment.gilded, comment.score)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def get_poems(poems=None):
    if poems is None:
        poems = []
    user = r.get_redditor(user_name)
    comments = user.get_comments(limit=comment_limit)
    newpoems = []
    known_links = [p.link.split("//")[1] for p in poems]
    for i, c in enumerate(comments):
        # break if a known poem is encountered
        # checking only poem[0] does not suffice as comments may be deleted
        if poems and c.permalink.split("//")[1] in known_links:
            break
        print(".", end="", flush=True)
        try:
            newpoems.append(Poem.from_comment(c))
        except Exception as e:
            print(e)
            print(len(poems))

    print()
    return newpoems + poems


def save_poems_json(poems, filename):
    struct = []
    for p in poems:
        struct.append({
            "timestamp": (p.datetime - datetime.datetime(1970, 1, 1)).total_seconds(),
            "link": p.link,
            "content": p.content,
            "submission_user": p.submission_user,
            "submission_content": p.submission_content,
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


def load_poems_json(filename):
    poems = []
    try:
        with open(filename, "r") as f:
            struct = json.loads(f.read())
            if struct:
                for p in struct:
                    poems.append(Poem(
                        timestamp=datetime.datetime.utcfromtimestamp(p["timestamp"]),
                        link=p["link"],
                        content=p["content"],
                        submission_user=p["submission_user"],
                        submission_content=p["submission_content"],
                        submission_url=p["submission_url"],
                        submission_title=p["submission_title"],
                        parents=p["parents"],
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


def download_file(url, filename):
    try:
        with open(filename, 'wb') as f:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            if "Content-Type" in response.headers and "gif" in response.headers["Content-Type"]:
                raise ValueError("Image {} is a gif".format(url))
            if "removed.png" in response.url:
                raise FileNotFoundError("Image {} deleted".format(url))
            size = 0
            for block in response.iter_content(1024):
                size += len(block)
                if size >= 5.243 * 10 ** 6:  # > 5 MiB
                    raise ValueError("File {} too big".format(url))
                if not block:
                    break
                f.write(block)
            if size < 100:
                raise ValueError("File {} too small".format(url))
    except Exception as e:
        os.remove(filename)
        raise e


def get_image_url_from_link(url):
    if "imgur" in url and not url[-3:] in ("jpg", "png", "gif", "ifv"):
        return url + ".jpg"
    elif url[-3:] in ("jpg", "png"):
        return url
    return None


def create_image_filename(timestamp, imgurl):
    tstring = timestamp.strftime("%Y_%m_%dT%H_%M_%S")
    # create imgname from last url segment by filtering out anything that isn't a valid filename character
    imgname = "".join([c for c in imgurl.split("/")[-1] if c.isalnum() or c in ' _.']).rstrip()
    imgfilename = "{}_{}".format(tstring, imgname)
    return imgfilename


def download_image(imgurl, imgfilename):
    print("loading " + imgurl)
    try:
        if not os.path.isfile(os.path.join(tmpdir, imgfilename)):
            download_file(imgurl, os.path.join(tmpdir, imgfilename))
        else:
            print(imgurl + " already loaded")
    except Exception as e:
        print("Failed to download Image: " + str(e))
        return False
    else:
        return True


def get_images_from_tex(tex, timestamp):
    for m in re.finditer(r"(?:\\href{)?(https?://\S+/[\w/.-?]+)(?:}{(.*?)})?", tex,
                         re.MULTILINE | re.DOTALL):

        imgurl = get_image_url_from_link(m.group(1))
        if imgurl:
            imgfilename = create_image_filename(timestamp, imgurl)
            if download_image(imgurl, imgfilename):
                includeimg = r"{}~\\ \includegraphics[keepaspectratio," \
                             r"max width=0.5\textwidth, max height=0.75\textwidth]" \
                             r'{{"{}"}}\\'.format(m.group(2) or "", imgfilename)
                tex = tex.replace(m.group(0), includeimg)
    return tex


def get_images(poems):
    for p in poems:
        if p.submission_url and not p.noimg and not p.imgfilename:
            imgurl = get_image_url_from_link(p.submission_url)
            if imgurl:
                imgfilename = create_image_filename(p.datetime, imgurl)
                if download_image(imgurl, imgfilename):
                    p.imgfilename = imgfilename
                else:
                    p.noimg = True
        else:
            p.submission_content = get_images_from_tex(p.submission_content, p.datetime)

        for i, c in enumerate(p.parents):
            c["body"] = get_images_from_tex(c["body"], p.datetime)
    return poems


def process_images():
    """scale images to a maximum resolution of 2000x2000 and set dpi to 300 (for auto scaling of images)"""
    command = r'mogrify -verbose -resize "2000x2000>" -units "pixelsperinch" -density "150x150" tmp/*.png tmp/*.jpg'
    subprocess.call(command, shell=True)


def process_latex(latex):
    """Replace various LaTeX expressions produced by pypandoc with correct ones

    currently Reddit superscript notation and section headings (otherwise they appear in the PDF TOC)
    this should really be done earlier but I don't want to redownload everything...
    """

    #############
    # Superscripts
    #############
    # first undo the substitution done by pypandoc (why do I use it again...)
    while True:
        i = latex.find(r"\textsuperscript{")
        if i == -1:
            break
        latex = latex[:i] + "^" + latex[i + len(r"\textsuperscript{"):].replace("}", "", 1)
    latex = latex.replace(r"\^{}", "^")

    # then substitute the correct ones
    platex = ""
    sup = 0
    for s in latex:
        if s == "^":
            sup += 1
            platex += r"\textsuperscript{"
            continue
        if sup > 0 and s in (" ", "\n"):
            platex += "}" * sup
            sup = 0
        platex += s

    #########
    # section headings
    #########
    platex = platex.replace(r"\section{", r"\textbf{\Large ")
    platex = platex.replace(r"\subsection{", r"\textbf{\large ")

    ########
    # format urls
    ########
    # this turns urls into links but also allows latex to put linebreaks in them
    platex = re.sub(r"\s(https?://\S+/(?:[\w/.-?_]|\\_)+)", r"\\url{\1}", platex)

    return platex


def make_snippet(tex):
    """"strips out newlines and links (used for top gilded list in statistics)"""

    tex = tex.replace(r"\\", " ").replace("\r\n", " ")
    tex = re.sub(r"\\href\{.*?\}\{(.*?)\}", r"\1", tex, re.MULTILINE)
    snip = " ".join(tex.split(" ")[:6])
    snip += "}" * sum(1 if c == "{" else -1 if c == "}" else 0 for c in snip)
    return snip


def make_compile_latex(poems):
    latex = template.render_unicode(poems=poems,
                                    make_snippet=make_snippet, id_from_link=id_from_link,
                                    posting_time_stats=posting_time_stats, statistics=statistics,
                                    user_name=user_name.replace("_", "\\_"))
    latex = process_latex(latex)

    with open(os.path.join(tmpdir, latexfile), "wb") as f:
        f.write(latex.encode("utf-8"))

    command = "xelatex -interaction nonstopmode {}".format(latexfile)
    res = subprocess.run(command, cwd=tmpdir, shell=True,)
    res = subprocess.run(command, cwd=tmpdir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    res_stdout = res.stdout.decode(encoding="utf-8", errors="replace")
    match = re.search(r"Output written on sprog\.pdf \((\d+?) pages\)", res_stdout)
    if not match:
        raise Exception("something went wrong with the xetex command")
    return int(match.group(1))


def create_pdf(poems):
    poems = get_images(poems)
    process_images()
    make_graphs(poems)
    pages = make_compile_latex(poems)
    filename = latexfile[:-4] + ".pdf"
    shutil.move(os.path.join(tmpdir, filename), filename)
    return poems, pages


def get_comment_from_link(link):
    submission = r.get_submission(link)
    c = submission.comments[0]
    if c.permalink != link or c.body == "[deleted]":
        raise IndexError("Comment does not exist")
    return c


def update_poems(poems, deleted_poems):
    for p in poems:
        print(".", end="", flush=True)
        if (datetime.datetime.today() - p.datetime) > datetime.timedelta(days=14):
            break
        try:
            c = get_comment_from_link(p.link)
            p.gold = c.gilded
            p.score = c.score
            p.content = md2latex(c.body)
            p.orig_content = c.body
            if False:  # Don't update comments for now, takes a long time and info is not used.
                for parent in p.parents:
                    if "link" in parent and parent["link"]:
                        parent_comment = get_comment_from_link(parent["link"])
                        parent["score"] = parent_comment.score
                        parent["gold"] = parent_comment.gilded

        except Exception as e:
            print("-------")
            if isinstance(e, IndexError):
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


def make_html(poems, pages):
    with open(os.path.join(tmpdir, "sprog.html"), "w") as f:
        f.write(index_template.render_unicode(poems=poems, pages=pages,
                                              suffix_strftime=suffix_strftime))


def upload_to_s3():
    s3 = boto3.resource("s3", "eu-west-1",
                        aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_KEY,)
    bucket = s3.Bucket("almoturg.com")
    bucket.upload_file("sprog.pdf", "sprog.pdf",
                       ExtraArgs={'ContentType': 'application/pdf'})
    bucket.upload_file(os.path.join(tmpdir, "sprog.html"), "sprog",
                       ExtraArgs={'ContentType': 'text/html'})


def add_submission(poems, link):
    """Add a submission (currently not running automatically because most submissions aren't poems)"""
    if link in (p.link for p in poems):
        print("submission already stored")
        return
    submission = r.get_submission(link)
    time = datetime.datetime.utcfromtimestamp(submission.created_utc)
    for i in range(len(poems) - 1):
        if poems[i].datetime > time > poems[i + 1].datetime:
            poems.insert(i + 1, Poem.from_comment(submission, is_submission=True))
            return


def main():
    print("loading stored poems")
    poems = load_poems_json("poems.json")
    deleted_poems = load_poems_json("deleted_poems.json")
    print("updating recent poems")
    poems, deleted_poems = update_poems(poems, deleted_poems)
    print("getting new poems")
    poems = get_poems(poems)
    print("creating pdf")
    poems, pages = create_pdf(poems)
    print("make sprog.html")
    make_html(poems, pages)
    print("uploading to S3")
    upload_to_s3()
    print("uploading to Google Drive")
    upload_sprog_to_drive()
    print("saving poems")
    save_poems_json(poems, "poems.json")
    save_poems_json(deleted_poems, "deleted_poems.json")

if __name__ == "__main__":
    main()

# ----------------------------------
# useful snippets
# ----------------------------------

# # remove double spacing except between verses
# # (sprog only used this on early poems so this doesn't need to run all the time)
# # \r\n\r\n should be readded between \end{itemize} and \emph to prevent an error,
# # I did this manually for the six cases where it occurred.
# for p in poems[-142:]:
#     p.content = re.sub("(?:(?<!})\r\n\r\n(?!\\\\emph))|(?:(?<=})\r\n\r\n(?=\\\\emph))", r"\\\\", p.content)
