import libraries.utils.request as request

def download_server(manifest, path):
    exist = False
    if "downloads" in manifest:
        if "server" in manifest["downloads"]:
            url = manifest["downloads"]["server"]["url"]
            exist = request.download(url, path)
    return exist