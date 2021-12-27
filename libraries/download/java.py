import libraries.utils.request as request
import libraries.utils.system as system
import os
import json

osNamae = system.get_os()
if osNamae == "linux":
    try:
        temp_directory = os.environ["TMPDIR"]
    except:
        temp_directory = "/tmp"
    delim = "/"
elif osNamae == "windows":
    temp_directory = os.environ["temp"]
    delim = "\\"

java_manifest = "https://launchermeta.mojang.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json"

def get_manifest(platform, component, path):
    java_manifest_path = path + "/all.json"
    java_manifest_json = None
    url = None
    if request.download(java_manifest, java_manifest_path):
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
                system.mkdir_recurcive(item_path)
        elif manifest["files"][item]["type"] == "file":
            url = manifest["files"][item]["downloads"]["raw"]["url"]
            size = manifest["files"][item]["downloads"]["raw"]["size"]
            to_download.append((url, item_path, size))
            if manifest["files"][item]["executable"] == True:
                executable.append(item_path)
            total_size += size
            

    request.download(multiple_files=to_download, total_size=total_size, string="downloading java")
    if osNamae == "linux":
        for i in executable:
            system.command("chmod +x %s" % i)
    