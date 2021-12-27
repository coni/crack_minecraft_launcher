import urllib.request
import urllib.parse
import os
import sys
import libraries.utils.system as system
import uuid
import logging
import json
import re
import socket


class obj:
    def __init__(self):
        pass

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

def download(url="", filename="", multiple_files=[], total_size=0, string="", replace=False):

    osNamae = system.get_os()
    if osNamae == "linux":
        delim = "/"
        delim_ = "\\"
        try:
            temp_directory = os.environ["TMPDIR"]
        except:
            temp_directory = "/tmp/gally_launcher"
    elif osNamae == "windows":
        delim = "\\"
        delim_ = "/"
        temp_directory = os.environ["temp"] + delim + "gally_launcher"
        

    
    if delim:
        path = delim.join(filename.split(delim)[:-1])
        if path:
            if os.path.isdir(path) == False:
                system.mkdir_recurcive(path)
        
    if url and filename:
        url = urllib.parse.quote(url).replace("%3A",":")
        multiple_files.append((url, filename, total_size))

    all_size = 0
    block_sz = 8192
    for url, path, size in  multiple_files:
        path = path.replace(delim_,delim)
        filename = path.split(delim)[-1]
        temp_filename = temp_directory + delim + filename

        if os.path.isfile(path) == False or replace == True:
            directory = delim.join(path.split(delim)[:-1])
            temp_directory = delim.join(temp_filename.split(delim)[:-1])
            if directory:
                if os.path.isdir(directory) == False:
                    system.mkdir_recurcive(directory)
                    
                if os.path.isdir(temp_directory) == False:
                    system.mkdir_recurcive(temp_directory)
            
            try:
                u = urllib.request.urlopen(url)
                f = open(temp_filename, 'wb')

                while True:
                    buffer = u.read(block_sz)
                    if not buffer:
                        break

                    all_size += len(buffer)
                    f.write(buffer)
                    if string:
                        status = r"%s [%i%%]    " % (string, all_size * 100. / total_size)
                        status = status + chr(8)*(len(status)+1)
                        sys.stdout.flush()
                        sys.stdout.write(status)
                f.close()
                system.mv(temp_filename, path)

            except KeyboardInterrupt:
                sys.exit()
        else:
            all_size += size
    return True
        

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