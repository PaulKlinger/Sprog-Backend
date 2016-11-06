import praw
from mako.template import Template
import subprocess
import datetime
import os
import requests
import shutil
import re
import json
import statistics

from md_to_latex import md_to_latex
from stats_n_graphs import id_from_link, posting_time_stats, make_graphs
from utility import suffix_strftime
from drive_upload import upload_sprog_to_drive
from s3_upload import upload_to_s3
from namecheap_ftp_upload import upload_sprog_to_namecheap

user_name = "Poem_for_your_sprog"
template = Template(filename="sprog.tex.mako")
index_template = Template(filename="sprog.html.mako")
latexfile = "sprog.tex"
tmpdir = "tmp"
comment_limit = None

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


def poem_md_to_latex(md, dt):
    latex = md_to_latex(md)
    if dt < datetime.datetime(year=2013, month=2, day=11):
        # in sprog's early poems there is a double newline between each line, not just stanza
        # this is turned into \\ here
        latex = re.sub("(?:(?<!})\n\n(?!\\\\emph))|(?:(?<=})\n\n(?=\\\\emph))|(?:(?<=},)\n\n(?=\\\\emph))",
                       r"~\\\\", latex)
    # replace single dots with fleurons
    fleuron_tex = r"\n\n\\hfill\\includegraphics[width=1em, height=1em]{../fleuron.png}\\hspace*{\\fill}\n\n"
    latex = re.sub(r"\\begin\{itemize\}\s*\\item\s*\\end\{itemize\}",
                   fleuron_tex, latex)
    # replace single stars with fleurons
    latex = re.sub(r"(?:^|\\\\)(?:\s|~)*?\*(?:\s|~)*?(?:$|\\\\)", fleuron_tex, latex, flags=re.MULTILINE)

    # disable verse environment during blockquote
    # (verse messes up the indentation (text overlaps the line to the left))
    latex = latex.replace(r"\begin{blockquote}", r"\end{verse}\begin{blockquote}")
    latex = latex.replace(r"\end{blockquote}", r"\end{blockquote}\begin{verse}")

    latex = "\\begin{verse}\n%s\n\\end{verse}" % latex

    latex = re.sub(r"\\begin\{verse\}\s*\\end\{verse\}", "", latex)
    return latex


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

    @classmethod
    def from_comment(cls, comment, is_submission=False):
        timestamp = datetime.datetime.utcfromtimestamp(comment.created_utc)
        link = comment.permalink

        parents = []
        submission_url = None
        if not is_submission:
            submission, parent_comments = get_all_parents(comment)
            for p in parent_comments:
                parents.append({"author": username_escape(p.author),
                                "orig_body": p.body, "link": p.permalink, "timestamp": p.created_utc,
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

    def poem_latex(self):
        return poem_md_to_latex(self.orig_content, self.datetime)

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
                        submission_user=p["submission_user"],
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
    for m in re.finditer(r"(?:\\href{)?(?:\\url{)?(https?://\S+/[\w/.\-?]+)(?:(?:}{(.*?)})|})?", tex,
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


def make_snippet(tex):
    """"strips out newlines and links (used for top gilded list in statistics)"""
    tex = tex.replace("\\begin{verse}", "")
    tex = tex.replace("\\end{verse}", "")  # veeery short poems??
    tex = tex.replace(r"\\", " ").replace("\r\n", " ")
    tex = re.sub(r"\\href\{.*?\}\{(.*?)\}", r"\1", tex, re.MULTILINE)
    snip = " ".join(tex.split(" ")[:6])
    snip += "}" * sum(1 if c == "{" else -1 if c == "}" else 0 for c in snip)
    return snip


def compile_latex(latexfile):
    try:
        os.remove(os.path.join(tmpdir, latexfile[:-3] + "aux"))
    except OSError:
        pass
    command = "xelatex {}".format(latexfile)
    subprocess.run(command, cwd=tmpdir, shell=True, )
    res = subprocess.run(command, cwd=tmpdir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    res_stdout = res.stdout.decode(encoding="utf-8", errors="replace")
    match = re.search(r"\.pdf \((\d+?) pages\)", res_stdout)
    if not match:
        raise Exception("something went wrong with the xetex command")

    return int(match.group(1))


def make_compile_latex(poems):
    latex = template.render_unicode(poems=poems, small=False,
                                    make_snippet=make_snippet, id_from_link=id_from_link,
                                    posting_time_stats=posting_time_stats, statistics=statistics,
                                    user_name=user_name.replace("_", "\\_"), poem_md_to_latex=poem_md_to_latex)

    with open(os.path.join(tmpdir, latexfile), "wb") as f:
        f.write(latex.encode("utf-8"))

    latex = template.render_unicode(poems=poems, small=True,
                                    make_snippet=make_snippet, id_from_link=id_from_link,
                                    posting_time_stats=posting_time_stats, statistics=statistics,
                                    user_name=user_name.replace("_", "\\_"), poem_md_to_latex=poem_md_to_latex)

    with open(os.path.join(tmpdir, "small_" + latexfile), "wb") as f:
        f.write(latex.encode("utf-8"))

    pages = compile_latex(latexfile)
    pages_small = compile_latex("small_" + latexfile)
    return pages, pages_small


def create_pdf(poems):
    poems = get_images(poems)
    process_images()
    make_graphs(poems)
    pages, pages_small = make_compile_latex(poems)
    filename = latexfile[:-4] + ".pdf"
    shutil.move(os.path.join(tmpdir, filename), filename)
    shutil.move(os.path.join(tmpdir, "small_" + filename), "small_" + filename)
    return poems, pages, pages_small


def get_comment_from_link(link):
    submission = r.get_submission(link)
    c = submission.comments[0]
    if c.permalink not in link or c.body in ("[deleted]", "[removed]") or c.body is None:
        raise IndexError("Comment does not exist")
    return c


def update_poems(poems, deleted_poems):
    for p in poems:
        print(".", end="", flush=True)
        if (datetime.datetime.today() - p.datetime) > datetime.timedelta(days=30):
            break
        try:
            c = get_comment_from_link(p.link)
            p.gold = c.gilded
            p.score = c.score
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


def poems_to_latex(poems):
    for p in poems:
        p.content = p.poem_latex()
        p.submission_content = md_to_latex(p.orig_submission_content)
        for parent in p.parents:
            if parent["orig_body"]:
                parent["body"] = md_to_latex(parent["orig_body"])
            else:
                print("No orig_body???")


def make_html(poems, pages, pages_small):
    now = datetime.datetime.utcnow()
    next_update = now + datetime.timedelta(hours=12)
    with open(os.path.join(tmpdir, "sprog.html"), "w") as f:
        f.write(index_template.render_unicode(poems=poems, pages=pages, pages_small=pages_small,
                                              suffix_strftime=suffix_strftime,
                                              now=now, next_update=next_update))


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
    print("converting markdown to LaTeX")
    poems_to_latex(poems)
    print("creating pdf")
    poems, pages, pages_small = create_pdf(poems)
    print("make sprog.html")
    make_html(poems, pages, pages_small)
    print("uploading to S3")
    upload_to_s3()
    print("uploading to Google Drive")
    upload_sprog_to_drive()
    print("uploading to namecheap")
    upload_sprog_to_namecheap()
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

# # this was in load_poems_json to add orig_content to comments without it
# for parent in p["parents"]:
#     if parent["orig_body"] is None and "body" in parent and parent["body"] and parent["link"] is None:
#         print()
#         print(parent["body"])
#         print(parent["author"])
#         print(p["link"] + "?context=10000")
#         parent_link = input()
#         if parent_link == "o":
#             parent["orig_body"] = parent["body"]
#         elif parent_link == "d":
#             parent["orig_body"] = "[deleted]"
#         else:
#             try:
#                 c = get_comment_from_link(parent_link[:-1])
#             except Exception as e:
#                 print("error:")
#                 print(e)
#                 input("enter to continue with next comment")
#             else:
#                 print(c.body)
#                 yn = input("non-empty to accept")
#                 if yn:
#                     parent["link"] = c.permalink
#                     parent["orig_body"] = c.body