import libraries.utils.web as web
import os

def download_client(manifest, path, version):
    path = "%s/%s.jar" % (path, version)
    if os.path.isfile(path) == False:
        if "downloads" in manifest:
            url = manifest["downloads"]["client"]["url"]
            size = manifest["downloads"]["client"]["size"]
            web.download(url, path, total_size=size)