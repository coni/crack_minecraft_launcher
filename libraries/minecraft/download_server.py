import libraries.utils.web as web

def download_server(manifest, path):
    exist = False
    if "downloads" in manifest:
        if "server" in manifest["downloads"]:
            url = manifest["downloads"]["server"]["url"]
            exist = web.download(url, path)
    return exist