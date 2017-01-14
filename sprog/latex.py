import shutil
import subprocess
import re
import os
import statistics
from typing import List
from mako.template import Template

from .stats_n_graphs import posting_time_stats, id_from_link
from .poems import Poem
from .load_process_images import get_images, process_images


def make_snippet(tex):
    """"strips out newlines and links (used for top gilded list in statistics)"""
    tex = re.sub(r"\\begin\{[^}]*\}", "", tex)
    tex = re.sub(r"\\end\{[^}]*\}", "", tex)
    tex = tex.replace(r"\\", " ").replace("\r\n", " ").replace("\n", " ")
    tex = re.sub(r"\\href\{.*?\}\{(.*?)\}", r"\1", tex, re.MULTILINE)
    snip = " ".join(tex.split(" ")[:6])
    # close all braces (if snipped in the middle of e.g. \emph{...})
    snip += "}" * sum(1 if c == "{" else -1 if c == "}" else 0 for c in snip)
    return snip


def compile_latex(tmpdir, latexfile):
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


def make_compile_latex(tmpdir: str, latexfile: str, user_name: str, template: Template, poems: List[Poem]):
    latex = template.render_unicode(poems=poems, small=False,
                                    make_snippet=make_snippet, id_from_link=id_from_link,
                                    posting_time_stats=posting_time_stats, statistics=statistics,
                                    user_name=user_name.replace("_", "\\_"))

    with open(os.path.join(tmpdir, latexfile), "wb") as f:
        f.write(latex.encode("utf-8"))

    latex = template.render_unicode(poems=poems, small=True,
                                    make_snippet=make_snippet, id_from_link=id_from_link,
                                    posting_time_stats=posting_time_stats, statistics=statistics,
                                    user_name=user_name.replace("_", "\\_"))

    with open(os.path.join(tmpdir, "small_" + latexfile), "wb") as f:
        f.write(latex.encode("utf-8"))

    pages = compile_latex(tmpdir, latexfile)
    pages_small = compile_latex(tmpdir, "small_" + latexfile)
    return pages, pages_small


def create_pdf(tmpdir: str, latexfile: str, user_name: str,
               template: Template, poems: List[Poem]) -> (List[Poem], int, int):
    print("Getting Images")
    poems = get_images(tmpdir, poems)
    print("Processing Images")
    process_images()
    print("Compiling LaTeX")
    pages, pages_small = make_compile_latex(tmpdir, latexfile, user_name, template, poems)
    filename = latexfile[:-4] + ".pdf"
    shutil.move(os.path.join(tmpdir, filename), filename)
    shutil.move(os.path.join(tmpdir, "small_" + filename), "small_" + filename)
    return poems, pages, pages_small
