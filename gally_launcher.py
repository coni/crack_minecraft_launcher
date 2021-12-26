import argparse
import logging
import sys
import os
from libraries.launcher.client import gally_launcher
from libraries.launcher.server import minecraft_server
import libraries.utils.request as request
import libraries.utils.system as system
import json

class MyParser(argparse.ArgumentParser):
    def help(self):
        self.print_help()
        sys.exit(2)

if len(sys.argv) > 1:
    arguments = True
else:
    arguments = False

version = "still_beta_im_sorry_for_the_commit"
start = False
java_argument = None
type_ = "client"
debug = False
osName = system.get_os()

parser = MyParser()

parser.add_argument("-t", "--type", help="Launcher type (client|server)")

parser.add_argument("-password", "--password", help="password to login to a Mojang account")
parser.add_argument("-email", "--email", help="email to login to a Mojang account")
parser.add_argument("-logout", "--logout", action="store_true", help="disconnect to a Mojang account")
parser.add_argument("-login", "--login", action="store_true", help="login to a mojang account (with a prompt for email and password)")

parser.add_argument("-d", "--download", help="download client")
parser.add_argument("-v", "--version", help="Load version")
parser.add_argument("-ds", "--dont_start", action="store_true", help="Dont start the game")
parser.add_argument("-r", "--root", help="Set minecraft root")
parser.add_argument("-j", "--java_runtime", help="Specify your java binary path")
parser.add_argument("-ja", '--java_argument')
parser.add_argument("-lv", "--list_versions", help="List Minecraft versions (release|downloaded|snapshot)")
parser.add_argument("-db", "--debug", action="store_true", help="Show everything")

parser.add_argument("-c", "--console", action="store_true", help="Java console when starting Minecraft client")
parser.add_argument("-up", "--update", action="store_true", help="Update the launcher")
parser.add_argument("-q", "--quiet", action="store_true", help="Don't show any messages")
parser.add_argument("-i", "--install", action="store_true", help="EXPERIMENTAL: Add the game to path")
parser.add_argument("-credit", "--credit", action="store_true", help="Credit")

parser.add_argument("-test", "--test", action="store_true", help="test")
parser.add_argument("-sp", "--server_port", help="Server Port (default = 25565)")

args, unknown = parser.parse_known_args()
args = vars(args)

if args["type"] == "server" or args["type"] == "s":
    type_ = "server"

if type_ == "client":
    parser.add_argument("-lp", "--list_profiles", action='store_true', help="list every existing profiles")
    parser.add_argument("-p", "--profile", help="load profile")
    parser.add_argument("-w", "--without_assets", action="store_true", help="can start the game much faster but without some texture")
    parser.add_argument("-u", "--username", help="set username")
    parser.add_argument("-g", '--gameDirectory')

    parser.add_argument("-s", '--server', help="auto connect to the specified server")

    parser.add_argument("-uuid_of", "--uuid_of", help="(only for offline player) choose the uuid of a player")
    parser.add_argument("-uuid", "--uuid", help="(only for offline player) choose an uuid")
    
elif type_ == "server":
    parser.add_argument("-motd", "--motd", help="server displayed message (Default = A Minecraft Server")
    parser.add_argument("-pvp", "--pvp", help="friendly fire (Default = true)")
    parser.add_argument("-difficulty", "--difficulty", help="Difficulty (default = easy)")

    parser.add_argument("-gamemode", "--gamemode", help="player mode (default = survival)")
    parser.add_argument("-view_distance", "--view_distance", help="max distance entities spawn (default = 10)")
    parser.add_argument("-allow_nether", "--allow_nether", help="allowing nether (default = true)")
    parser.add_argument("-enable_command_block", "--enable_command_block", help="enable command block (default = false)")
    parser.add_argument("-level_name", "--level_name", help="world name (defaultl = world)")
    parser.add_argument("-force_gamemode", "--force_gamemode", help="force gamemode for every player (default = false)")
    parser.add_argument("-hardcore", "--hardcore", help="set the server in hardcore (1 life) (default = false)")
    parser.add_argument("-white_list", "--white_list", help="only white list player (from whitelist.json file) can join (default = false)")
    parser.add_argument("-spawn_npcs", "--spawn_npcs", help="spawn_npcs (default = true)")
    parser.add_argument("-spawn_animals", "--spawn_animals", help="spawn animals (default = true)")
    parser.add_argument("-generate_structures", "--generate_structures", help="allow structures in the world (default = true)")
    parser.add_argument("-max_tick_time", "--max_tick_time", help="max tick (default 60000)")
    parser.add_argument("-max_players", "--max_players", help="max players limitation (default 20)")
    parser.add_argument("-spawn_protection", "--spawn_protection", help="zone protected can't be grief by non op player (default = 16)")
    parser.add_argument("-online_mode", "--online_mode", help="prohibit cracked players (default = true)")
    parser.add_argument("-allow_flight", "--allow_flight", help="allow players to fly in survival (default = false)")
    parser.add_argument("-level_type", "--level_type", help="level_type")

args = vars(parser.parse_args())
if args["version"] or args["test"] or args["install"] or args["update"] or args["list_versions"] or args["type"] == "server" and args["root"] or args["download"] or args["logout"] or args["login"] or args["email"]:
    pass
else:
    parser.help()


if args["quiet"]:
    logging.basicConfig(level=logging.WARNING)
else:
    if args["debug"]:
        debug = True
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

if osName == "linux":
    try:
        temp_directory = os.environ["TMPDIR"]
    except:
        temp_directory = "/tmp"
    gally_path = "%s/.gally_launcher" % (os.environ["HOME"])
elif osName == "windows":
    temp_directory = os.environ["temp"]
    gally_path = "%s/gally_launcher" % (os.environ["appdata"])

if args["update"]:
    if getattr(sys, 'frozen', False):
        executable_fullpath =  sys.executable
        executable_temp = executable_fullpath + ".tmp"
    elif __file__:
        print("incorrect file")
        sys.exit()

    if osName == "linux":
        url = "https://github.com/coni/gally_launcher/releases/download/latest/gally_launcher"
    else:
        url = "https://github.com/coni/gally_launcher/releases/download/latest/gally_launcher.exe"

    if request.download(url, executable_temp):
        if osName == "windows":
            filename = sys.executable.split("\\")[-1]
            if os.path.isfile(temp_directory + "/" + filename):
                os.remove(temp_directory + "/" + filename)
            os.rename(executable_fullpath, temp_directory + "/" + filename)
        os.rename(executable_temp, executable_fullpath)
        if osName == "linux":
            system.command("chmod +x %s" % executable_fullpath)
            
        logging.info("sucessfully updated")
    else:
        logging.info("An error occured")
    sys.exit()

if args["test"]:
    import libraries.minecraft.java as hihi
    java_manifest_url = hihi.get_manifest("linux","jre-legacy")

    java_manifest_path = "/tmp/java_manifest.json"
    java_manifest = None
    if request.download(java_manifest_url, java_manifest_path):
        with open(java_manifest_path, "r") as temp:
            java_manifest = json.load(temp)
        hihi.download_java(java_manifest, "./java/")


if args["install"]:
    if osName == "linux":
        if getattr(sys, 'frozen', False):
            executable_fullpath =  sys.executable
        elif __file__:
            print("incorrect file")
            sys.exit()
        if osName == "linux":
            delim = "/"
        else:
            delim = "\\"
        home_path = os.environ["HOME"]
        accepted_paths = [home_path + "/.local/bin/", home_path + "/bin/", home_path + "/.bin/", "/usr/local/bin/", "/usr/bin/", "/usr/local/sbin/", "/bin/"]
        bin_path = None
        for path in accepted_paths:
            for sys_path in os.environ["PATH"].split(":"):
                if sys_path[-1] != delim:
                    sys_path += delim
                if path == sys_path:
                    bin_path = sys_path
                    break
            if bin_path:
                break
        if bin_path:
            try:
                filename = system.cp(executable_fullpath, bin_path + "gally_launcher")
                if osName == "linux":
                    os.system("chmod +x %s" % filename)
                logging.info("sucessfully installed gally_launcher to the path (%s)", bin_path)
            except PermissionError:
                logging.error("can't install gally_launcher to %s, retry with 'sudo'" % bin_path)
        else:
            logging.error("Can't find correct PATH..")
    else:
        logging.error("this feature is only for the linux users")
        
if args["credit"]:
    print("author : coni (github.com/coni)")
    print("made with love <3")
    print("my code may be trashy, any advice is welcome")

if args["root"]:
    root = args["root"]
else:
    root = None

assets = True
java = None
if type_ == "client":
    launcher = gally_launcher(minecraft_root=root)

    if args["logout"]:
        if launcher.logout(args["email"], args["password"]):
            print("logout sucessfully")
        else:
            logging.warning("failed to logout")

    if args["login"]:
        args["email"] = input("Email : ")

    if args["list_versions"]:
        launcher.list_versions(args["list_versions"])

    if args["download"]:
        logging.info("Downloading %s" % args["download"])
        launcher.download_version(args["download"])

    if args["list_profiles"]:
        launcher.list_profiles()

    if args["java_runtime"]:
        java = args["java_runtime"]

    if args["username"]:
        launcher.set_username(args["username"])
    else:
        launcher.set_username("steve")
        
    if args["without_assets"]:
        assets = False
    
    if args["uuid_of"]:
        launcher.set_uuid(username=args["uuid_of"])
    
    if args["uuid"]:
        launcher.set_uuid(uuid=args["uuid_of"])
        
    if args["profile"]:
        start = launcher.load_profile(args["profile"])

    if args["version"]:
        start = launcher.load_version(args["version"])
    
    if args["gameDirectory"]:
        game_directory = args["gameDirectory"]
    else:
        game_directory = None

    if args["email"] and args["logout"] == False:
        launcher.login(args["email"], args["password"])

    if start:
        launcher.start(
        game_directory=game_directory,
        debug=debug,
        assets=assets,
        java=java,
        console=args["console"],
        java_argument=args["java_argument"],
        ip=args["server"],
        port=args["server_port"],
        dont_start=args["dont_start"])

elif type_ == "server":
    version = args["version"]

    server = minecraft_server(version=args["version"], server_root=root)
    server_properties = {}

    if args["java_argument"]:
        java_argument = args["java_argument"]

    if args["download"]:
        server.download_server()

    if args["java_runtime"]:
        java = args["java_runtime"]

    if args["motd"]:
        server_properties["motd"] = args["motd"]

    if args["server_port"]:
        server_properties["server-port"] = args["server_port"]

    if args["pvp"]:
        server_properties["pvp"] = args["pvp"]

    if args["gamemode"]:
        server_properties["gamemode"] = args["gamemode"]

    if args["view_distance"]:
        server_properties["view-distance"] = args["view_distance"]

    if args["allow_nether"]:
        server_properties["allow-nether"] = args["allow_nether"]

    if args["enable_command_block"]:
        server_properties["enable-command-block"] = args["enable_command_block"]

    if args["force_gamemode"]:
        server_properties["force-gamemode"] = args["force_gamemode"]

    if args["hardcore"]:
        server_properties["hardcore"] = args["hardcore"]

    if args["white_list"]:
        server_properties["white-list"] = args["white_list"]

    if args["spawn_npcs"]:
        server_properties["spawn-npcs"] = args["spawn_npcs"]

    if args["spawn_animals"]:
        server_properties["spawn-animals"] = args["spawn_animals"]

    if args["generate_structures"]:
        server_properties["generate-structures"] = args["generate_structures"]

    if args["level_type"]:
        server_properties["level-type"] = args["level_type"]

    if args["max_tick_time"]:
        server_properties["max-tick-time"] = args["max_tick_time"]

    if args["max_players"]:
        server_properties["max-players"] = args["max_players"]

    if args["spawn_protection"]:
        server_properties["spawn-protection"] = args["spawn_protection"]

    if args["online_mode"]:
        server_properties["online-mode"] = args["online_mode"]

    if args["allow_flight"]:
        server_properties["allow-flight"] = args["allow_flight"]
    
    if version or root:
        server.start(java=java, server_properties=server_properties, java_arguments=java_argument)