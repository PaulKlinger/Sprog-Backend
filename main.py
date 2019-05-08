from sprog.sprog import Sprog

from sprog_auth import passwords

user_name = "Poem_for_your_sprog"
latex_template_filename = "templates/sprog.tex.mako"
html_template_filename = "templates/sprog.html.mako"
rss_template_filename = "templates/sprog.rss.mako"
latexfile = "sprog.tex"
tmpdir = "tmp"

if __name__ == "__main__":
    sprog = Sprog(user_name=user_name,
                  latex_template_filename=latex_template_filename, html_template_filename=html_template_filename,
                  rss_template_filename=rss_template_filename,
                  tmpdir=tmpdir, latexfile=latexfile, passwords=passwords)
    sprog.run(upload=False)
