import libraries.utils.request as request

def download_client(manifest, path, version):
    path = "%s/%s.jar" % (path, version)
    if "downloads" in manifest:
        url = manifest["downloads"]["client"]["url"]
        size = manifest["downloads"]["client"]["size"]
        request.download(url, path, total_size=size, string="downloading client")