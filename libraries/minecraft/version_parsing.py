import json
import os
import libraries.utils.string as string
import libraries.utils.web as web
import libraries.utils._file as _file
import re
import logging

class parse_minecraft_version:

    def __init__(self, system=None,version=None, minecraft_root=".", libraries_root="libraries", binary_root="bin", assets_root="assets", versions_root="versions", username=None, inherit=False):
        
        self.system = None
        if system == None:
            self.system = _file.get_os()
        else:
            if system == "windows" or system == "linux":
                self.system = system
            else:
                self.system = _file.get_os()

        self.minecraft_root = minecraft_root

        self.assets_root = assets_root
        self.versions_root = versions_root
        self.libraries_root = libraries_root
        self.binary_root = binary_root
        self.uuid_of = None
        self.uuid = None
        
        self.inherit = inherit
        self.version = version
        self.username = username

        if self.system == "windows":
            self.classpath_separator = ";"
        elif self.system == "linux":
            self.classpath_separator = ":"
        
        if version:
            self.load_version(version)


    def load_version(self, version=None):
        logging.debug("loading %s" % version)
        if version:
            self.version = version
            json_file = open("%s/%s/%s/%s.json" % (self.minecraft_root, self.versions_root, self.version, self.version),"r")
        else:
            logging.error("%s don't exist" % version)
            return None

        self.json_loaded = json.load(json_file)
        self.lastest_lwjgl_version = None
    
        if "inheritsFrom" in self.json_loaded:
            self.inheritsFrom = self.json_loaded["inheritsFrom"]
            self.inheritsFrom_parse = parse_minecraft_version(version=self.inheritsFrom,minecraft_root=self.minecraft_root, libraries_root=self.libraries_root, binary_root=self.binary_root,assets_root=self.assets_root,versions_root=self.versions_root, username=self.username, inherit=True)
        else:
            self.inheritsFrom = False
        
        self.download_client()
        self.version_type = self.get_versionType()
        self.lastest_lwjgl_version = self.get_lastest_lwjgl_version()
        self.assetIndex = self.get_assetIndex()
        self.binary_path = None
        self.classpath = self.download_libraries(download=False)
        
        if "javaVersion" in self.json_loaded:
            self.javaVersion = self.json_loaded["javaVersion"]["majorVersion"]
        else:
            if self.inheritsFrom:
                self.javaVersion = self.inheritsFrom_parse.javaVersion
            else:
                self.javaVersion = 8
    
    def get_java_version(self):
        if "javaVersion" in self.json_loaded:
            javaVersion = self.json_loaded["javaVersion"]["majorVersion"]
        else:
            if self.inheritsFrom:
                javaVersion = self.inheritsFrom_parse.get_java_version()
            else:
                javaVersion = 8
        return javaVersion

    def get_java_component(self):
        if "javaVersion" in self.json_loaded:
            javaVersion = self.json_loaded["javaVersion"]["component"]
        else:
            if self.inheritsFrom:
                javaVersion = self.inheritsFrom_parse.get_java_component()
            else:
                javaVersion = "jre-legacy"
        return javaVersion

    def get_lastest_lwjgl_version(self):
        
        if self.inheritsFrom:
            lastest_inherits = self.inheritsFrom_parse.lastest_lwjgl_version

        lwjgl_version = []
        if "libraries" in self.json_loaded:
            for i in self.json_loaded["libraries"]:
                if "lwjgl" in i["name"] and i["name"].split(":")[-1] not in lwjgl_version:
                    lwjgl_version.append(i["name"].split(":")[-1])

        sorted(lwjgl_version)
        if lwjgl_version:
            reggex = re.search(r"(?P<version>[0-9]\.[0-9]\.[0-9])(-(?P<type>.+)-(?P<build>.+)\\)?",lwjgl_version[-1])
            logging.debug("getting the lastest version of lwjgl : %s " % reggex.group("version"))
            return reggex.group("version")
        else:
            logging.debug("getting the lastest version of lwjgl : %s " % lastest_inherits)
            return lastest_inherits

    def set_uuid(self, username=None, uuid=None):
        if username:
            self.uuid_of = username
        else:
            self.uuid = uuid

    def download_server(self, path="."):
        exist = False
        if "downloads" in self.json_loaded:
            if "server" in self.json_loaded["downloads"]:
                url = self.json_loaded["downloads"]["server"]["url"]
                exist = web.download(url, "%s/server.jar" % path)
        return exist
        
    def get_jar(self):

        if self.minecraft_root == ".":
            minecraft_root = os.getcwd()
        else:
            if self.minecraft_root[:3] == "C:\\" or self.minecraft_root[0] == "/":
                minecraft_root = self.minecraft_root
            else:
                minecraft_root = "%s/%s" % (os.getcwd(), self.minecraft_root)

        default_jar = "%s/%s/%s.jar" % (self.versions_root, self.version, self.version)
        default_jar_fullpath = "%s/%s/%s/%s.jar" % (minecraft_root, self.versions_root, self.version, self.version)

        logging.debug("getting jar path %s" % default_jar)
        if os.path.isfile(default_jar_fullpath):
            return default_jar

        if self.inheritsFrom:
            jar = self.inheritsFrom_parse.get_jar()
            return jar
        
    def download_libraries(self, download=True):
        
        def get_index(liste, element):
            for i in range(len(liste)):
                if liste[i] == element:
                    return i
            return None

        def extract_double(liste):
            libraries_name = []
            libraries = []
            for i in liste:
                if i["name"] not in libraries_name:
                    libraries_name.append(i["name"])
                    libraries.append(i)
                else:
                    index_old = get_index(libraries_name, i["name"])
                    if len(i) > len(libraries[index_old]):
                        libraries[index_old] = i
            return libraries

        def use_last_version(liste):
            libraries_name = []
            libraries_version = []
            libraries = []
            for i in range(len(liste)):
                name_splitted = liste[i]["name"].split(":")
                name = name_splitted[:-1]
                version = name_splitted[-1]

                if name not in libraries_name:
                    libraries_name.append(name)
                    libraries_version.append(version)
                    libraries.append(liste[i])
                else:
                    index_old = get_index(libraries_name, name)
                    if version > libraries_version[index_old]:
                        libraries[index_old] = liste[i]
                        libraries_version[index_old] = version
                        libraries_name[index_old] = name
            return libraries

        libraries = []

        for i in self.json_loaded["libraries"]:
            if "name" in i:
                libraries.append(i)

        libraries = extract_double(libraries)
        libraries = use_last_version(libraries)

        to_download = []
        classpath = []
        native = "natives-%s" % self.system

        for i in libraries:
            url = None
            librarie_name = i["name"].split(":")
            
            filename = "%s.jar" % "-".join(librarie_name[-2:])
            path = "%s/%s" % ("/".join(librarie_name[0].split(".")), "/".join(librarie_name[1:]))
            fullpath = "%s/%s" % (path, filename)
            classpath.append("./%s/%s" % (self.libraries_root, fullpath))

            if type(libraries) == dict:
                if "url" in i:
                    url = "%s/%s/%s" % (i["url"], path, filename)
                elif "downloads" in i:
                    url = i["downloads"]["artifact"]["url"]

                if url:
                    to_download.append((url,fullpath))

                if "natives" in i:
                    if native in i["downloads"]["classifiers"]:
                        # not sure if it's important
                        # if "sources" in i["downloads"]["classifiers"]:
                        #     path = i["downloads"]["classifiers"]["sources"]["path"]
                        #     url = i["downloads"]["classifiers"]["sources"]["url"]
                        #     to_download.append(path,url)
                        #     classpath.append("./%s/%s" % (self.libraries_root, path))
                        url = i["downloads"]["classifiers"][native]["url"]
                        path = i["downloads"]["classifiers"][native]["path"]
                        to_download.append((path,url))
                        classpath.append("./%s/%s" % (self.libraries_root, path))

            elif type(libraries) == list:
                if "url" in i:
                    url = "%s/%s" % (i["url"], fullpath)
                    path = fullpath
                else:
                    if "downloads" in i:
                        if "artifact" in i["downloads"]:
                            url = i["downloads"]["artifact"]["url"]
                            path = i["downloads"]["artifact"]["path"]
                        elif "classifiers" in i["downloads"]:
                            if native in i["downloads"]["classifiers"]:
                                url = i["downloads"]["classifiers"][native]["url"]
                                path = i["downloads"]["classifiers"][native]["path"]
                if url:
                    to_download.append((url, path))
                    
        libraries_path = "%s/%s" % (self.minecraft_root, self.libraries_root)
        if download:
            logging.debug("prepare the downloading of libraries")
            for url, filename in to_download:
                web.download(url, "%s/%s" % (libraries_path,filename))

        inherited_classpath = None
        if "inheritsFrom" in self.json_loaded:
            inherits = parse_minecraft_version(version=self.inheritsFrom,minecraft_root=self.minecraft_root, libraries_root=self.libraries_root, binary_root=self.binary_root,assets_root=self.assets_root,versions_root=self.versions_root, username=self.username, inherit=True)
            inherited_classpath = inherits.download_libraries()

        main_jar = self.get_jar()
        if main_jar:
            classpath.append("./%s" % main_jar)

        if inherited_classpath:
            self.classpath = "%s%s%s" % (self.classpath_separator.join(classpath), self.classpath_separator, inherited_classpath)
        else:
            self.classpath = self.classpath_separator.join(classpath)

        return self.classpath

    def download_binary(self):
        if self.minecraft_root == ".":
            minecraft_root = os.getcwd()
        else:
            if self.minecraft_root[:3] == "C:\\" or self.minecraft_root[0] == "/":
                minecraft_root = self.minecraft_root
            else:
                minecraft_root = "%s/%s" % (os.getcwd(), self.minecraft_root)

        logging.debug("prepare the downloading of binaries")
        binary_url = []

        if self.lastest_lwjgl_version.split(".")[0] == "3":
            
            if os.path.isdir("%s/%s" % (self.binary_root, self.lastest_lwjgl_version)) == False:
                base_url_x64 = "https://build.lwjgl.org/release/%s/%s/x64" % (self.lastest_lwjgl_version, self.system)
                base_url_x86 = "https://build.lwjgl.org/release/%s/windows/x86" % self.lastest_lwjgl_version

                if self.system == "windows":

                    binary_url.append("%s/%s" % (base_url_x64, "glfw.dll"))
                    binary_url.append("%s/%s" % (base_url_x64, "jemalloc.dll"))
                    binary_url.append("%s/%s" % (base_url_x64, "lwjgl.dll"))
                    binary_url.append("%s/%s" % (base_url_x64, "lwjgl_opengl.dll"))
                    binary_url.append("%s/%s" % (base_url_x64, "lwjgl_stb.dll"))
                    binary_url.append("%s/%s" % (base_url_x64, "OpenAL.dll"))
                    binary_url.append("%s/%s" % (base_url_x86, "glfw32.dll"))
                    binary_url.append("%s/%s" % (base_url_x86, "jemalloc32.dll"))
                    binary_url.append("%s/%s" % (base_url_x86, "lwjgl_opengl32.dll"))
                    binary_url.append("%s/%s" % (base_url_x86, "lwjgl_stb32.dll"))
                    binary_url.append("%s/%s" % (base_url_x86, "lwjgl32.dll"))
                    binary_url.append("%s/%s" % (base_url_x86, "OpenAL32.dll"))

                elif self.system == "linux":
                    # binary_url.append("%s/%s" % (base_url_x64, "libfliteWrapper.so"))
                    binary_url.append("%s/%s" % (base_url_x64, "libglfw.so"))
                    binary_url.append("%s/%s" % (base_url_x64, "libglfw_wayland.so"))
                    binary_url.append("%s/%s" % (base_url_x64, "libjemalloc.so"))
                    binary_url.append("%s/%s" % (base_url_x64, "liblwjgl.so"))
                    binary_url.append("%s/%s" % (base_url_x64, "liblwjgl_opengl.so"))
                    binary_url.append("%s/%s" % (base_url_x64, "liblwjgl_stb.so"))
                    binary_url.append("%s/%s" % (base_url_x64, "libopenal.so"))
                    binary_url.append("%s/%s" % (base_url_x64, "liblwjgl_tinyfd.so"))
            else:
                 return "%s/%s/%s/" % (minecraft_root, self.binary_root, self.lastest_lwjgl_version)

        elif self.lastest_lwjgl_version.split(".")[0] == "2":
            if os.path.isdir("%s/%s/%s" % (minecraft_root, self.binary_root, self.lastest_lwjgl_version)) == False:
                if self.lastest_lwjgl_version == "2.9.4":
                    zip_url = "http://ci.newdawnsoftware.com/job/LWJGL-git-dist/lastBuild/artifact/dist/lwjgl-2.9.4.zip"
                else:
                    zip_url = "https://versaweb.dl.sourceforge.net/project/java-game-lib/Official Releases/LWJGL %s/lwjgl-%s.zip" % (self.lastest_lwjgl_version, self.lastest_lwjgl_version)
            else:
                return "%s/%s/%s/native/%s/" % (minecraft_root, self.binary_root, self.lastest_lwjgl_version, self.system)
        
        temp_path = "%s/.temp" % self.minecraft_root
        zip_filename = "%s/%s.zip" % (temp_path, self.lastest_lwjgl_version)

        if binary_url:
            binary_full_path = "%s/%s/" % (self.binary_root, self.lastest_lwjgl_version)
            for url in binary_url:
                binary_filename = url.split("/")[-1]
                binary_file = "%s/%s/%s" % (self.minecraft_root, binary_full_path, binary_filename)
                web.download(url, binary_file)

        elif zip_url:

            web.download(zip_url, zip_filename)
            if os.path.isfile(zip_filename):
                list_folder_extracted = _file.extract_archive(zip_filename, "%s/%s" % (self.minecraft_root, self.binary_root))
                print(list_folder_extracted)
                # exit()
                for folder in list_folder_extracted:
                    if folder == "lwjgl-%s/" % self.lastest_lwjgl_version:
                        folder = "%s/%s" % (self.binary_root, self.lastest_lwjgl_version)
                        _file.mv("%s/%s/lwjgl-%s" % (self.minecraft_root, self.binary_root, self.lastest_lwjgl_version), "%s/%s" % (self.minecraft_root, folder))

                        binary_full_path = "%s/native/%s/" % (folder, self.system)

        _file.rm_rf(temp_path)

        self.binary_path = binary_full_path

        return binary_full_path

    def get_mainclass(self):
        logging.debug("getting mainclass")

        if self.get_versionType() != "snapshot":
            if self.inheritsFrom:
                version = self.inheritsFrom
            else:
                version = self.version

            # hihi
            reggex = re.search(r"1\.(?P<majorVersion>[0-9]*)(\.(?P<minorVersion>[0-9]*))?",version)
            version_major = int(reggex.group("majorVersion"))
            if len(version.split(".")) > 2:
                version_minor = int(reggex.group("minorVersion"))
            else:
                version_minor = 0

        if self.inheritsFrom:
            mainclass_inherits = self.inheritsFrom_parse.get_mainclass()
        

        jar_path = "%s/%s" % (self.minecraft_root, self.get_jar())
        manifest_mainclass = None
        manifest_path = "META-INF/MANIFEST.MF"
        try:
            if _file.extract_archive(jar_path, ".temp/", to_extract=manifest_path):
                manifest_text = _file.get_text(".temp/%s" % manifest_path)
                manifest_mainclass = string.find_string(manifest_text, "Main-Class")
                if manifest_mainclass:
                    manifest_mainclass = manifest_mainclass.split("Main-Class: ")[1]
                _file.rm_rf("./temp")
        except:
            pass
    
        if "mainClass" in self.json_loaded:
            if self.get_versionType() != "snapshot":
                if version_major <= 2 and version_minor < 5:
                    return "net.minecraft.client.Minecraft"
                elif version_major == 2 and version_minor == 5 or version_major > 2 and version_major < 6:
                    return manifest_mainclass
            mainclass = self.json_loaded["mainClass"]
            return mainclass
        else:
            return mainclass_inherits


    def get_assetIndex(self):
        assetIndex = False

        if self.inheritsFrom:
            assetIndex = self.inheritsFrom_parse.get_assetIndex()
            
        if "assetIndex" in self.json_loaded:
            if "id" in self.json_loaded["assetIndex"]:
                assetIndex = self.json_loaded["assetIndex"]["id"]
        logging.debug("get the asset index : %s" %assetIndex)
        return assetIndex

    def get_versionType(self):

        assetIndex = False
        if self.inheritsFrom:
            assetIndex = self.inheritsFrom_parse.get_versionType()

        if "type" in self.json_loaded:
            assetIndex = self.json_loaded["type"]
        logging.debug("get the version type : %s" % assetIndex)
        return assetIndex

    def download_client(self):
        logging.debug("downloading client for %s" % self.version)
        client_path = "%s/%s/%s" % (self.minecraft_root, self.versions_root, self.version)

        if os.path.isfile("%s/%s.jar" % (client_path, self.version)) == False:
            if "downloads" in self.json_loaded:
                url = self.json_loaded["downloads"]["client"]["url"]
                web.download(url, "%s/%s.jar" % (client_path, self.version))
        else:
            return True

    def download_assets(self):
        logging.debug("download assets..")

        if self.inheritsFrom:
            self.inheritsFrom_parse.download_assets()

        to_download = []
        if "assetIndex" not in self.json_loaded:
            return False

        asset_index_url = self.json_loaded["assetIndex"]["url"]
        asset_index_filename = self.json_loaded["assetIndex"]["id"]
        asset_index_fullpath = "%s/%s/indexes/%s.json" % (self.minecraft_root, self.assets_root, asset_index_filename)

        if "logging" in self.json_loaded:
            config_filename = self.json_loaded["logging"]["client"]["file"]["id"]
            config_url = self.json_loaded["logging"]["client"]["file"]["url"]
            config_fullpath = "%s/%s/log_configs/%s" % (self.minecraft_root, self.assets_root, config_filename)
            to_download.append((config_url, config_fullpath))

        to_download.append((asset_index_url, asset_index_fullpath))

        for asset_indexes in to_download:
            web.download(asset_indexes[0], asset_indexes[1])

        asset_index_file = open(asset_index_fullpath,'r')
        asset_index_json = json.load(asset_index_file)

        for i in asset_index_json["objects"]:
            asset_hash = asset_index_json["objects"][i]["hash"]
            asset_folder = asset_hash[:2]
            web.download("https://resources.download.minecraft.net/%s/%s" % (asset_folder, asset_hash), "%s/%s/objects/%s/%s" % (self.minecraft_root, self.assets_root, asset_folder, asset_hash))

    def get_minecraft_arguments(self, access_token=None, game_directory=None):

        if game_directory == None:
            game_directory = "."

        if access_token == None:
            access_token = "??????????"
        
        inherits_arguments = None
        if self.inheritsFrom:
            inherits_arguments = self.inheritsFrom_parse.get_minecraft_arguments()
        
        if self.uuid:
            uuid = self.uuid
        else:
            if self.uuid_of:
                username = self.uuid_of
            else:
                username = self.username
            uuid = web.get_uuid(username=username)

        minecraft_arguments = []

        arguments_var = {}
        arguments_var["${auth_player_name}"] = self.username
        arguments_var["${version_name}"] = self.version
        arguments_var["${game_directory}"] = "\"%s\"" % game_directory
        arguments_var["${assets_root}"] = arguments_var["${game_assets}"] = self.assets_root
        arguments_var["${assets_index_name}"] = self.assetIndex
        arguments_var["${auth_uuid}"] = uuid
        arguments_var["${auth_access_token}"] = arguments_var["${auth_session}"] = access_token
        arguments_var["${user_type}"] = "mojang"
        arguments_var["${version_type}"] = self.version_type
        arguments_var["${user_properties}"] = "{}"

        json_arguments = []
        if "minecraftArguments" in self.json_loaded:
            json_arguments = self.json_loaded["minecraftArguments"].split(" ")
        elif "arguments" in self.json_loaded:
            json_arguments = self.json_loaded["arguments"]["game"]

        for argument in json_arguments:
            if type(argument) == str:
                if argument in arguments_var:
                    minecraft_arguments.append(arguments_var[argument])
                else:
                    minecraft_arguments.append(argument)

        if self.inheritsFrom:
            for i in range(len(inherits_arguments)):
                if inherits_arguments[i]:
                    if "--" == inherits_arguments[i][:2]:
                        if inherits_arguments[i] not in minecraft_arguments:
                            if type(inherits_arguments[i]) == list:
                                minecraft_arguments += inherits_arguments[i]
                            elif type(inherits_arguments[i]) == str:
                                minecraft_arguments.append(inherits_arguments[i])
                            
                            if type(inherits_arguments[i+1]) == list:
                                minecraft_arguments += inherits_arguments[i+1]
                            elif type(inherits_arguments[i+1]) == str:
                                minecraft_arguments.append(inherits_arguments[i+1])
        
        logging.debug("getting minecraft arguments")
        return minecraft_arguments

    def get_java_arguments(self, classpath=None):
        
        if classpath == None:
            classpath = self.classpath

        values_temp = []
        values = []

        inherits_arguments = None
        if self.inheritsFrom:
            version_name = self.inheritsFrom
            inherits_arguments = self.inheritsFrom_parse.get_java_arguments()
        else:
            version_name = self.version

        
        arguments_var = {}
        arguments_var["${launcher_name}"] = "coni_python"
        arguments_var["${launcher_version}"] = "unknown"
        arguments_var["${version_name}"] = "1.17.1"
        arguments_var["${classpath}"] = classpath
        
        arguments_var["${library_directory}"] = "./%s" % self.libraries_root
        arguments_var["${classpath_separator}"] = self.classpath_separator
        
        os.environ["classpath"] = arguments_var["${classpath}"]
        if self.system == "windows":
            arguments_var["${classpath}"] = "\"%classpath%\""
        elif self.system == "linux":
            arguments_var["${classpath}"] = "\"$classpath\""


        if self.binary_path:
            arguments_var["${natives_directory}"] = self.binary_path
        else:
            arguments_var["${natives_directory}"] = self.download_binary()
        
        if "arguments" in self.json_loaded:
            if "jvm" not in self.json_loaded["arguments"]:
                if inherits_arguments:
                    return inherits_arguments
                else:
                    return False
        else:
            values.append("-Djava.library.path=%s" % arguments_var["${natives_directory}"])
            values.append("-cp")
            values.append(arguments_var["${classpath}"])
            return values

        for i in self.json_loaded["arguments"]["jvm"]:
            if type(i) == dict:
                if "name" in i["rules"][0]["os"]:
                    if i["rules"][0]["os"]["name"] == "windows":
                        values_temp.append(i["value"])
            else:
                values_temp.append(i.replace(" ",""))
            
        for value in values_temp:
            if type(value) == str:
                for argument in arguments_var:
                    if argument in value:
                        value = value.replace(argument, arguments_var[argument])
                values.append(value)
            elif type(value) == list:
                for i in value:
                    for argument in arguments_var:
                        if argument in i:
                            i = i.replace(argument, arguments_var[argument])
                    values.append(i)

        to_remove = []
        for i in range(len(values)-1):
            if " " in values[i]:
                to_remove.append(i)
        
        for i in to_remove:
            values.pop(i)


        if inherits_arguments:
            values += inherits_arguments
        logging.debug("getting java arguments")
        logging.debug("classpath : %s" % os.environ["classpath"])
        return values

    def get_default_java_arguments(self):
        default_java_arg = []

        default_java_arg.append("-Xmx2G") 
        default_java_arg.append("-XX:+UnlockExperimentalVMOptions") 
        default_java_arg.append("-XX:+UseG1GC -XX:G1NewSizePercent=20") 
        default_java_arg.append("-XX:G1ReservePercent=20")
        default_java_arg.append("-XX:MaxGCPauseMillis=50")
        default_java_arg.append("-XX:G1HeapRegionSize=32M")

        logging.debug("getting default java arguments : %s" % ' '.join(default_java_arg))

        return default_java_arg
    
    def set_username(self, username):
        logging.debug("setting username : %s" % username)
        self.username = username
        return self.username