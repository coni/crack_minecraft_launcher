import os
import libraries.utils._file as _file
import libraries.utils.web as web
from libraries.launcher.openJava import get_java
from libraries.minecraft.version_parsing import parse_minecraft_version
from libraries.minecraft.launcher_profile import profile
from libraries.minecraft.download_versions import search_version
import logging
import json
import sys
import getpass
import re

class obj:
    def __init__(self):
        pass

class gally_launcher:

    def __init__(self, minecraft_root=None):
        
        self.system = _file.get_os()
        self.architechture = _file.get_architechture()
        if minecraft_root == None:
            if self.system == "windows":
                minecraft_root = "%s/.minecraft" % (os.environ["appdata"])
            elif self.system == "linux":
                minecraft_root = "%s/.minecraft" % (os.environ["HOME"])
        
        self.minecraft_root = minecraft_root
        versions_root = "versions"
        assets_root = "assets"
        libraries_root = "libraries"
        self.launcher_accounts_file = "%s/launcher_accounts.json" % (minecraft_root)
        if os.path.isfile(self.launcher_accounts_file):
            with open(self.launcher_accounts_file, "r") as json_file:
                self.launcher_accounts = json.loads(json_file.read())
        else:
            self.launcher_accounts = {}

        if "accounts" not in self.launcher_accounts:
            self.launcher_accounts["accounts"] = {}
        
        self.version = None
        self.opt_java_arg = None
        self.profile_gamedir = None
        self.profile_id = None
        self.access_token = None
        self.localid = None

        if os.path.isdir(self.minecraft_root) == False:
            _file.mkdir_recurcive(self.minecraft_root)
        
        self.version_parser = parse_minecraft_version(minecraft_root=self.minecraft_root, assets_root=assets_root, versions_root=versions_root, libraries_root=libraries_root)
        self.profile = profile(minecraft_root=self.minecraft_root)
        self.downloader = search_version(minecraft_root=self.minecraft_root)



    def load_version(self, argument):
        if self.downloader.exist(argument):
            self.downloader.download_versions(argument)
            self.version_parser.load_version(version=argument)
            self.javaVersion = self.version_parser.javaVersion
            self.version = self.version_parser.version
            return True
        else:
            print("the version does not exist")
            return False
    
    def download_java(self, version=None):

        temp_directory = None
        filename = None
        url = None
        java_directory = None

        if version == None:
            if self.javaVersion:
                version = self.javaVersion
            else:
                version = 8

        if self.system == "linux":
            try:
                temp_directory = os.environ["TMPDIR"]
            except:
                temp_directory = "/tmp"
            java_directory = "%s/.gally_launcher" % (os.environ["HOME"])
        elif self.system == "windows":
            temp_directory = os.environ["temp"]
            java_directory = "%s/gally_launcher" % (os.environ["appdata"])

        filename = "jdk-%s_%s_%s" % (version, self.system, self.architechture)
        jdk_directory = "%s/%s" % (java_directory, filename)
        url = get_java(version, self.system, self.architechture)

        if self.system == "windows":
            filename = "%s.zip" % filename
        else:
            filename = "%s.tar.gz" % filename

        if url:
            java_archive = web.download(url, "%s/%s" % (temp_directory,filename))
        else:
            logging.error("Operating System or Architecture Unknown : (%s, %s)" % (self.system, self.architechture))
            exit()
        
        if os.path.isdir(jdk_directory) == False:
            if java_archive == False:
                print("java_archive : %s" % java_archive)
                exit()
            else:
                extracted_directory = _file.extract_archive(java_archive, java_directory)
                _file.mv("%s/%s" % (java_directory, extracted_directory[0]), jdk_directory )
                
        self.java_path = "%s/bin" % jdk_directory
        return True
        

    def load_profile(self, argument):
        profile_name = None
        profile_id = None

        if "=" in argument:
            arg = argument.split("=")
            if arg[0] == "profile_id":
                profile_id = arg[1]
            elif arg[0] == "profil_name":
                profile_name = arg[1]
            else:
                print("wrong syntax")
        else:
            profile_id = argument
            
        if self.profile.exist(profile_id):
            if profile_name:
                profile_info = self.profile.load_profile(profile_name=profile_name)
            else:
                profile_info = self.profile.load_profile(profile_id=profile_id)

            self.version = profile_info["version"]
            self.opt_java_arg = profile_info["javaArgs"]
            self.profile_gamedir = profile_info["gameDir"]
            
            self.downloader.download_versions(self.version)
            self.version_parser.load_version(version=self.version)
            self.profile_id = profile_id
            return True
        else:
            print("the profile does not exist")
            return False

    def list_versions(self, argument):
        for i in self.downloader.get_versions(argument):
            print(i)
            
    def download_version(self, argument):
        self.downloader.download_versions(argument)
        self.version_parser.load_version(version=argument)
        self.version_parser.download_client()

    def list_profiles(self):
        profiles = self.profile.list_profiles()
        for i in range(len(profiles)):
            profile_id = "".join(list(profiles[i].keys()))
            profile_version = profiles[i][profile_id]["lastVersionId"]
            profile_name = profiles[i][profile_id]["name"]
            java_arg = None
            if "javaArgs" in profiles[i][profile_id]:
                java_arg = profiles[i][profile_id]["javaArgs"]
            print("\nname=%s\nprofile_id=%s\nversion=%s\njava_arg=%s\n" % (profile_name, profile_id, profile_version, java_arg))
    
    def set_username(self, argument):
        self.version_parser.set_username(argument)

    def authenticate(self, email, password):
        payload = {
            "agent" : {
                "name": "Minecraft",
                "version": "1"
            },
            "username": email,
            "password": password
        }

        headers={'Content-Type':'application/json'}
        req = web.post("https://authserver.mojang.com/authenticate", payload, headers=headers)

        if req.status == 200:
            logging.debug("authorisation granted")
            auth_response = json.loads(req.read().decode())

            self.version_parser.set_username(auth_response["selectedProfile"]["name"])
            self.access_token = auth_response["accessToken"]
            
            if self.localid == None:
                localid = web.get_uuid()

            accounts_information = {
                "accessToken" : self.access_token,
                "minecraftProfile":auth_response["selectedProfile"],
                "localId":self.localid, "username":email,
                "remoteId":auth_response["clientToken"]
            }



            self.launcher_accounts["accounts"][self.localid] = accounts_information
            _file.write_file(self.launcher_accounts_file, json.dumps(self.launcher_accounts))

        else:
            logging.error("Wrong Email or Password!")
            sys.exit()
    
    def login(self, email, password=None):
        for id in self.launcher_accounts["accounts"]:
            if self.launcher_accounts["accounts"][id]["username"] == email:
                self.localid = id
                if "accessToken" in self.launcher_accounts["accounts"][id]:
                    self.access_token = self.launcher_accounts["accounts"][id]["accessToken"]
                    self.set_username(self.launcher_accounts["accounts"][id]["minecraftProfile"]["name"])
                    client_token = self.launcher_accounts["accounts"][id]["remoteId"]
                    if self.validate(self.access_token, client_token) == False:
                        if self.refresh(self.access_token, client_token) == True:
                            return True
                    else:
                        return True
                continue

        if password == None:
            password = getpass.getpass("Password to Login : ")
        self.authenticate(email, password)

    def logout(self, email, password=None):
        headers={'Content-type':'application/json'}

        for id in self.launcher_accounts["accounts"]:
            self.localid = id
            if self.launcher_accounts["accounts"][id]["username"] == email:
                if "accessToken" not in self.launcher_accounts["accounts"][id]:
                    continue
                accessToken = self.launcher_accounts["accounts"][id]["accessToken"]
                clientToken = self.launcher_accounts["accounts"][id]["remoteId"]
                payload = {
                    "accessToken": accessToken,
                    "clientToken": clientToken
                }
                if web.post("https://authserver.mojang.com/invalidate", payload, headers=headers).status == 204:
                    self.launcher_accounts["accounts"].pop(id)

                    _file.write_file(self.launcher_accounts_file, json.dumps(self.launcher_accounts))
                    return True
                else:
                    return False
            continue

        if password == None:
            password = getpass.getpass("Password to Logout : ")

        payload = {
            "username": email,
            "password": password
        }
        resp = web.post("https://authserver.mojang.com/signout", payload, headers=headers)
        if resp.status == 200 or resp.status == 204:
            return True
        else:
            return False

    def refresh(self, accessToken, clientToken):
        payload = {
            "accessToken": accessToken,
            "clientToken": clientToken
        }
        headers={'Content-type':'application/json'}
        resp = web.post("https://authserver.mojang.com/refresh", payload, headers=headers)

        if resp.status == 200 or resp.status == 204:
            auth_response = json.loads(resp.read())
            if "accessToken" in auth_response:
                self.access_token = auth_response["accessToken"]
                self.launcher_accounts["accounts"][self.localid]["accessToken"] =  self.access_token
                _file.write_file(self.launcher_accounts_file, json.dumps(self.launcher_accounts))
                return True
        else:
            return False

    def validate(self, accessToken, clientToken):
        payload = {
            "accessToken": accessToken,
            "clientToken": clientToken
        }
        
        headers = {'Content-type':'application/json'}
        resp = web.post("https://authserver.mojang.com/validate", payload, headers=headers)

        if resp.status == 204:
            return True
        else:
            return False

    def start(self, assets=True, java=None, console=False, java_argument=None, game_directory=None, debug=False, dont_start=False):
        if game_directory == None:
            game_directory = self.profile_gamedir

        logging.info("checking client")
        self.version_parser.download_client()
        logging.info("checking library")
        self.version_parser.download_libraries()

        if assets == True:
            logging.info("checking assets")
            self.version_parser.download_assets()
            
        logging.info("checking binary")
        self.version_parser.download_binary()

        if java == None:
            if console:
                java = "java"
            else:
                if self.system == "windows":
                    java = "javaw"
                else:
                    java = "java"

            java = "%s/%s" % (self.java_path, java)
            
        JAVA_ARGUMENT = []
        
        classpath = None
        if os.path.isfile("debug/classpath"):
           with open("debug/classpath",'r') as classpath_file:
            classpath = classpath_file.read()
        
        mainclass = self.version_parser.get_mainclass()
        if os.path.isfile("debug/mainclass"):
            with open("debug/mainclass", "r") as mainclass_file:
                mainclass = mainclass_file.read()

        if os.path.isfile("debug/game_argument"):
            with open("debug/game_argument", "r") as game_argument_file:
                game_argument = [game_argument_file.read()]
        else:
            game_argument = self.version_parser.get_minecraft_arguments(access_token=self.access_token, game_directory=game_directory)

        default_arguments = []

        if java_argument:
            default_arguments = java_argument
        elif self.opt_java_arg:
            default_arguments = self.opt_java_arg
        else:
            default_arguments = self.version_parser.get_default_java_arguments()
        if type(default_arguments) == str:
            default_arguments = [default_arguments]

        if os.path.isfile("debug/java_argument"):
            os.environ["classpath"] = classpath
            with open("debug/java_argument", "r") as java_argument_file:
                java_argument = [java_argument_file.read()]
        else:
            java_argument = default_arguments + self.version_parser.get_java_arguments(classpath=classpath)


        arguments = [java_argument, mainclass, game_argument]
        for argument in arguments:
            if type(argument) == list:
                JAVA_ARGUMENT += argument
            elif type(argument) == str:
                JAVA_ARGUMENT.append(argument)

        JAVA_ARGUMENT = " ".join(JAVA_ARGUMENT)
        
        if debug:
            debug_path = "debug/%s" % self.version
            _file.write_file("%s/classpath" % debug_path, os.environ["classpath"])
            _file.write_file("%s/mainclass" % debug_path, mainclass)
            _file.write_file("%s/java_argument" % debug_path, " ".join(java_argument))
            _file.write_file("%s/game_argument" % debug_path, " ".join(game_argument))
            _file.write_file("%s/java" % debug_path, java)
        
        _file.chdir(self.minecraft_root)
            
        command = "\"%s\" %s" % (java, JAVA_ARGUMENT)
        if console == False:
            if self.system == "linux":
                command = "nohup \"%s\" %s >/dev/null 2>&1 " % (java, JAVA_ARGUMENT)
            elif self.system == "windows":
                command = "start \"\" \"%s\" %s" % (java, JAVA_ARGUMENT)
                

        if self.access_token:
            logging.debug(command.replace(self.access_token, "??????????"))
        else:
            logging.debug(command)

        if dont_start == False:
            logging.info("starting Minecraft.. please wait")
            _file.command(command, console=console)
