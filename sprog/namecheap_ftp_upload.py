import pysftp
import os.path


def upload_sprog_to_namecheap(tmpdir, passwords):
    with pysftp.Connection(passwords["NAMECHEAP_SERVER"], username=passwords["NAMECHEAP_USERNAME"],
                           password=passwords["NAMECHEAP_PASSWORD"], port=passwords["NAMECHEAP_PORT"]) as sftp:
        with sftp.cd('public_html'):
            print("uploading sprog.pdf")
            sftp.put("sprog.pdf")
            print("uploading sprog_small.pdf")
            sftp.put("small_sprog.pdf", "sprog_small.pdf")
            print("uploading sprog.html")
            sftp.put(os.path.join(tmpdir, "sprog.html"), "sprog.html")
            print("uploading sprog.json")
            sftp.put("poems.json", "poems.json")
            print("uploading sprog.json.gz")
            sftp.put("poems.json.gz", "poems.json.gz")
            print("uploading sprog_60days.json.gz")
            sftp.put("poems_60days.json.gz", "poems_60days.json.gz")
            print("uploading sprog.rss")
            sftp.put("sprog.rss", "sprog.rss")
            print("uploading sprog_no_context.rss")
            sftp.put("sprog_no_context.rss", "sprog_no_context.rss")
