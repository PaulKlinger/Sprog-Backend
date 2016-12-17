import pysftp


def upload_sprog_to_namecheap():
    with pysftp.Connection('***REMOVED***', username='***REMOVED***', password='***REMOVED***', port=***REMOVED***) as sftp:
        with sftp.cd('public_html'):
            print("uploading sprog.pdf")
            sftp.put("sprog.pdf")
            print("uploading sprog_small.pdf")
            sftp.put("small_sprog.pdf", "sprog_small.pdf")
            print("uploading sprog.html")
            sftp.put("tmp/sprog.html", "sprog.html")
            print("uploading sprog.json")
            sftp.put("sprog.json", "sprog.json")
