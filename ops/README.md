# Sprog host operations

How the backend runs, and how to rebuild the host from scratch. Nothing in
this folder (or the repo) holds a secret — secrets live on the machine only
(see below).

## What runs where

- EC2 instance "Sprog" (`i-08ac4dc4d1a25b815`), eu-west-1, started twice a day
  by Lambda + EventBridge. On boot it pulls this repo, runs the update,
  uploads the results, and shuts itself down. It is Stopped the rest of the
  time.
- Lambda `start_sprog_instance`
  (`aws_lambda_scripts/start_sprog_instance.py`, Python 3.12, 128 MB, 10 s) —
  starts the instance. Triggered by EventBridge rule `1am_1pm`, cron
  `0 1,13 * *? *` (01:00 and 13:00 UTC).
- Lambda `rolling_snapshots`
  (`aws_lambda_scripts/rolling_snapshots.py`, Python 3.12, 128 MB, 60 s) —
  snapshots the root volume daily and deletes snapshots older than 14 days
  (each snapshot is tagged with a DeleteOn date 2 days out). Triggered by
  EventBridge rule `daily_2am`, cron `0 2 * *? *` (02:00 UTC). The timeout
  was 3 s until Nov 2026 — too short for a snapshot + list + delete pass,
  which is likely why snapshots were sparse; 60 s is the current value.
- AWS account 681414469766, region eu-west-1.

## The host (current, built 5 Nov 2026)

- t2.micro, Amazon Linux 2023 (AMI `ami-00fcaf85b81e85b1d`,
  2023.12.20261102.0), 8 GiB gp3 root volume (`vol-04507e8239e10fff9`),
  eu-west-1a, VPC `vpc-b7cba5d3`, subnet `subnet-83750df5`, security group
  `sg-9c5a88fa` (launch-wizard-2; SSH open to 0.0.0.0/0 — inherited from the
  2016 setup, tighten if rebuilding).
- No key pair; IMDSv2 required; termination protection on.
- Packages: git, Python 3.9, cronie (crond), ImageMagick, TeX Live
  scheme-medium plus `texlive-verse` and `texlive-scalerel`. scheme-medium
  lacks verse and scalerel — the only two of the template's 20 LaTeX
  packages it was missing. xelatex is at /bin/xelatex.
- Python venv at /home/ec2-user/sprog-venv with everything in
  requirements.txt installed (praw 5.4.0, boto3, matplotlib, pandas, pysftp,
  mako). The repo pins praw<6.0.0; version bumps belong in requirements.txt,
  not on the machine.
- Checkout at /home/ec2-user/sprog, cloned from this public repo (pulls need
  no credentials). The machine pulls `master` on every boot.
- Boot script `run_sprog.sh`, installed at /home/ec2-user/run_sprog.sh, run by
  cron at boot: `@reboot /home/ec2-user/run_sprog.sh` in ec2-user's crontab.
  It pulls master, runs main.py, then shuts the machine down 10 minutes
  later. The instance must be Stopped for the schedule to start it — a start
  call on a running instance does nothing.
- State lives in the checkout directory and is NOT in this repo: poems.json
  (4,147 entries), deleted_poems.json. Copy them across when rebuilding; the
  run updates them in place.
- Secrets live on the machine only, never in this repo (see .gitignore):
  `sprog_auth.py` (`passwords` dict: AWS_ACCESS_KEY, AWS_SECRET_KEY,
  NAMECHEAP_SERVER, NAMECHEAP_USERNAME, NAMECHEAP_PASSWORD, NAMECHEAP_PORT,
  FCM_KEY; plus GITHUB_TOKEN and R2_ACCOUNT_ID / R2_ACCESS_KEY_ID /
  R2_SECRET_ACCESS_KEY once the R2 upload is enabled) and `praw.ini`
  ([DEFAULT]: client_id, client_secret, user_agent).

## Uploads

- Each run uploads to Amazon S3. The
  GitHub/R2 upload (live site) is in PR #5, not yet merged — until it is
  merged and the R2 + GitHub secrets are added to the `sprog` secret in
  Secrets Manager, runs do not update almoturg.com. (The old Namecheap
  SFTP upload was dropped when the hosting expired: the site no longer
  uses it, and a dead upload step could fail the run before the
  GitHub/R2 steps.)
- The FCM notification step at the end of each run fails with a 404 (legacy
  FCM API is dead; the Android app is gone). It is dead weight and should be
  removed (GitHub PR).

## Rebuilding from scratch

1. Launch the instance as above; install the packages; create the venv and
   install requirements.txt.
2. Clone this repo to /home/ec2-user/sprog; copy poems.json,
   deleted_poems.json, sprog_auth.py and praw.ini from the old host.
3. Install `ops/run_sprog.sh` at /home/ec2-user/run_sprog.sh; add the
   @reboot crontab line; enable termination protection.
4. Create/update the two Lambdas from `aws_lambda_scripts/` (Python 3.12 —
   AWS refuses to create or update functions on python2.7/python3.6) and the
   two EventBridge rules with the cron expressions above.
5. Test with a manual start: the machine should boot, run, upload, and shut
   itself down in ~25 minutes. Then stop it and let the schedule take over.
6. Keep the old host stopped as a fallback until a few scheduled runs have
   succeeded.

## Retired host

- `i-00c8bff4207d0e201` ("Sprog-old-AL1"), t2.nano, Amazon Linux 1 (AMI
  2018.03, Python 3.5, TeX Live 2016), volume `vol-0e3fe6bd947540db4` (5 GiB
  gp2). Stopped, termination protection on. Its checkout pulled from
  Bitbucket (`git@bitbucket.org:Almoturg/sprog.git`) at fd238ee (2021) —
  GitHub PRs never reached it. 217 snapshots of its volume exist. Retire it
  (and the snapshots) after a few good runs on the new host.
- The inspection copy volume `vol-0011c2955066d8ffe` (from
  snap-0be737d83fb7cfb0e) is still attached to the new host as /dev/sdf —
  detach and delete it after the first good scheduled run.

## Quirks worth knowing

- xelatex runs interactively: on failure it sits at a prompt (quit with X).
  The code doesn't check xelatex's exit status before the second pass.
- Page counts differ slightly from the old TeX Live 2016 builds (3,764 vs
  3,779 pages for sprog.pdf) — newer TeX Live rendering, same poems.
- In the console, a Lambda's Runtime is shown under "Runtime settings" on
  the Code tab, not under Configuration > General configuration.
