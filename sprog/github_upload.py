import os
import shutil
import subprocess
import tempfile

import boto3


REPO_URL = "https://github.com/PaulKlinger/almoturg.com.git"
REPO_BRANCH = "master"

# (source relative to the backend working directory, destination in the
# almoturg.com repo). Paths match upload_sprog_to_namecheap, except
# sprog.html is stored twice: it is served both at /sprog.html and at
# /sprog/ (as sprog/index.html) on the old hosting.
#
# The two PDFs are deliberately NOT in this list: Workers Static Assets
# caps files at 25 MiB and each PDF is ~45 MB, so they go to the R2
# bucket instead (upload_pdfs_to_r2 below) and the Worker serves them
# from there at their usual URLs.
FILES = [
    ("sprog.rss", "content/sprog.rss"),
    ("sprog_no_context.rss", "content/sprog_no_context.rss"),
    ("poems.json", "content/poems.json"),
    ("poems.json.gz", "content/poems.json.gz"),
    ("poems_60days.json.gz", "content/poems_60days.json.gz"),
]
HTML_SOURCE = "sprog.html"  # lives in tmpdir, not the working directory
HTML_DESTINATIONS = ("content/sprog.html", "content/sprog/index.html")

R2_BUCKET = "almoturg-sprog"
# (local file, object key in the R2 bucket). The Worker serves these at
# their usual URLs (/sprog.pdf, /sprog_small.pdf).
R2_FILES = [
    ("sprog.pdf", "sprog.pdf"),
    ("small_sprog.pdf", "sprog_small.pdf"),
]


def _run(cmd, cwd, token=None):
    # Never log the token: it is part of the clone URL, so keep command
    # output free of it by never printing cmd.
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "command failed (exit {}): {}".format(result.returncode, result.stderr.strip())
        )
    return result.stdout.strip()


def upload_sprog_to_github(tmpdir, passwords):
    """Push the generated sprog files to the almoturg.com repo.

    Runs in parallel with the Namecheap FTP upload: the site is served
    from the repo (Cloudflare Workers Static Assets, same setup as
    paulklinger.com), so each backend update keeps it current. The two
    PDFs are not pushed here — see upload_pdfs_to_r2.

    Needs passwords["GITHUB_TOKEN"]: a token with contents write access
    to PaulKlinger/almoturg.com. If it is not set, this step is skipped
    (the Namecheap upload is unaffected). If passwords["GITHUB_REPO_DIR"]
    is set, that persistent checkout is reused (pulled first) instead of
    cloning the repo fresh into a temporary directory each run.
    """
    token = passwords.get("GITHUB_TOKEN")
    if not token:
        print("no GITHUB_TOKEN set, skipping GitHub upload")
        return

    repo_dir = passwords.get("GITHUB_REPO_DIR")
    tmp_repo = None
    try:
        if repo_dir:
            print("pulling almoturg.com repo in {}".format(repo_dir))
            _run(["git", "pull", "--rebase", "origin", REPO_BRANCH], cwd=repo_dir)
        else:
            tmp_repo = tempfile.mkdtemp(prefix="almoturg-com-")
            print("cloning almoturg.com repo")
            authed_url = REPO_URL.replace("https://", "https://{}@".format(token), 1)
            _run(["git", "clone", "--branch", REPO_BRANCH, authed_url, tmp_repo],
                 cwd=".")
            repo_dir = tmp_repo

        _run(["git", "config", "user.name", "Sprog Backend"], cwd=repo_dir)
        _run(["git", "config", "user.email", "klinger.paul+automation@gmail.com"],
             cwd=repo_dir)

        print("copying sprog files into repo")
        for source, dest in FILES:
            dest_path = os.path.join(repo_dir, dest)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copyfile(source, dest_path)
        html_source = os.path.join(tmpdir, HTML_SOURCE)
        for dest in HTML_DESTINATIONS:
            dest_path = os.path.join(repo_dir, dest)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copyfile(html_source, dest_path)

        _run(["git", "add", "-A"], cwd=repo_dir)
        status = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_dir)
        if status.returncode == 0:
            print("no changes to push to GitHub")
            return
        _run(["git", "commit", "-m",
              "Update sprog files\n\nAutomated sync from Sprog-Backend, "
              "in parallel with the Namecheap FTP upload."],
             cwd=repo_dir)
        _run(["git", "push", "origin", REPO_BRANCH], cwd=repo_dir)
        print("pushed sprog files to GitHub")
    finally:
        if tmp_repo:
            shutil.rmtree(tmp_repo, ignore_errors=True)


def upload_pdfs_to_r2(passwords):
    """Upload the two PDFs to the Cloudflare R2 bucket.

    The Worker serves them from R2 at their usual URLs (/sprog.pdf,
    /sprog_small.pdf). They must not go into the repo, which Workers
    Static Assets caps at 25 MiB per file.

    Needs passwords["R2_ACCOUNT_ID"] (the Cloudflare account id, as
    shown in the dashboard URL), passwords["R2_ACCESS_KEY_ID"] and
    passwords["R2_SECRET_ACCESS_KEY"] — an R2 API token with Object
    Read & Write on the almoturg-sprog bucket (Cloudflare dashboard:
    R2 -> Manage R2 API Tokens -> Create API token). If any of them is
    not set, this step is skipped (the repo push is unaffected).
    """
    account_id = passwords.get("R2_ACCOUNT_ID")
    access_key = passwords.get("R2_ACCESS_KEY_ID")
    secret_key = passwords.get("R2_SECRET_ACCESS_KEY")
    if not (account_id and access_key and secret_key):
        print("R2 credentials not set, skipping R2 upload")
        return

    s3 = boto3.resource(
        "s3",
        endpoint_url="https://{}.r2.cloudflarestorage.com".format(account_id),
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    bucket = s3.Bucket(R2_BUCKET)
    for source, key in R2_FILES:
        bucket.upload_file(source, key,
                           ExtraArgs={"ContentType": "application/pdf"})
    print("uploaded PDFs to R2 bucket {}".format(R2_BUCKET))
