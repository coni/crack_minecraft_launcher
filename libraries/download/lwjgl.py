import libraries.utils.request as request
import libraries.utils.system as system
import os

temp_dir = "/tmp/gally_launcher"

def download_binary(lwjgl_version, path, osName):

    binary_url = []
    if lwjgl_version.split(".")[0] == "3":
        
        if os.path.isdir(path) == False:
            base_url_x64 = "https://build.lwjgl.org/release/%s/%s/x64" % (lwjgl_version, osName)
            base_url_x86 = "https://build.lwjgl.org/release/%s/windows/x86" % lwjgl_version

            if osName == "windows":

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

            elif osName == "linux":
                binary_url.append("%s/%s" % (base_url_x64, "libglfw.so"))
                binary_url.append("%s/%s" % (base_url_x64, "libglfw_wayland.so"))
                binary_url.append("%s/%s" % (base_url_x64, "libjemalloc.so"))
                binary_url.append("%s/%s" % (base_url_x64, "liblwjgl.so"))
                binary_url.append("%s/%s" % (base_url_x64, "liblwjgl_opengl.so"))
                binary_url.append("%s/%s" % (base_url_x64, "liblwjgl_stb.so"))
                binary_url.append("%s/%s" % (base_url_x64, "libopenal.so"))
                binary_url.append("%s/%s" % (base_url_x64, "liblwjgl_tinyfd.so"))
        else:
                return True

    elif lwjgl_version.split(".")[0] == "2":
        if os.path.isdir(path) == False:
            if lwjgl_version == "2.9.4":
                zip_url = "http://ci.newdawnsoftware.com/job/LWJGL-git-dist/lastBuild/artifact/dist/lwjgl-2.9.4.zip"
            else:
                zip_url = "https://versaweb.dl.sourceforge.net/project/java-game-lib/Official Releases/LWJGL %s/lwjgl-%s.zip" % (lwjgl_version, lwjgl_version)
        else:
            return path
    
    zip_filename = "%s/%s.zip" % (temp_dir, lwjgl_version)

    if binary_url:
        binary_full_path = path
        for url in binary_url:
            binary_filename = url.split("/")[-1]
            binary_file = "%s/%s" % (path, binary_filename)
            request.download(url, binary_file)

    elif zip_url:
        request.download(zip_url, zip_filename)
        if os.path.isfile(zip_filename):
            list_folder_extracted = system.extract_archive(zip_filename, temp_dir)

            for folder in list_folder_extracted:
                if folder == "lwjgl-%s/native/%s/" % (lwjgl_version, osName):
                    system.mv("%s/lwjgl-%s/native/%s/" % (temp_dir, lwjgl_version, osName),"%s" % path)
    return True