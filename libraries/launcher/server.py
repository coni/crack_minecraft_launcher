import os
from libraries.minecraft.version_parsing import parse_minecraft_version
from libraries.minecraft.download_versions import search_version
import libraries.utils._file as _file
import libraries.utils.web as web
import logging
import re

class minecraft_server:

    def __init__(self, version=None, server_root=None, java_arguments=None):
        
        self.system = _file.get_os()
        self.architechture = _file.get_architechture()
        self.java_arguments = None
        self.java = "java"

        self.version = version
        if server_root == None:
            if _file.get_os() == "windows":
                server_root = "%s/.minecraft" % (os.environ["appdata"])
            elif _file.get_os() == "linux":
                server_root = "~/.minecraft"

            self.server_root = "%s/server/%s" % (server_root, version)
        else:
            self.server_root = server_root
    
    def download_java(self):

        temp_directory = None
        filename = None
        url = None
        java_directory = None

        if self.system == "linux":
            try:
                temp_directory = os.environ["TMPDIR"]
            except:
                temp_directory = "/tmp"
            java_directory = "%s/.gally_launcher" % (os.environ["HOME"])
        elif self.system == "windows":
            temp_directory = os.environ["temp"]
            java_directory = "%s/gally_launcher" % (os.environ["appdata"])
        
        if self.version == None:
            version2 = "16"
        else:
            r_version = re.search(r"1\.(?P<version2>[0-9]+)(\.(?P<version3>[0-9]+))?",self.version)
            version2 = r_version.group("version2")

        if int(version2) >= 17:
        
            if self.system == "linux":
                if self.architechture == "AMD64":
                    url = "https://github.com/AdoptOpenJDK/openjdk16-binaries/releases/download/jdk-16.0.1 9/OpenJDK16U-jre_x64_linux_hotspot_16.0.1_9.tar.gz"
                
                elif self.architechture == "armv7l":
                    url = "https://github.com/AdoptOpenJDK/openjdk16-binaries/releases/download/jdk-16.0.1 9/OpenJDK16U-jre_arm_linux_hotspot_16.0.1_9.tar.gz"
                
                elif self.architechture == "aarch64":
                    url = "https://github.com/AdoptOpenJDK/openjdk16-binaries/releases/download/jdk-16.0.1 9/OpenJDK16U-jre_aarch64_linux_hotspot_16.0.1_9.tar.gz"
                    
                filename = "openjdk-16.tar.gz"
                jdk_directory = "%s/jdk-16.0.1+9-jre" % java_directory

            elif self.system == "windows":
                if self.architechture == "AMD64":
                    url = "https://github.com/AdoptOpenJDK/openjdk16-binaries/releases/download/jdk-16.0.1 9/OpenJDK16U-jre_x64_windows_hotspot_16.0.1_9.zip"
                
                elif self.architechture == "i386":
                    url = "https://github.com/AdoptOpenJDK/openjdk16-binaries/releases/download/jdk-16.0.1 9/OpenJDK16U-jre_x86-32_windows_hotspot_16.0.1_9.zip"

                filename = "openjdk-16.zip"
                jdk_directory = "%s/jdk-16.0.1+9-jre" % java_directory
            
        else:
            if self.system == "linux":
                if self.architechture == "AMD64":
                    url = "https://github.com/AdoptOpenJDK/openjdk15-binaries/releases/download/jdk-15.0.2 7/OpenJDK15U-jre_x64_linux_hotspot_15.0.2_7.tar.gz"

                elif self.architechture == "armv7l":
                    url = "https://github.com/AdoptOpenJDK/openjdk15-binaries/releases/download/jdk-15.0.2 7/OpenJDK15U-jre_arm_linux_hotspot_15.0.2_7.tar.gz"

                elif self.architechture == "aarch64":
                    url = "https://github.com/AdoptOpenJDK/openjdk15-binaries/releases/download/jdk-15.0.2 7/OpenJDK15U-jre_aarch64_linux_hotspot_15.0.2_7.tar.gz"

                filename = "openjdk-15.tar.gz"
                jdk_directory = "%s/jdk-15.0.2+7-jre" % java_directory

            elif self.system == "windows":
                if self.architechture == "AMD64":
                    url = "https://github.com/AdoptOpenJDK/openjdk15-binaries/releases/download/jdk-15.0.2 7/OpenJDK15U-jre_x64_windows_hotspot_15.0.2_7.zip"
                
                elif self.architechture == "i386":
                    url = "https://github.com/AdoptOpenJDK/openjdk15-binaries/releases/download/jdk-15.0.2 7/OpenJDK15U-jre_x86-32_windows_hotspot_15.0.2_7.zip"

                filename = "openjdk-15.zip"
                jdk_directory = "%s/jdk-15.0.2+7-jre" % java_directory

        if url:
            zip_file = web.download(url, "%s/%s" % (temp_directory, filename))
        else:
            logging.error("Operating System Unknown")
            exit()
        
        if os.path.isdir(jdk_directory) == False:
            if zip_file == False:
                print("zipfile : %s" % zip_file)
                exit()
            else:
                print(zip_file, java_directory)
                _file.extract_zip(zip_file, java_directory)

        self.java = "%s/bin/java" % jdk_directory
        return True

    def verify_eula(self):
        eula_file = "%s/eula.txt" % self.server_root
        if os.path.isfile(eula_file):
            full_text = ""
            with open(eula_file,"r") as eula:
                for i in eula.read().splitlines():
                    if "eula=" in i:
                        if "eula=true" not in i:
                            full_text += "eula=true"
                        else:
                            return True
                    else:
                        full_text += i + "\n"
            
            with open(eula_file,"w") as eula:
                eula.write(full_text)
        else:
            with open(eula_file,"w") as eula:
                eula.write("eula=true")
    
    def download_server(self):
        self.downloader = search_version(minecraft_root=".temp")
        self.downloader.download_versions(version=self.version)
        version_parser = parse_minecraft_version(minecraft_root=".temp",version=self.version)
        jar_path = version_parser.download_server(self.server_root)
        _file.rm_rf(".temp")
        return jar_path
    
    def get_java_arguments(self):
        arguments = []
        arguments.append("-Xmx1024M")
        arguments.append("-Xms1024M")
        return arguments
    
    def get_server_arguments(self):
        arguments = []
        arguments.append("nogui")
        return arguments
    
    def set_server_properties(self, server_properties=None):
        if server_properties == None:
            return False

        server_properties_file = "%s/server.properties" % self.server_root
        if os.path.isfile(server_properties_file):
            text_file = _file.get_content_file(server_properties_file)

            for line in text_file.splitlines():
                for i in server_properties:
                    if i in line:
                        text_file = text_file.replace(line, "%s=%s" % (i, server_properties[i]))
        else:
            text_file = ""
            for i in server_properties:
                text_file += "%s=%s" % (i, server_properties[i])
            
        with open(server_properties_file, "w") as server_prop:
            server_prop.write(text_file)

    def start(self, java_arguments=None, java=None, server_properties=None, jar_filename=None):

        if java_arguments:
            if type(java_arguments) == str:
                self.java_arguments = java_arguments.split(" ")
            elif type(java_arguments) == list:
                self.java_arguments = java_arguments

        if java == None:
            java = self.java
        
        if self.version:
            self.download_server()
        else:
            if os.path.isdir(self.server_root) == False:
                logging.warning("the folder %s doesn't exist", self.server_root)
                return False
            else:
                if os.path.isfile("%s/server.jar" % self.server_root) == False:
                    logging.error("can't find %s/server.jar" % (self.server_root))
                    return False
        self.verify_eula()

        if server_properties:
            self.set_server_properties(server_properties)

        if self.java_arguments:
            java_arguments = " ".join(self.java_arguments)
        else:
            java_arguments = " ".join(self.get_java_arguments())

        server_arguments = " ".join(self.get_server_arguments())

        os.chdir(self.server_root)
        if jar_filename == None:
            jar_filename = "server.jar"

        _file.command("\"%s\" %s -jar %s %s" % (java, java_arguments, jar_filename, server_arguments))