import libraries.utils.web as web
import libraries.utils._file as _file
import os
import json

temp_directory = "/tmp"
java_manifest = "https://launchermeta.mojang.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json"

def get_manifest(platform, component):
    java_manifest_path = temp_directory + "/all.json"
    java_manifest_json = None
    url = None
    if web.download(java_manifest, java_manifest_path):
        with open(java_manifest_path, "r") as temp:
            java_manifest_json = json.load(temp)
        url = java_manifest_json[platform][component][0]["manifest"]["url"]
    return url

def download_java(manifest, path):
    for item in manifest["files"]:
        item_path = path + "/" + item
        if manifest["files"][item]["type"] == "directory":
            if os.path.isdir(item_path) == False:
                _file.mkdir_recurcive(item_path)
        elif manifest["files"][item]["type"] == "file":
            if web.download(manifest["files"][item]["downloads"]["raw"]["url"], item_path):
                if manifest["files"][item]["executable"]:
                    _file.command("chmod +x %s" % item_path)
            