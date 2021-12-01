api = "https://api.adoptium.net"

def get_java(majorVersion, os, architecture):
    if architecture == "AMD64" or architecture == "x86_64":
        architecture = "x64"
    elif architecture == "i386":
        architecture = "x86"

    url = "%s/v3/binary/latest/%s/ga/%s/%s/jre/hotspot/normal/eclipse" % (api, majorVersion, os, architecture)

    return url
