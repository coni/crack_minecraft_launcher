import libraries.utils.web as web
import json

def download_assets(manifest, path):
        to_download = []
        if "assetIndex" not in manifest:
            return False

        asset_index_url = manifest["assetIndex"]["url"]
        asset_index_filename = manifest["assetIndex"]["id"]
        asset_index_fullpath = "%s/indexes/%s.json" % (path, asset_index_filename)

        if "logging" in manifest:
            config_filename = manifest["logging"]["client"]["file"]["id"]
            config_url = manifest["logging"]["client"]["file"]["url"]
            config_fullpath = "%s/log_configs/%s" % (path, config_filename)
            web.download(config_url, config_fullpath)

        web.download(asset_index_url, asset_index_fullpath)
        with open(asset_index_fullpath,'r') as asset_index_file:
            asset_index_json = json.load(asset_index_file)

        total_size = 0
        to_download = []
        for i in asset_index_json["objects"]:
            asset_hash = asset_index_json["objects"][i]["hash"]
            asset_folder = asset_hash[:2]
            asset_path =  "%s/objects/%s/%s" % (path, asset_folder, asset_hash)
            url = "https://resources.download.minecraft.net/%s/%s" % (asset_folder, asset_hash)
            size = asset_index_json["objects"][i]["size"]
            total_size += size
            to_download.append((url, asset_path, size))
        
        web.download(multiple_files=to_download, total_size=total_size, string="downloading assets")
