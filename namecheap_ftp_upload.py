import pysftp
from sprog_auth import NAMECHEAP_SERVER, NAMECHEAP_USERNAME, NAMECHEAP_PASSWORD, NAMECHEAP_PORT


def upload_sprog_to_namecheap():
    with pysftp.Connection(NAMECHEAP_SERVER, username=NAMECHEAP_USERNAME,
                           password=NAMECHEAP_PASSWORD, port=NAMECHEAP_PORT) as sftp:
        with sftp.cd('public_html'):
            print("uploading sprog.pdf")
            sftp.put("sprog.pdf")
            print("uploading sprog_small.pdf")
            sftp.put("small_sprog.pdf", "sprog_small.pdf")
            print("uploading sprog.html")
            sftp.put("tmp/sprog.html", "sprog.html")
            print("uploading sprog.json")
            sftp.put("poems.json", "poems.json")
