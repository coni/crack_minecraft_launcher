import json
import os
import libraries.utils.string as string
import libraries.utils.system as system
import re
import logging

class version:
    def __init__(self, version=None, minecraft_root=".", versions_root="versions", osName=None,):
        
        self.system = None
        if osName == None:
            self.system = system.get_os()
        else:
            self.system = osName

                
        if self.system == "linux":
            try:
                self.temp_directory = os.environ["TMPDIR"]
            except:
                self.temp_directory = "/tmp"
            self.delim = "/"
        elif system == "windows":
            self.temp_directory = os.environ["temp"]
            self.delim = "\\"

        self.minecraft_root = minecraft_root
        self.versions_root = versions_root
        
        self.version = version

        if self.system == "windows":
            self.classpath_separator = ";"
        elif self.system == "linux":
            self.classpath_separator = ":"
        
        if version:
            self.load_version(version)
    
    def inherit_from(self):
        if "inheritsFrom" in self.json_loaded:
            return self.json_loaded["inheritsFrom"]
        return ""
        
    def load_version(self, version=None):
        logging.debug("loading %s" % version)
        if version:
            self.version = version
            json_file = open("%s/%s/%s.json" % (self.versions_root, self.version, self.version),"r")
        else:
            logging.error("%s don't exist" % version)
            return None

        self.json_loaded = json.load(json_file)
        
        self.version_type = self.get_versionType()
        self.lastest_lwjgl_version = self.get_lastest_lwjgl_version()
        self.assetIndex = self.get_assetIndex()
        self.binary_path = None
        
        self.javaVersion = self.get_java_version()
    
    def get_java_version(self):
        if "javaVersion" in self.json_loaded:
            javaVersion = self.json_loaded["javaVersion"]["majorVersion"]
        else:
            javaVersion = 8
        return javaVersion

    def get_java_component(self):
        if "javaVersion" in self.json_loaded:
            javaVersion = self.json_loaded["javaVersion"]["component"]
        else:
            javaVersion = "jre-legacy"
        return javaVersion

    def get_lastest_lwjgl_version(self):

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
        
    def classpath(self):
        
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

        classpath = []

        for i in libraries:
            librarie_name = i["name"].split(":")
            filename = "%s.jar" % "-".join(librarie_name[-2:])
            path = "%s/%s" % ("/".join(librarie_name[0].split(".")), "/".join(librarie_name[1:]))
            fullpath = "%s/%s" % (path, filename)
            classpath.append(fullpath)
        
        return classpath

    def get_mainclass(self):
        logging.debug("getting mainclass")

        if self.get_versionType() != "snapshot":
            version = self.version

            reggex = re.search(r"1\.(?P<majorVersion>[0-9]*)(\.(?P<minorVersion>[0-9]*))?",version)
            version_major = int(reggex.group("majorVersion"))
            if len(version.split(".")) > 2:
                version_minor = int(reggex.group("minorVersion"))
            else:
                version_minor = 0

        jar_path = "%s/%s/%s.jar" % (self.versions_root, self.version, self.version)
        manifest_mainclass = None
        manifest_path = "META-INF/MANIFEST.MF"
        
        try:
            if system.extract_archive(jar_path, self.temp_directory, to_extract=manifest_path):
                manifest_text = system.get_text("%s/%s" % (self.temp_directory, manifest_path))
                manifest_mainclass = string.find_string(manifest_text, "Main-Class")
                if manifest_mainclass:
                    manifest_mainclass = manifest_mainclass.split("Main-Class: ")[1]
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

    def get_assetIndex(self):
        assetIndex = None
            
        if "assetIndex" in self.json_loaded:
            if "id" in self.json_loaded["assetIndex"]:
                assetIndex = self.json_loaded["assetIndex"]["id"]

        return assetIndex

    def get_versionType(self):
        assetIndex = None
        if "type" in self.json_loaded:
            assetIndex = self.json_loaded["type"]

        return assetIndex

    def minecraft_arguments(self):
        minecraft_arguments = []
        json_arguments = []

        if "minecraftArguments" in self.json_loaded:
            json_arguments = self.json_loaded["minecraftArguments"].split(" ")
        elif "arguments" in self.json_loaded:
            json_arguments = self.json_loaded["arguments"]["game"]

        for i in range(len(json_arguments)):
            if type(json_arguments[i]) == str:
                if "--" == json_arguments[i][:2]:
                    if json_arguments[i] not in minecraft_arguments:
                        if type(json_arguments[i]) == list:
                            minecraft_arguments += json_arguments[i]
                        elif type(json_arguments[i]) == str:
                            minecraft_arguments.append(json_arguments[i])
                        
                        if type(json_arguments[i+1]) == list:
                            minecraft_arguments += json_arguments[i+1]
                        elif type(json_arguments[i+1]) == str:
                            minecraft_arguments.append(json_arguments[i+1])
        return minecraft_arguments
    
    def java_arguments(self, system=None, architecture=None):

        arguments = []
        new_arguments = []
        if "arguments" in self.json_loaded:
            if "jvm" in self.json_loaded["arguments"]:
                arguments = self.json_loaded["arguments"]["jvm"]

        for index in range(len(arguments)):
            if type(arguments[index]) == dict:
                if system or architecture:
                    if "name" in arguments[index]["rules"][0]["os"]:
                        if arguments[index]["rules"][0]["os"]["name"] == system:
                            if type(arguments[index]["value"]) == str:
                                new_arguments.append(arguments[index]["value"])
                            elif type(arguments[index]["value"]) == list:
                                new_arguments += arguments[index]["value"]

            elif type(arguments[index]) == str:
                new_arguments.append(arguments[index])
            elif type(arguments[index]) == list:
                new_arguments += arguments[index]

        return new_arguments