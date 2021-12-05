import urllib.request
import urllib.parse
import os
import sys
import libraries.utils._file as _file
import uuid
import logging
import json
import re
import socket

class obj:
    def __init__(self):
        pass


header= {
    "User-Agent": "hii",
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "Connection": "Keep-Alive"
    }

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0'), ("Accept", "*/*"), ("Accept-Encoding", "identity"), ("Connection", "Keep-Alive")]
urllib.request.install_opener(opener)

def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False

def download(url, filename, exist_ignore=False, retry=False):
    if exist_ignore:
        is_file = False
    else:
        is_file = os.path.isfile(filename)

    delim = None
    if "/" in filename:
        delim = "/"
    elif "\\" in filename:
        delim = "\\"
    

    if delim:
        path = delim.join(filename.split(delim)[:-1])
        if os.path.isdir(path) == False:
            _file.mkdir_recurcive(path)
    
    url_fixed = urllib.parse.quote(url).replace("%3A",":")

    if retry:
        if "%20" in url_fixed:
            url_fixed = url_fixed.replace("%20","%2B")
        else:
            url_fixed = url_fixed.replace("%2B","%20")

    try:
        if is_file == False:
            logging.debug("[web] download %s from %s" % (filename, url_fixed))
            data = urllib.request.urlopen(url_fixed).read()
            with open(filename,'wb') as download:
                download.write(data)
        else:
            logging.debug("[web] %s already exist (from %s)" % (filename, url_fixed))

        return filename
    except KeyboardInterrupt:
        sys.exit()
    except:
        logging.debug("[web] can't download %s from %s" % (filename, url_fixed))
        
def get_uuid(username=None):
    if username != None:
        req = get("https://api.mojang.com/users/profiles/minecraft/%s" % username)
        if req:
            return json.loads(req)["id"]

    uuid_ = str(uuid.uuid1()).replace("-","")
    logging.debug("[web] generate uuid : %s" % uuid_)
    return uuid_

def get(url):
    try:
        response = urllib.request.urlopen(url)
    except KeyboardInterrupt:
        sys.exit()
    except:
        logging.warning("[web] FAILED to request %s" % url)
        return False
    return response.read()

def post(url, data, headers=None):
    data = json.dumps(data).encode()
    
    req =  urllib.request.Request(url)
    if headers:
        for i in headers:
            req.add_header(i, headers[i])

    try:
        resp = urllib.request.urlopen(
            req,
            data=data
            )
    except urllib.error.HTTPError as e:
        resp = obj
        resp.status = e.code

    return resp