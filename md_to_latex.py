import mistune_modified
import re


def escape(text):
    out = ""
    superscript = 0
    singlecharescapes = {
        "~": r"\textasciitilde{}",
        "\\":  r"\textbackslash{}",
        "&": r"\&{}",
        "$": r"\${}",
        "{": r"\{{}",
        "}": r"\}{}",
        "#": r"\#{}",
        "<": r"\textless{}",
        ">": r"\textgreater{}",
        "_": r"\_{}",
        "%": r"\%",
        "[": r"{[}",
        "]": r"{]}",
    }
    for c in text:
        if c in singlecharescapes:
            out += singlecharescapes[c]
        elif c == ";" and out[-8:] == r"\&{}nbsp":
            out = out[:-8] + "~"
        elif c == "." and out[-2:] == "..":
            out = out[:-2] + "…"
        else:
            out += c
    out += "}" * superscript

    return out


class LaTeXRenderer(mistune_modified.Renderer):
    """
    LaTeX Renderer
    """

    def block_code(self, code, lang=None):
        return "\n\\begin{verbatim}\n%s\n\end{verbatim}\n" % code

    def block_quote(self, text):
        return "\n\\begin{blockquote}\n%s\n\\end{blockquote}\n" % text

    def header(self, text, level, raw=None):
        if level == 1:
            return "{\\vspace{.4em}\n\n\\LARGE \\textbf{%s}\\vspace{.4em}\n\n}\n" % text
        elif level == 2:
            return "{\n\n\\vspace{.3em}\\LARGE %s\\vspace{.3em}\n\n}\n" % text
        elif level == 3:
            return "{\n\n\\vspace{.1em}\\Large \\textbf{%s}\\vspace{.1em}\n\n}\n" % text
        elif level == 4:
            return "{\n\n\\Large %s\n\n}\n" % text
        elif level == 5:
            return "{\n\n\\large \\textbf{%s}\n\n}\n" % text
        elif level == 6:
            return "\n\n\\underline{%s}\n\n" % text
        return text

    def hrule(self):
        return '\n\n\\vspace{.5em}\\hrule\\vspace{.5em}\n\n'

    def list(self, body, ordered=True):
        if ordered:
            return "\\begin{enumerate}\n%s\n\\end{enumerate}" % body
        else:
            return "\\begin{itemize}\n%s\n\\end{itemize}" % body

    def list_item(self, text):
        return "\\item %s" % text

    def paragraph(self, text):
        return "%s\n\n" % text.strip(' ')

    def table(self, header, body):
        columns = "c" * (body.split("\n")[0].count("&") + 1) if "\n" in body else ""
        return '\n\\begin{tabular}{%s}\n%s\n\hline\n%s\n\\end{tabular}\n' % (columns, header, body)

    def table_row(self, content):
        return "%s \\\\\n" % content[:-2]

    def table_cell(self, content, **flags):
        return " %s & " % content

    def double_emphasis(self, text):
        return "\\textbf{%s}" % text

    def emphasis(self, text):
        return "\\emph{%s}" % text

    def codespan(self, text):
        return "\\verb!%s!" % text

    def linebreak(self):
        return r'\\'

    def strikethrough(self, text):
        return r"\sout{%s}" % text

    def text(self, text):
        return escape(text)

    def autolink(self, link, is_email=False):
        link = link.replace(r"\)", ")").replace(r"\(", "(")
        return r'\url{%s}' % link

    def link(self, link, title, text):
        link = link.replace(r"\)", ")").replace(r"\(", "(")
        if not text:
            text = link
        if link[0] == "#":
            # link to same page object / reddit image thingy
            return "[%s]" % link[1:]
        return r"\href{%s}{%s}" % (link.replace("#", "\#{}"), escape(text))

    def image(self, src, title, text):
        # should never be called
        raise ValueError("Image tag in reddit markdown???")

    def inline_html(self, html):
        return escape(html)

    def footnote_ref(self, key, index):
        return ''

    def footnote_item(self, key, text):
        print("Footnote???")
        return text

    def footnotes(self, text):
        print("Footnotes???")
        return text

    def escape(self, text):
        return escape(text)


def process_superscript(source):
    superscript = 0
    superpar = False
    out = ""
    for c in source:
        if c == "^":
            superscript += 1
            out += r"\textsuperscript{"
        elif c == "(" and not superpar and out[-17:] == r"\textsuperscript{":
            superpar = True
        elif c == ")" and superscript and superpar:
            out += "}" * superscript
            superscript = 0
        elif c in (" ", "\n") and not superpar:
            if out[-17:] == r"\textsuperscript{":
                out = out[:-17] + r"\textasciicircum{}"
                superscript -= 1

            out += "}" * superscript
            superscript = 0
            out += c
        elif superscript and c == "\\" and out[-1:] == "\\":
            if superpar:
                out = out[:-1] + "}" * superscript + "\\\\" + r"\textsuperscript{" * superscript
            else:
                out = out[:-1] + "}" * superscript + "\\\\"
                superscript = 0
        elif c == "\n" and superscript and superpar:
            out += " "
        else:
            out += c
    return out

renderer = LaTeXRenderer()
parser = mistune_modified.Markdown(renderer=renderer)


def md_to_latex(source):
    parsed = parser(source)
    out = process_superscript(parsed)
    # latex quotes
    out = re.sub(r'(?:(?<=^)"(?=\w))|(?:(?<=\s)"(?=\w))', "``", out, re.MULTILINE)
    out = re.sub(r'(?<=\w)"(?=\s|$)', "''", out, re.MULTILINE)
    out = re.sub(r"(?:(?<=^)'(?=[^']))|(?:(?<=\s)'(?=[^']))", "`", out, re.MULTILINE)
    return out