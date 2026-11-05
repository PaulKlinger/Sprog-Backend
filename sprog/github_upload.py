import os
import shutil
import subprocess
import tempfile


REPO_URL = "https://github.com/PaulKlinger/almoturg.com.git"
REPO_BRANCH = "master"

# (source relative to the backend working directory, destination in the
# almoturg.com repo). Paths match upload_sprog_to_namecheap, except
# sprog.html is stored twice: it is served both at /sprog.html and at
# /sprog/ (as sprog/index.html) on the old hosting.
FILES = [
    ("sprog.pdf", "content/sprog.pdf"),
    ("small_sprog.pdf", "content/sprog_small.pdf"),
    ("sprog.rss", "content/sprog.rss"),
    ("sprog_no_context.rss", "content/sprog_no_context.rss"),
    ("poems.json", "content/poems.json"),
    ("poems.json.gz", "content/poems.json.gz"),
    ("poems_60days.json.gz", "content/poems_60days.json.gz"),
]
HTML_SOURCE = "sprog.html"  # lives in tmpdir, not the working directory
HTML_DESTINATIONS = ("content/sprog.html", "content/sprog/index.html")


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
    paulklinger.com), so each backend update keeps it current.

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
            shutil.copyfile(source, os.path.join(repo_dir, dest))
        html_source = os.path.join(tmpdir, HTML_SOURCE)
        for dest in HTML_DESTINATIONS:
            shutil.copyfile(html_source, os.path.join(repo_dir, dest))

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
