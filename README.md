# Sprog Backend

Backend for [https://almoturg.com/sprog/](https://almoturg.com/sprog/) and the [Sprog Android App](https://github.com/PaulKlinger/Sprog-App).

Gets new reddit comments by /u/Poem_for_your_sprog, creates pdf collections of them, and stores them as json. Results are uploaded to https://almoturg.com/sprog

In addition to the Python packages specified in requirements.txt the following external tools are required
* A LaTeX installation with XeLateX (e.g. [TexLive](https://www.tug.org/texlive/)) and the following packages: babel, geometry, tcolorbox, verse, eurosym, ulem, graphicx, subcaption, float, adjustbox, scalerel, fontspec, varwidth, longtable, booktabs, fancyvrb, microtype, titlesec, hyperref, xcolor
* [mogrify](http://www.imagemagick.org/script/mogrify.php) (part of [ImageMagick](http://www.imagemagick.org/))
## Uploads

Each run uploads the generated files to Amazon S3 and pushes them to the
[almoturg.com repo](https://github.com/PaulKlinger/almoturg.com): the site
is served from that repo (Cloudflare Workers Static Assets, same setup as
paulklinger.com), so each update keeps the live site current. The GitHub
push is best-effort — if it fails, the run still completes, but the live
site won't update until the next successful run.

The two PDFs are the exception: they are ~45 MB each, over Workers
Static Assets' 25 MiB per-file limit, so they are not pushed to the
repo. Instead they are uploaded to the Cloudflare R2 bucket
`almoturg-sprog`, from which the Worker serves them at their usual
URLs (`/sprog.pdf`, `/sprog_small.pdf`).

Setup: add `GITHUB_TOKEN` to the `sprog` secret in AWS Secrets Manager
— a token with contents write access to PaulKlinger/almoturg.com.
Without it the GitHub step is skipped. Optionally set `GITHUB_REPO_DIR`
to a persistent checkout of the repo to avoid cloning it fresh on every
run. For the R2 step add `R2_ACCOUNT_ID` (the Cloudflare account id, as
shown in the dashboard URL), `R2_ACCESS_KEY_ID` and
`R2_SECRET_ACCESS_KEY` to the same secret — an R2 API token with Object
Read & Write on the `almoturg-sprog` bucket (Cloudflare dashboard: R2
-> Manage R2 API Tokens -> Create API token). Without them the R2 step
is skipped.
