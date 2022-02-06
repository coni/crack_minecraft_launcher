import os
import libraries.utils.system as system
import libraries.utils.request as request

from libraries.minecraft.version import version
from libraries.minecraft.profile import profile
from libraries.minecraft.versionManifest import versionManifest

from libraries.download.libraries import download_libraries
from libraries.download.client import download_client
from libraries.download.assets import download_assets
from libraries.download.lwjgl import download_binary
from libraries.download.openjdk import get_java

import logging
import json
import sys
import getpass
import re
import base64

osName = system.get_os()
if osName == "linux":
    try:
        temp_directory = os.environ["TMPDIR"]
    except:
        temp_directory = "/tmp/gally_launcher"
elif osName == "windows":
    temp_directory = os.environ["temp"] + "/gally_launcher"
system.mkdir_recurcive(temp_directory)

class obj:
    def __init__(self):
        pass

class gally_launcher:
    def __init__(self, minecraft_root=None):
        
        self.system = osName
        self.architecture = system.get_architechture()
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
        self.accessToken = "None"
        self.localid = None

        if os.path.isdir(self.minecraft_root) == False:
            system.mkdir_recurcive(self.minecraft_root)
        
        self.version_parser = version(osName=self.system, minecraft_root=self.minecraft_root, versions_root=self.versions_root)
        self.profile = profile(minecraft_root=self.minecraft_root)
        self.downloader = versionManifest(versions_path=self.versions_root)

    def load_version(self, version):
        if self.downloader.exist(version):
            self.downloader.download_versions(version)
            self.version_parser.load_version(version=version)
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
        import libraries.download.java as jre_downloader
        java_manifest_url = jre_downloader.get_manifest(platform,component,self.minecraft_root)
        java_manifest_path = "%s/java_manifest.json" % self.minecraft_root
        java_manifest = None
        if request.download(java_manifest_url, java_manifest_path, replace=True):
            with open(java_manifest_path, "r") as temp:
                java_manifest = json.load(temp)
            jre_downloader.download_java(java_manifest, path)
        return "%s/bin" % path

    def get_uuid(self, username):
        req = request.get("https://api.mojang.com/users/profiles/minecraft/%s" % username)
        if req:
            uuid_ = json.loads(req)["id"]
        else:
            uuid_ = username
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
            java_archive = request.download(url, "%s/%s" % (temp_directory,filename))
        else:
            logging.error("Operating System or Architecture Unknown : (%s, %s)" % (self.system, self.architecture))
            exit()

        if os.path.isdir(jdk_directory) == False:
            if java_archive == False:
                print("java_archive : %s" % java_archive)
                exit()
            else:
                extracted_directory = system.extract_archive(java_archive, java_directory)
                system.mv("%s/%s" % (java_directory, extracted_directory[0]), jdk_directory)
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
        download_client(self.version_parser.json_loaded,"%s/%s" % (self.versions_root,self.version), self.version)

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
        req = request.post("https://authserver.mojang.com/authenticate", payload, headers=headers)

        if req.status == 200:
            logging.debug("authorisation granted")
            auth_response = json.loads(req.read().decode())

            self.set_username(auth_response["selectedProfile"]["name"])
            self.accessToken = auth_response["accessToken"]
            
            if self.localid == None:
                localid = request.get_uuid()

            accounts_information = {
                "accessToken" : self.accessToken,
                "minecraftProfile":auth_response["selectedProfile"],
                "localId":self.localid, "username":email,
                "remoteId":auth_response["clientToken"]
            }

            self.launcher_accounts["accounts"][self.localid] = accounts_information
            system.write_file(self.launcher_accounts_file, json.dumps(self.launcher_accounts))

        else:
            logging.error("Wrong Email or Password!")
            sys.exit()
    
    def login(self, email, password=None):
        for id in self.launcher_accounts["accounts"]:
            if self.launcher_accounts["accounts"][id]["username"] == email:
                self.localid = id
                if "accessToken" in self.launcher_accounts["accounts"][id]:
                    self.accessToken = self.launcher_accounts["accounts"][id]["accessToken"]
                    self.set_username(self.launcher_accounts["accounts"][id]["minecraftProfile"]["name"])
                    client_token = self.launcher_accounts["accounts"][id]["remoteId"]
                    if self.validate(self.accessToken, client_token) == False:
                        if self.refresh(self.accessToken, client_token) == True:
                            return True
                    else:
                        return True
                continue

        if password == None:
            password = getpass.getpass("Password to Login : ")
        self.authenticate(email, password)

    def logout(self, email, password=None):
        headers={'Content-Type':'application/json'}

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
                if request.post("https://authserver.mojang.com/invalidate", payload, headers=headers).status == 204:
                    self.launcher_accounts["accounts"].pop(id)

                    system.write_file(self.launcher_accounts_file, json.dumps(self.launcher_accounts))
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
        resp = request.post("https://authserver.mojang.com/signout", payload, headers=headers)
        if resp.status == 200 or resp.status == 204:
            return True
        else:
            return False

    def refresh(self, accessToken, clientToken):
        payload = {
            "accessToken": accessToken,
            "clientToken": clientToken
        }
        headers={'Content-Type':'application/json'}
        resp = request.post("https://authserver.mojang.com/refresh", payload, headers=headers)

        if resp.status == 200 or resp.status == 204:
            auth_response = json.loads(resp.read())
            if "accessToken" in auth_response:
                self.accessToken = auth_response["accessToken"]
                self.launcher_accounts["accounts"][self.localid]["accessToken"] =  self.accessToken
                system.write_file(self.launcher_accounts_file, json.dumps(self.launcher_accounts))
                return True
        else:
            return False

    def validate(self, accessToken, clientToken):
        payload = {
            "accessToken": accessToken,
            "clientToken": clientToken
        }

        headers = {'Content-Type':'application/json'}
        resp = request.post("https://authserver.mojang.com/validate", payload, headers=headers)

        if resp.status == 204:
            return True
        else:
            return False

    def getId(self, username):
        resp = request.get("https://api.mojang.com/users/profiles/minecraft/%s" % username)
        if resp:
            resp = json.loads(resp.decode())["id"]
        return resp

    def getPlayerSkin(self, id):
        url = "https://sessionserver.mojang.com/session/minecraft/profile/%s" % id
        resp = request.get(url)
        if resp:
            resp = json.loads(resp.decode())["properties"][0]["value"]
        else:
            return ()
        resp = json.loads(base64.b64decode(resp).decode())
        skinUrl = resp["textures"]["SKIN"]["url"]
        if "metadata" in resp["textures"]["SKIN"]:
            skinVariant = resp["textures"]["SKIN"]["metadata"]["model"]
        else:
            skinVariant = "classic"

        return skinUrl, skinVariant

    def setSkin(self, skinFile, variant, accessToken=""):
        url = "https://api.minecraftservices.com/minecraft/profile/skins"
        skinFileData = b""

        if not accessToken:
            accessToken = self.accessToken

        if os.path.isfile(skinFile):
            with open(skinFile, "rb") as _skinFile:
                skinFileData = _skinFile.read()

            headers = {
                "Authorization": "Bearer %s" % accessToken,
                "Content-Type": "multipart/form-data;boundary=xoxo"
            }
            boundary = "xoxo".encode()
            payload = []
            payload.append(b"--%b" % boundary)
            payload.append(b'Content-Disposition: form-data;name="variant"')
            payload.append(b"")
            payload.append(variant.encode())
            payload.append(b"--%b" % boundary)
            payload.append(b'Content-Disposition: form-data;name="file";filename="alex.png"')
            payload.append(b'Content-Type: image/png')
            payload.append(b"")
            payload.append(skinFileData)
            payload.append(b"--%b--" % boundary)

        else:
            headers = {
                "Authorization": "Bearer %s" % accessToken,
                "Content-Type": "application/json"
            }
            payload = {
                "variant": variant,
                "url": skinFile
            }

        if request.post(url, payload, headers=headers).status == 200:
            return True
        return False

    def set_uuid(self, username=None, uuid=None):
        if username:
            self.uuid = self.get_uuid(username)
        else:
            self.uuid = uuid

    def get_minecraft_arguments(self, arguments, version_parser):

        arguments_var = {}
        arguments_var["${auth_player_name}"] = self.username
        arguments_var["${version_name}"] = self.version
        arguments_var["${game_directory}"] = "\".\""
        arguments_var["${assets_root}"] = arguments_var["${game_assets}"] = "assets"
        arguments_var["${assets_index_name}"] = version_parser.get_assetIndex()
        arguments_var["${auth_uuid}"] = self.uuid
        arguments_var["${auth_access_token}"] = arguments_var["${auth_session}"] = self.accessToken
        arguments_var["${user_type}"] = "mojang"
        arguments_var["${version_type}"] = version_parser.get_versionType()
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
            arguments_var["${natives_directory}"] = self.binary_root + "/"
        
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
            value = value.replace(" ","")
            values.append(value)
        return values


    def start(self, assets=True, java=None, console=False, java_argument=None, game_directory=None, debug=False, dont_start=False, ip=None, port=None):
        if game_directory == None:
            game_directory = self.profile_gamedir

        classpath = []
        inheritsFrom = []
        lwjgl_version = ""
        inherit = self.version_parser.inherit_from()
        while inherit:
            inheritsFrom.append(version(osName=self.system, minecraft_root=self.minecraft_root, versions_root=self.versions_root))
            self.downloader.download_versions(inherit)
            inheritsFrom[len(inheritsFrom)-1].load_version(version=inherit)
            temp = inheritsFrom[len(inheritsFrom)-1].get_lastest_lwjgl_version()
            if temp:
                lwjgl_version = temp
            inherit = inheritsFrom[len(inheritsFrom)-1].inherit_from()
        
        

        if self.uuid == None:
            self.set_uuid(username=self.username)

        platform = None
        if self.architecture == "i386" or self.architecture == "x86" or self.architecture == "x64":
            platform = "%s-%s" % (self.system, self.architecture)
        else:
            platform = self.system
        
        download_client(self.version_parser.json_loaded,"%s/%s" % (self.versions_root,self.version), self.version)

        download_libraries(self.version_parser.json_loaded["libraries"], self.libraries_root, self.system)

        if not lwjgl_version:
            lwjgl_version = self.version_parser.get_lastest_lwjgl_version()
        self.binary_root = "%s/%s" % (self.binary_root, lwjgl_version)
        download_binary(lwjgl_version, self.binary_root, self.system)

        if assets == True:
            download_assets(self.version_parser.json_loaded, self.assets_root)
    

        # Setting up classpath
        if os.path.isfile("debug/classpath"):
            with open("debug/classpath",'r') as classpath_file:
                classpath = classpath_file.read()
        else:
            classpath += self.version_parser.classpath()
            for version_parser in inheritsFrom:
                classpath += version_parser.classpath()
                
            for index in range(len(classpath)):
                classpath[index] = "%s/%s" % (self.libraries_root, classpath[index])

            mainJar = "%s/%s/%s.jar" % (self.versions_root, self.version, self.version)
            for version_parser in inheritsFrom:
                download_client(version_parser.json_loaded,"%s/%s" % (self.versions_root, version_parser.version), version_parser.version)
                if os.path.isfile(mainJar) == False or os.path.getsize(mainJar) == 0:
                    mainJar = "%s/%s/%s.jar" % (self.versions_root, version_parser.version, version_parser.version)
                download_libraries(version_parser.json_loaded["libraries"], self.libraries_root, self.system)
                if assets == True:
                    download_assets(version_parser.json_loaded, self.assets_root)
            
            classpath.append(mainJar)
            classpath = self.classpath_separator.join(classpath)

        os.environ["classpath"] = classpath
        
        # Setting up mainclass
        if os.path.isfile("debug/mainclass"):
            with open("debug/mainclass", "r") as mainclass_file:
                mainclass = mainclass_file.read()
        else:
            mainclass = self.version_parser.get_mainclass()

        # Game arguments
        game_argument = []
        java_argument = []

        if os.path.isfile("debug/game_argument"):
            with open("debug/game_argument", "r") as game_argument_file:
                game_argument = [game_argument_file.read()]
        else:
            game_argument += self.get_minecraft_arguments(self.version_parser.minecraft_arguments(), self.version_parser)
            for version_parser in inheritsFrom:
                game_argument += self.get_minecraft_arguments(version_parser.minecraft_arguments(), version_parser)

        if ip:
            game_argument.append("--server %s" % ip)
            if port:
                game_argument.append("--port %s" % port)
            else:
                game_argument.append("--port 25565")
                
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
            java_argument += default_arguments + self.get_java_arguments(self.version_parser.java_arguments())
            for version_parser in inheritsFrom:
                java_argument += self.get_java_arguments(version_parser.java_arguments())
            
        
        if os.path.isfile("debug/java"):
            with open("debug/java", "r") as java_file:
                java = java_file.read()
        elif java == None:
            component = self.version_parser.get_java_component()
            for version_parser in inheritsFrom:
                if version_parser.javaVersion > self.javaVersion:
                    self.javaVersion = version_parser.javaVersion
                    component = version_parser.get_java_component()

            java_path = "%s/runtime/%s/%s/%s" % (self.minecraft_root, component, platform, component)
            if platform == "windows":
                platform += "-%s" % self.architecture
            self.download_java(platform, component, java_path)
            java_path += "/bin"

            if console:
                java = "java"
            else:
                if self.system == "windows":
                    java = "javaw"
                else:
                    java = "java"

            java = "%s/%s" % (java_path, java)

        JAVA_ARGUMENT = []
        arguments = [java_argument, mainclass, game_argument]
        for argument in arguments:
            if type(argument) == list:
                JAVA_ARGUMENT += argument
            elif type(argument) == str:
                JAVA_ARGUMENT.append(argument)

        JAVA_ARGUMENT = " ".join(JAVA_ARGUMENT)
        
        if debug:
            debug_path = "debug/%s" % self.version
            system.write_file("%s/classpath" % debug_path, os.environ["classpath"])
            system.write_file("%s/mainclass" % debug_path, mainclass)
            system.write_file("%s/java_argument" % debug_path, " ".join(java_argument))
            system.write_file("%s/game_argument" % debug_path, " ".join(game_argument))
            system.write_file("%s/java" % debug_path, java)
        
        system.chdir(self.minecraft_root)
        command = "\"%s\" %s" % (java, JAVA_ARGUMENT)
        if console == False:
            if self.system == "linux":
                command = "nohup \"%s\" %s >/dev/null 2>&1 " % (java, JAVA_ARGUMENT)
            elif self.system == "windows":
                command = "start \"\" \"%s\" %s" % (java, JAVA_ARGUMENT)
                

        if self.accessToken:
            logging.debug(command.replace(self.accessToken, "??????????"))
        else:
            logging.debug(command)

        if dont_start == False:
            sys.stdout.write("launching Minecraft\n")
            system.command(command, console=console)
