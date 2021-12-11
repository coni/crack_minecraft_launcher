import os
import libraries.utils._file as _file
import libraries.utils.web as web
from libraries.launcher.openJava import get_java
from libraries.minecraft.version_parsing import parse_minecraft_version
from libraries.minecraft.launcher_profile import profile
from libraries.minecraft.download_versions import search_version
from libraries.minecraft.download_libraries import download_libraries
from libraries.minecraft.download_client import download_client
from libraries.minecraft.download_assets import download_assets
from libraries.minecraft.download_lwjgl import download_binary
import logging
import json
import sys
import getpass
import re

system = _file.get_os()
if system == "linux":
    try:
        temp_directory = os.environ["TMPDIR"]
    except:
        temp_directory = "/tmp/gally_launcher"
elif system == "windows":
    temp_directory = os.environ["temp"] + "/gally_launcher"
_file.mkdir_recurcive(temp_directory)

class obj:
    def __init__(self):
        pass

class gally_launcher:
    def __init__(self, minecraft_root=None):
        
        self.system = system
        self.architecture = _file.get_architechture()
        if minecraft_root == None:
            if self.system == "windows":
                minecraft_root = "%s/.minecraft" % (os.environ["appdata"])
                self.classpath_separator = ";"
            elif self.system == "linux":
                minecraft_root = "%s/.minecraft" % (os.environ["HOME"])
                self.classpath_separator = ":"
        
        self.minecraft_root = minecraft_root
        self.versions_root = "%s/versions" % self.minecraft_root
        self.assets_root = "%s/assets" % self.minecraft_root
        self.libraries_root = "%s/libraries" % self.minecraft_root
        self.binary_root = "%s/bin" % self.minecraft_root

        self.launcher_accounts_file = "%s/launcher_accounts.json" % (minecraft_root)
        if os.path.isfile(self.launcher_accounts_file):
            with open(self.launcher_accounts_file, "r") as json_file:
                self.launcher_accounts = json.loads(json_file.read())
        else:
            self.launcher_accounts = {}

        if "accounts" not in self.launcher_accounts:
            self.launcher_accounts["accounts"] = {}
        
        self.uuid = None
        self.version = None
        self.username = "steve"
        self.opt_java_arg = None
        self.profile_gamedir = None
        self.profile_id = None
        self.access_token = "None"
        self.localid = None

        if os.path.isdir(self.minecraft_root) == False:
            _file.mkdir_recurcive(self.minecraft_root)
        
        self.version_parser = parse_minecraft_version(system=self.system, minecraft_root=self.minecraft_root, versions_root=self.versions_root)
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
    
    def get_jar(self):
        default_jar = "%s/%s/%s.jar" % (self.libraries_root, self.version, self.version)
        if os.path.isfile(default_jar):
            return "%s.jar" % self.version
        else:
            return None

    def download_java(self, platform, component, path):

        import libraries.minecraft.java as jre_downloader
        java_manifest_url = jre_downloader.get_manifest(platform,component)

        java_manifest_path = "%s/java_manifest.json" % temp_directory
        java_manifest = None
        if web.download(java_manifest_url, java_manifest_path):
            with open(java_manifest_path, "r") as temp:
                java_manifest = json.load(temp)
            jre_downloader.download_java(java_manifest, path)

        return "%s/bin" % path

    def get_uuid(self, username=None):
        if username != None:
            req = web.get("https://api.mojang.com/users/profiles/minecraft/%s" % username)
            if req:
                return json.loads(req)["id"]

        uuid_ = str(uuid.uuid1()).replace("-","")
        logging.debug("[web] generate uuid : %s" % uuid_)
        return uuid_

    def download_openjdk(self, version=None):

        filename = None
        url = None
        java_directory = None

        if version == None:
            if self.javaVersion:
                version = self.javaVersion
            else:
                version = 8

        filename = "jdk-%s_%s_%s" % (version, self.system, self.architecture)
        jdk_directory = "%s/%s" % (java_directory, filename)
        url = get_java(version, self.system, self.architecture)

        if self.system == "windows":
            filename = "%s.zip" % filename
        else:
            filename = "%s.tar.gz" % filename

        if url:
            java_archive = web.download(url, "%s/%s" % (temp_directory,filename))
        else:
            logging.error("Operating System or Architecture Unknown : (%s, %s)" % (self.system, self.architecture))
            exit()
        
        if os.path.isdir(jdk_directory) == False:
            if java_archive == False:
                print("java_archive : %s" % java_archive)
                exit()
            else:
                extracted_directory = _file.extract_archive(java_archive, java_directory)
                _file.mv("%s/%s" % (java_directory, extracted_directory[0]), jdk_directory)
                
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
    
    def set_username(self, username):
        logging.debug("setting username : %s" % username)
        self.username = username

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

    def set_uuid(self, username=None, uuid=None):
        if username:
            self.uuid = self.get_uuid(username)
        else:
            self.uuid = uuid
    
    def get_minecraft_arguments(self, arguments):

        arguments_var = {}
        arguments_var["${auth_player_name}"] = self.username
        arguments_var["${version_name}"] = self.version
        arguments_var["${game_directory}"] = "\".\""
        arguments_var["${assets_root}"] = arguments_var["${game_assets}"] = "assets"
        arguments_var["${assets_index_name}"] = self.version_parser.get_assetIndex()
        arguments_var["${auth_uuid}"] = self.uuid
        arguments_var["${auth_access_token}"] = arguments_var["${auth_session}"] = self.access_token
        arguments_var["${user_type}"] = "mojang"
        arguments_var["${version_type}"] = self.version_parser.get_versionType()
        arguments_var["${user_properties}"] = "{}"

        for index in range(len(arguments)):
            for argument in arguments_var:
                if argument in arguments[index]:
                    arguments[index] = arguments_var[argument]
        
        return arguments
    
    def get_default_java_arguments(self):
        default_java_arg = []
        default_java_arg.append("-Xmx2G") 
        default_java_arg.append("-XX:+UnlockExperimentalVMOptions") 
        default_java_arg.append("-XX:+UseG1GC -XX:G1NewSizePercent=20") 
        default_java_arg.append("-XX:G1ReservePercent=20")
        default_java_arg.append("-XX:MaxGCPauseMillis=50")
        default_java_arg.append("-XX:G1HeapRegionSize=32M")
        return default_java_arg
    
    def get_java_arguments(self, arguments):
        values = []
        
        arguments_var = {}
        arguments_var["${launcher_name}"] = "gally_launcher"
        arguments_var["${launcher_version}"] = "unknown"
        arguments_var["${version_name}"] = self.version
        arguments_var["${library_directory}"] = "%s" % self.libraries_root
        arguments_var["${classpath_separator}"] = self.classpath_separator
        
        if self.system == "windows":
            arguments_var["${classpath}"] = "\"%classpath%\""
        elif self.system == "linux":
            arguments_var["${classpath}"] = "\"$classpath\""

        if self.binary_root:
            arguments_var["${natives_directory}"] = self.binary_root
        
        if arguments == []:
            values.append("-Djava.library.path=%s" % arguments_var["${natives_directory}"])
            values.append("-cp")
            values.append(arguments_var["${classpath}"])
            return values

        for index in range(len(arguments)):
            value = arguments[index]
            for argument in arguments_var:
                if argument in arguments[index]:
                    value = value.replace(argument, arguments_var[argument])
            values.append(value)
        
        return values


    def start(self, assets=True, java=None, console=False, java_argument=None, game_directory=None, debug=False, dont_start=False, ip=None, port = None):
        if game_directory == None:
            game_directory = self.profile_gamedir

        if self.uuid == None:
            self.set_uuid(username=self.username)

        logging.info("downloading java")
        platform = None
        if self.architecture == "i386" or self.architecture == "x86" or self.architecture == "x64":
            platform = "%s-%s" % (self.system, self.architecture)
        else:
            platform = self.system
        
        component = self.version_parser.get_java_component()
        java_path = "%s/runtime/%s/%s/%s" % (self.minecraft_root, component, platform, component)
        java_path = self.download_java(platform, component, java_path)
        
        logging.info("downloading client")
        download_client(self.version_parser.json_loaded,"%s/%s" % (self.versions_root,self.version), self.version)
        main_jar = "%s/%s/%s.jar" % (self.versions_root, self.version, self.version)

        logging.info("downloading library")
        download_libraries(self.version_parser.json_loaded["libraries"], self.libraries_root, self.system)

        logging.info("downloading binary")
        lwjgl_version = self.version_parser.get_lastest_lwjgl_version()
        self.binary_root = "%s/%s" % (self.binary_root, lwjgl_version)
        download_binary(lwjgl_version, self.binary_root, self.system)

        if assets == True:
            logging.info("downloading assets")
            download_assets(self.version_parser.json_loaded, self.assets_root)

        if java == None:
            if console:
                java = "java"
            else:
                if self.system == "windows":
                    java = "javaw"
                else:
                    java = "java"

            java = "%s/%s" % (java_path, java)
            
        JAVA_ARGUMENT = []
        
        classpath = None

        # Setting up classpath
        if os.path.isfile("debug/classpath"):
            with open("debug/classpath",'r') as classpath_file:
                classpath = classpath_file.read()
        else:
            classpath = self.version_parser.classpath()
            for index in range(len(classpath)):
                classpath[index] = "%s/%s" % (self.libraries_root, classpath[index])

            if not main_jar:
                main_jar = "%s/%s/%s" % (self.minecraft_root, self.version, self.version_parser.get_jar())
            if main_jar:
                classpath.append("%s" % (main_jar))
            classpath = self.classpath_separator.join(classpath)
        os.environ["classpath"] = classpath
        

        # Setting up mainclass
        if os.path.isfile("debug/mainclass"):
            with open("debug/mainclass", "r") as mainclass_file:
                mainclass = mainclass_file.read()
        else:
            mainclass = self.version_parser.get_mainclass()

        # Game arguments
        if os.path.isfile("debug/game_argument"):
            with open("debug/game_argument", "r") as game_argument_file:
                game_argument = [game_argument_file.read()]
        else:
            game_argument = self.version_parser.minecraft_arguments()
            game_argument = self.get_minecraft_arguments(game_argument)

        if ip and port:
            game_argument.append("--server %s" % ip)
            game_argument.append("--port %s" % port)
        
        # Java argumennts
        default_arguments = []
        if java_argument:
            default_arguments = java_argument
        elif self.opt_java_arg:
            default_arguments = self.opt_java_arg
        else:
            default_arguments = self.get_default_java_arguments()

        if type(default_arguments) == str:
            default_arguments = [default_arguments]

        if os.path.isfile("debug/java_argument"):
            with open("debug/java_argument", "r") as java_argument_file:
                java_argument = [java_argument_file.read()]
        else:
            java_argument = self.version_parser.java_arguments()
            java_argument = default_arguments + self.get_java_arguments(java_argument)
            

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