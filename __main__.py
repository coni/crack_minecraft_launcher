import argparse
import logging
import sys
import os
from libraries.launcher.launcher import gally_launcher
from libraries.launcher.server import minecraft_server
import libraries.utils.web as web
import libraries.utils._file as _file

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
system = _file.get_os()

parser = MyParser()

parser.add_argument("-t", "--type", help="Launcher type (client|server)")

parser.add_argument("-v", "--version", help="Load version")
parser.add_argument("-dont_start", "--dont_start", action="store_true", help="Dont start the game")
parser.add_argument("-r", "--root", help="Set minecraft root")
parser.add_argument("-j", "--java_runtime", help="Specify your java binary path")
parser.add_argument("-ja", '--java_argument')
parser.add_argument("-lv", "--list_versions", help="List Minecraft versions (release|downloaded|snapshot)")
parser.add_argument("-debug", "--debug", action="store_true", help="Show everything")

parser.add_argument("-console", "--console", action="store_true", help="Java console when starting Minecraft client")
parser.add_argument("-update", "--update", action="store_true", help="Update the launcher")
parser.add_argument("-q", "--quiet", action="store_true", help="Don't show any messages")
parser.add_argument("-launcher_version", "--launcher_version", action="store_true", help="Show launcher version")
parser.add_argument("-install", "--install", action="store_true", help="EXPERIMENTAL: Add the game to path")
parser.add_argument("-c", "--credit", action="store_true", help="Credit")

args, unknown = parser.parse_known_args()
args = vars(args)

if args["type"] == "server" or args["type"] == "s":
    type_ = "server"

if type_ == "client":
    parser.add_argument("-d", "--download", help="download client")
    parser.add_argument("-lp", "--list_profiles", action='store_true', help="list every existing profiles")
    parser.add_argument("-p", "--profile", help="load profile")
    parser.add_argument("-w", "--without_assets", action="store_true", help="can start the game much faster but without some texture")
    parser.add_argument("-u", "--username", help="set username")
    parser.add_argument("-g", '--gameDirectory')

    parser.add_argument("-password", "--password", help="password to login to a Mojang account")
    parser.add_argument("-email", "--email", help="email to login to a Mojang account")
    parser.add_argument("-logout", "--logout", action="store_true", help="disconnect to a Mojang account")
    parser.add_argument("-login", "--login", action="store_true", help="login to a mojang account (with a prompt for email and password)")
    parser.add_argument("-skin", "--skin", help="(only for offline player) choose skin from a player name")

elif type_ == "server":
    parser.add_argument("-motd", "--motd", help="server displayed message (Default = A Minecraft Server")
    parser.add_argument("-pvp", "--pvp", help="friendly fire (Default = true)")
    parser.add_argument("-difficulty", "--difficulty", help="Difficulty (default = easy)")
    parser.add_argument("-server_port", "--server_port", help="Server Port (default = 25565)")

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
if args["version"] or args["list_versions"] or args["type"] == "server" and args["root"] or args["download"] or args["logout"] or args["login"] or args["email"]:
    pass
else:
    parser.help()

if sys.argv[0].split(".")[-1] == "exe":
    file_extension = "exe"

if args["quiet"]:
    logging.basicConfig(level=logging.WARNING)
else:
    if args["debug"]:
        debug = True
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

if system == "linux":
    try:
        temp_directory = os.environ["TMPDIR"]
    except:
        temp_directory = "/tmp"
    gally_path = "%s/.gally_launcher" % (os.environ["HOME"])
elif system == "windows":
    temp_directory = os.environ["temp"]
    gally_path = "%s/gally_launcher" % (os.environ["appdata"])

if args["launcher_version"]:
    print(version)

if args["update"]:
    if type(version) == int:
        executable_path = sys.argv[0]
        updater_path = "%s/gally_update.exe" % (gally_path)
        if executable_path[-4:] == ".exe":
            last_version = int(web.get("https://github.com/coni/gally_update/releases/download/latest/version"))
            if last_version > version:
                if os.path.isfile("%s/update.exe" % (gally_path)) == False:
                    web.download("https://github.com/coni/gally_update/releases/download/latest/gally_update.exe", updater_path, exist_ignore=True)
                _file.command("start \"\" \"%s\" \"%s\"" % (updater_path, executable_path))
            else:
                print("already the latest version")
        else:
            print("can only update with executable version")
    else:
        print("This is an experimental build. You can't update it")

    sys.exit()

if args["install"]:
    logging.warning("EXPERIMENTAL FEATURE!")
    user_response = input("Are you sure you want to continue? (y/n) : ")
    if user_response == "y":
        if file_extension == "exe":
            _file.cp(sys.argv[0], gally_path)
        _file.set_path(gally_path)
    else:
        print("response is negative, exiting the script")
        sys.exit()

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
    
    if args["skin"]:
        launcher.version_parser.set_skin(args["skin"])
        
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
        launcher.download_java(version=launcher.version)
        launcher.start(dont_start=args["dont_start"], debug=debug, assets=assets, java=java, console=args["console"], java_argument=args["java_argument"], game_directory=game_directory)

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
        server.download_java()
        server.start(java=java, server_properties=server_properties, java_arguments=java_argument)