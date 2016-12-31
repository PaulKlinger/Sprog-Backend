def add_submission(poems, link):
    """Add a submission (currently not running automatically because most submissions aren't poems)"""
    if link in (p.link for p in poems):
        print("submission already stored")
        return
    submission = r.submission(url=link)
    time = datetime.datetime.utcfromtimestamp(submission.created_utc)
    for i in range(len(poems) - 1):
        if poems[i].datetime > time > poems[i + 1].datetime:
            poems.insert(i + 1, Poem.from_comment(submission, is_submission=True))
            return

# ----------------------------------
# useful snippets
# ----------------------------------

# remove double spacing except between verses
# (sprog only used this on early poems so this doesn't need to run all the time)
# \r\n\r\n should be readded between \end{itemize} and \emph to prevent an error,
# I did this manually for the six cases where it occurred.
#
# As markdown is now converted every run this is done in poem_md_to_latex now
for p in poems[-142:]:
    p.content = re.sub("(?:(?<!})\r\n\r\n(?!\\\\emph))|(?:(?<=})\r\n\r\n(?=\\\\emph))", r"\\\\", p.content)

# this was in load_poems_json to manually add orig_content to comments without it
for parent in p["parents"]:
    if parent["orig_body"] is None and "body" in parent and parent["body"] and parent["link"] is None:
        print()
        print(parent["body"])
        print(parent["author"])
        print(p["link"] + "?context=10000")
        parent_link = input()
        if parent_link == "o":
            parent["orig_body"] = parent["body"]
        elif parent_link == "d":
            parent["orig_body"] = "[deleted]"
        else:
            try:
                c = get_comment_from_link(parent_link[:-1])
            except Exception as e:
                print("error:")
                print(e)
                input("enter to continue with next comment")
            else:
                print(c.body)
                yn = input("non-empty to accept")
                if yn:
                    parent["link"] = c.permalink
                    parent["orig_body"] = c.body