import argparse
import logging
import sys
import os
from libraries.launcher.launcher import gally_launcher
from libraries.launcher.server import minecraft_server
import libraries.utils.web as web
import libraries.utils._file as _file

if len(sys.argv) > 1:
    arguments = True
else:
    arguments = False

version = "still_beta_im_sorry_for_the_commit"
should_start = False
java_argument = None
type_ = "client"

def list_commands():
    print("version *version*       e.g: \"version 1.17\"")
    print("profile *profile*       e.g: \"profile OptiFine\"")
    print("without_assets               start without assets. Can start the game faster")
    print("list_versions *type*         type: \"all|release|snapshot|beta|alpha\"")
    print("list_profiles                 list every profile")
    print("java_launch *path_to_java*   use it if you know what you are doing")
    print("username *name*              set username. e.g: \"username coni\"")
    print("download *version*   download a version without starting the game (doesn't download assets)")
    print("start                        start the game\n")

all_args = argparse.ArgumentParser()
all_args.add_argument("-v", "--version", help="load version")
all_args.add_argument("-lv", "--list_versions", help="list every official versions of Minecraft")
all_args.add_argument("-d", "--download", help="download client")
all_args.add_argument("-lp", "--list_profiles", action='store_true', help="list every existing profiles")
all_args.add_argument("-p", "--profile", help="load profile")
all_args.add_argument("-w", "--without_assets", action="store_true", help="can start the game much faster but without some texture")
all_args.add_argument("-u", "--username", help="set username")
all_args.add_argument("-j", "--java_launch", help="choose your java")
all_args.add_argument("-debug", "--debug", action="store_true", help="don't show info except warning and error")
all_args.add_argument("-r", "--root", help="set minecraft root")
all_args.add_argument("-c", "--credit", action="store_true", help="contributor credit")
all_args.add_argument("-t", "--type", help="launcher type, for playing as casual or hosting a server (client | server )")

all_args.add_argument("-ja", '--java_argument')
all_args.add_argument("-g", '--gameDirectory')

all_args.add_argument("-motd", "--motd", help="server: server displayed message (Default = A Minecraft Server")
all_args.add_argument("-pvp", "--pvp", help="server: friendly fire (Default = true)")
all_args.add_argument("-difficulty", "--difficulty", help="server: Difficulty (default = easy)")
all_args.add_argument("-server_port", "--server_port", help="server: Server Port (default = 25565)")

all_args.add_argument("-gamemode", "--gamemode", help="server: player mode (default = survival)")
all_args.add_argument("-view_distance", "--view_distance", help="server: max distance entities spawn (default = 10)")
all_args.add_argument("-allow_nether", "--allow_nether", help="server: allowing nether (default = true)")
all_args.add_argument("-enable_command_block", "--enable_command_block", help="server: enable command block (default = false)")
all_args.add_argument("-level_name", "--level_name", help="server: world name (defaultl = world)")
all_args.add_argument("-force_gamemode", "--force_gamemode", help="server: force gamemode for every player (default = false)")
all_args.add_argument("-hardcore", "--hardcore", help="server: set the server in hardcore (1 life) (default = false)")
all_args.add_argument("-white_list", "--white_list", help="server: only white list player (from whitelist.json file) can join (default = false)")
all_args.add_argument("-spawn_npcs", "--spawn_npcs", help="server: spawn_npcs (default = true)")
all_args.add_argument("-spawn_animals", "--spawn_animals", help="server: spawn animals (default = true)")
all_args.add_argument("-generate_structures", "--generate_structures", help="server: allow structures in the world (default = true)")
all_args.add_argument("-max_tick_time", "--max_tick_time", help="server: max tick (default 60000)")
all_args.add_argument("-max_players", "--max_players", help="server: max players limitation (default 20)")
all_args.add_argument("-spawn_protection", "--spawn_protection", help="server: zone protected can't be grief by non op player (default = 16)")
all_args.add_argument("-online_mode", "--online_mode", help="server: prohibit cracked players (default = true)")
all_args.add_argument("-allow_flight", "--allow_flight", help="server: allow players to fly in survival (default = false)")
all_args.add_argument("-level_type", "--level_type", help="server: level_type")

all_args.add_argument("-console", "--console", action="store_true", help="java console when starting Minecraft client")
all_args.add_argument("-update", "--update", action="store_true", help="update the launcher")
all_args.add_argument("-q", "--quiet", action="store_true", help="don't show any messages")
all_args.add_argument("-launcher_version", "--launcher_version", action="store_true", help="show launcher version")
all_args.add_argument("-install", "--install", action="store_true", help="add to path")

all_args.add_argument("-password", "--password", help="password to login to a Mojang account")
all_args.add_argument("-email", "--email", help="email to login to a Mojang account")
all_args.add_argument("-logout", "--logout", action="store_true", help="disconnect to a Mojang account")
all_args.add_argument("-login", "--login", action="store_true", help="login to a mojang account (with a prompt for email and password)")
all_args.add_argument("-skin", "--skin", help="(only for offline player) choose skin from a player name")


args = vars(all_args.parse_args())
debug = False
system = _file.get_os()

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

if args["type"] == "server":
    type_ = "server"

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

    if args["java_launch"]:
        java = args["java_launch"]

    if args["username"]:
        launcher.set_username(args["username"])
    else:
        launcher.set_username("steve")
        
    if args["without_assets"]:
        assets = False
    
    if args["skin"]:
        launcher.version_parser.set_skin(args["skin"])
        
    if args["profile"]:
        should_start = launcher.load_profile(args["profile"])

    if args["version"]:
        should_start = launcher.load_version(args["version"])
    
    if args["gameDirectory"]:
        game_directory = args["gameDirectory"]
    else:
        game_directory = None

    if should_start:
        if args["email"]:
            launcher.login(args["email"], args["password"])

        launcher.download_java(version=launcher.version)
        launcher.start(debug=debug, assets=assets, java=java, console=args["console"], java_argument=args["java_argument"], game_directory=game_directory)

    if arguments == False:
        while True:
            info_prompt = []
            argument = None
            exist = False

            if launcher.version_parser.version:
                info_prompt.append("launch")
                info_prompt.append("version %s" % launcher.version_parser.version)

            if launcher.profile_id:
                info_prompt.append("in %s profile" % launcher.profile_id)
            
            if launcher.version_parser.username:
                info_prompt.append("as %s" % launcher.version_parser.username)
            
            if assets == False:
                info_prompt.append("without assets")

            prompt = input("%s > " % " ".join(info_prompt))

            argument_prompt = prompt.split(" ")

            if len(argument_prompt) > 1:
                argument = argument_prompt[1]

            if argument_prompt[0] == "list_versions":
                exist = True

                if argument == None:
                    print("ERROR: usage : list_versions release|downloaded|snapshot|beta|alpha\n")

                launcher.list_versions(argument)

            if argument_prompt[0] == "download":
                exist = True
                launcher.download_version(argument)

            if argument_prompt[0] == "list_profiles":
                exist = True
                launcher.list_profiles()
            
            if argument_prompt[0] == "java_launch":
                exist = True
                java = argument

            if argument_prompt[0] == "version":
                exist = True
                launcher.load_version(argument)
                should_start = True

            if argument_prompt[0] == "username":
                exist = True
                launcher.set_username(argument)

            if argument_prompt[0] == "profile":
                exist = True
                launcher.load_profile(argument)
                should_start = True

            if argument_prompt[0] == "without_assets":
                exist = True
                if assets:
                    assets = False
                else:
                    assets = True
            
            if argument_prompt[0] == "help":
                exist = True
                list_commands()

            if argument_prompt[0] == "start":
                exist = True
                launcher.start(assets=assets, java=java)
                break
                
            if exist == False:
                list_commands()

elif type_ == "server":
    version = args["version"]

    if args["java_argument"]:
        java_argument = args["java_argument"]

    server = minecraft_server(version=args["version"], server_root=root)

    if args["download"]:
        server.download_server()

    if args["java_launch"]:
        java = args["java_launch"]

    server_properties = {}

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