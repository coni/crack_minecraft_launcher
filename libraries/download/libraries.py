import libraries.utils.request as request

def download_libraries(libraries, libraries_root, system):
    to_download = []
    native = "natives-%s" % system
    total_size = 0

    for i in libraries:
        url = None
        librarie_name = i["name"].split(":")
        
        filename = "%s.jar" % "-".join(librarie_name[-2:])
        path = "%s/%s" % ("/".join(librarie_name[0].split(".")), "/".join(librarie_name[1:]))
        fullpath = "%s/%s" % (path, filename)
        size = 0

        if type(libraries) == dict:
            if "url" in i:
                url = "%s/%s/%s" % (i["url"], path, filename)
                size = i["size"]
            elif "downloads" in i:
                url = i["downloads"]["artifact"]["url"]
                size = i["downloads"]["artifact"]["size"]

            if url:
                to_download.append((url,fullpath, size))

            if "natives" in i:
                if native in i["downloads"]["classifiers"]:
                    url = i["downloads"]["classifiers"][native]["url"]
                    path = "%s/%s" % (libraries_root, i["downloads"]["classifiers"][native]["path"])
                    size = i["downloads"]["classifiers"][native]["size"]
                    to_download.append((url, path, size))

        elif type(libraries) == list:
            if "url" in i:
                url = "%s/%s" % (i["url"], fullpath)
                path = "%s/%s" % (libraries_root, fullpath)
            else:
                if "downloads" in i:
                    if "artifact" in i["downloads"]:
                        url = i["downloads"]["artifact"]["url"]
                        path = "%s/%s" % (libraries_root, i["downloads"]["artifact"]["path"])
                        size = i["downloads"]["artifact"]["size"]
                    elif "classifiers" in i["downloads"]:
                        if native in i["downloads"]["classifiers"]:
                            url = i["downloads"]["classifiers"][native]["url"]
                            path = "%s/%s" % (libraries_root, i["downloads"]["classifiers"][native]["path"])
                            size = i["downloads"]["classifiers"][native]["size"]
            if url:
                to_download.append((url, path, size))
        total_size += size
    request.download(multiple_files=to_download, total_size=total_size, string="downloading libraries")