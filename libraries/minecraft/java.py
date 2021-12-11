import libraries.utils.web as web
import libraries.utils._file as _file
import os
import json

system = _file.get_os()
if system == "linux":
    try:
        temp_directory = os.environ["TMPDIR"]
    except:
        temp_directory = "/tmp"
    delim = "/"
elif system == "windows":
    temp_directory = os.environ["temp"]
    delim = "\\"

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
    to_download = []
    executable = []
    total_size = 0
    for item in manifest["files"]:
        item_path = path + delim + item
        if manifest["files"][item]["type"] == "directory":
            if os.path.isdir(item_path) == False:
                _file.mkdir_recurcive(item_path)
        elif manifest["files"][item]["type"] == "file":
            url = manifest["files"][item]["downloads"]["raw"]["url"]
            size = manifest["files"][item]["downloads"]["raw"]["size"]
            to_download.append((url, item_path, size))
            if manifest["files"][item]["executable"] == True:
                executable.append(item_path)
            total_size += size
            

    web.download(multiple_files=to_download, total_size=total_size, string="downloading java")
    if system == "linux":
        for i in executable:
            _file.command("chmod +x %s" % i)
    