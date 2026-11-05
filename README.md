# Sprog Backend

Backend for [https://almoturg.com/sprog/](https://almoturg.com/sprog/) and the [Sprog Android App](https://github.com/PaulKlinger/Sprog-App).

Gets new reddit comments by /u/Poem_for_your_sprog, creates pdf collections of them, and stores them as json. Results are uploaded to https://almoturg.com/sprog

In addition to the Python packages specified in requirements.txt the following external tools are required
* A LaTeX installation with XeLateX (e.g. [TexLive](https://www.tug.org/texlive/)) and the following packages: babel, geometry, tcolorbox, verse, eurosym, ulem, graphicx, subcaption, float, adjustbox, scalerel, fontspec, varwidth, longtable, booktabs, fancyvrb, microtype, titlesec, hyperref, xcolor
* [mogrify](http://www.imagemagick.org/script/mogrify.php) (part of [ImageMagick](http://www.imagemagick.org/))
## Uploads

Each run uploads the generated files to Namecheap (SFTP, `public_html`)
and to Amazon S3. It also pushes them to the
[almoturg.com repo](https://github.com/PaulKlinger/almoturg.com) in
parallel: the site is served from that repo (Cloudflare Workers Static
Assets, same setup as paulklinger.com), so each update keeps the live
site current. The GitHub push is best-effort — if it fails, the run
still completes and the site still updates via FTP.

Setup: add `GITHUB_TOKEN` to the `passwords` dict in `sprog_auth.py`
(alongside the Namecheap and AWS credentials) — a token with contents
write access to PaulKlinger/almoturg.com. Without it the GitHub step is
skipped. Optionally set `GITHUB_REPO_DIR` to a persistent checkout of
the repo to avoid cloning it fresh on every run.
