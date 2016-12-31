from sprog import Sprog

user_name = "Poem_for_your_sprog"
latex_template_filename = "sprog.tex.mako"
html_template_filename = "sprog.html.mako"
latexfile = "sprog.tex"
tmpdir = "tmp"

if __name__ == "__main__":
    sprog = Sprog(user_name=user_name,
                  latex_template_filename=latex_template_filename, html_template_filename=html_template_filename,
                  tmpdir=tmpdir, latexfile=latexfile)
    sprog.run()
