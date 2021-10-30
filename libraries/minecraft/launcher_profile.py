import os
import json
from libraries.minecraft.download_versions import search_version
import logging

class profile:

    def __init__(self, minecraft_root="."):

        self.minecraft_root = minecraft_root
        self.filename = "%s/launcher_profiles.json" % self.minecraft_root

        if os.path.isfile(self.filename) == False:
            self.auto_generate_profil()

        self.json_loaded = json.load(open(self.filename,"r"))
    
    def auto_generate_profil(self):

        launcher_json_file = open(self.filename,'w')
        launcher_json = {}

        lastest_release = {}
        lastest_release["type"] = "lastest-release"
        lastest_release["lastVersionId"] = "lastest-release"
        lastest_release["name"] = "lastest-release"
        
        lastest_snapshot = {}
        lastest_snapshot["type"] = "lastest-snapshot"
        lastest_snapshot["lastVersionId"] = "lastest-snapshot"
        lastest_snapshot["name"] = "lastest-snapshot"

        launcher_json["profiles"] = {"lastest-snapshot":lastest_snapshot,"lastest-release":lastest_release}
        launcher_json_file.write(json.dumps(launcher_json))
        launcher_json_file.close()
        
        if os.path.isfile(self.filename):
            logging.info("launcher_profiles.json created")
        else:
            logging.warning("failed to create launcher_profiles.json")

        return True

    def exist(self, profile_id):
        profiles = self.list_profiles()
        for i in profiles:
            if profile_id == "".join(list(i.keys())):
                return True
        return False
    
    def load_profile(self, profile_id=None, profile_name=None):
        profile_id_ = None

        profile_information = {}
        java_argument = None
        gameDir = None

        if profile_name != None:
            for profile_ in self.json_loaded["profiles"]:
                profile = self.json_loaded["profiles"][profile_]
                if profile["name"] == profile_name:
                    self.version = profile["lastVersionId"]

                    if "javaArgs" in profile:
                        java_argument = profile["javaArgs"]
                    
                    if "gameDir" in profile:
                        gameDir = profile["gameDir"]
                    
                    profile_id_ = profile_

        if profile_id != None:
            for profile in self.json_loaded["profiles"]:
                if profile == profile_id:
                    profile = self.json_loaded["profiles"][profile]
                    self.version = profile["lastVersionId"]
                    if "javaArgs" in profile:
                        java_argument = profile["javaArgs"]

                    if "gameDir" in profile:
                        gameDir = profile["gameDir"]

                    profile_id_ = profile_id

        if self.version == "lastest-release" or self.version == "lastest-snapshot":
            self.version = search_version().get_lastest(version_type=self.version.split("-")[1])

        logging.info("loading profile : %s" % profile_id)
        profile_information["id"] = profile_id_
        profile_information["version"] = self.version
        profile_information["javaArgs"] = java_argument
        profile_information["gameDir"] = gameDir
        
        return profile_information

    def list_profiles(self):
        logging.info("getting every profiles..")
        profiles = []
        for profile in self.json_loaded["profiles"]:
            profiles.append({profile:self.json_loaded["profiles"][profile]})
        return profiles
