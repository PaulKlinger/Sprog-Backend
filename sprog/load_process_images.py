import subprocess
import requests
import os
import re
import datetime


def download_file(url: str, filename: str) -> None:
    try:
        with open(filename, 'wb') as f:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            if "Content-Type" in response.headers:
                if "gif" in response.headers["Content-Type"]:
                    raise ValueError("Image {} is a gif".format(url))
                if "text" in response.headers["Content-Type"]:
                    raise ValueError("Got text instead of image from {}".format(url))
            if "removed.png" in response.url:
                raise FileNotFoundError("Image {} deleted".format(url))
            size = 0
            for block in response.iter_content(1024):
                size += len(block)
                if size >= 5.243 * 10 ** 6:  # > 5 MiB
                    raise ValueError("File {} too big".format(url))
                if not block:
                    break
                f.write(block)
            if size < 500:
                raise ValueError("File {} too small".format(url))
    except Exception as e:
        os.remove(filename)
        raise e


def get_image_url_from_link(url):
    if "imgur" in url and not url[-3:] in ("jpg", "png", "gif", "ifv", "ebm"):
        return url + ".jpg"
    elif url[-3:] in ("jpg", "png"):
        return url
    return None


def create_image_filename(timestamp, imgurl):
    tstring = timestamp.strftime("%Y_%m_%dT%H_%M_%S")
    # create imgname from last url segment by filtering out anything that isn't a valid filename character
    imgname = "".join([c for c in imgurl.split("/")[-1] if c.isalnum() or c in ' _.']).rstrip()
    imgfilename = "{}_{}".format(tstring, imgname)
    return imgfilename


def download_image(tmpdir: str, imgurl: str, imgfilename: str) -> bool:
    print("loading " + imgurl)
    try:
        if not os.path.isfile(os.path.join(tmpdir, imgfilename)):
            download_file(imgurl, os.path.join(tmpdir, imgfilename))
        else:
            print(imgurl + " already loaded")
    except Exception as e:
        print("Failed to download Image: " + str(e))
        return False
    else:
        return True


def get_images_from_tex(tmpdir: str, tex: str, timestamp: datetime.datetime):
    for m in re.finditer(r"(?:\\href{)?(?:\\url{)?(https?://\S+/[\w/.\-?]+)(?:(?:}{(.*?)})|})?", tex,
                         re.MULTILINE | re.DOTALL):

        imgurl = get_image_url_from_link(m.group(1))
        if imgurl:
            imgfilename = create_image_filename(timestamp, imgurl)
            if download_image(tmpdir, imgurl, imgfilename):
                includeimg = r"{}~\\ \includegraphics[keepaspectratio," \
                             r"max width=0.5\textwidth, max height=0.75\textwidth]" \
                             r'{{"{}"}}\\'.format(m.group(2) or "", imgfilename)
                tex = tex.replace(m.group(0), includeimg)
    return tex


def get_images(tmpdir, poems):
    for p in poems:
        if p.submission_url and not p.noimg and not p.imgfilename:
            imgurl = get_image_url_from_link(p.submission_url)
            if imgurl:
                imgfilename = create_image_filename(p.datetime, imgurl)
                if download_image(tmpdir, imgurl, imgfilename):
                    p.imgfilename = imgfilename
                else:
                    p.noimg = True
        else:
            p.submission_content = get_images_from_tex(tmpdir, p.submission_content, p.datetime)

        for i, c in enumerate(p.parents):
            c["body"] = get_images_from_tex(tmpdir, c["body"], p.datetime)
    return poems


def process_images():
    """scale images to a maximum resolution of 2000x2000 and set dpi to 300 (for auto scaling of images)"""
    command = r'mogrify -verbose -resize "2000x2000>" -units "pixelsperinch" -density "150x150" tmp/*.png tmp/*.jpg'
    subprocess.call(command, shell=True)
