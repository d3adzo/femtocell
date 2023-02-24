import femtoshell
import argparse
import sys
import os
from termcolor import colored

def handle_args_main(ags):
    print('non interactive mode')
    print(ags)
    if ags.debug:
        femtoshell.baseparams["XOR"] = False
    
    if ags.pwnboard is not None:
        femtoshell.baseparams["PWNBOARD"] = ags.pwnboard

    femtoshell.baseparams["MODE"] = ags.mode.upper()

    if ags.mode.upper() == "SHELL":
        femtoshell.shellparams["RHOST"] = ags.target
        femtoshell.shellparams["RPORT"] = ags.port
        femtoshell.shellparams["TRANSPORT"] = ags.transport.upper()
        femtoshell.shellparams["LHOST"] = ags.local

        femtoshell.executeShell()
    elif ags.mode.upper() == "CMD":
        femtoshell.cmdparams["RHOST"] = ags.target
        femtoshell.cmdparams["RPORT"] = ags.port
        femtoshell.cmdparams["TRANSPORT"] = ags.transport.upper()
        femtoshell.cmdparams["COMMAND"] = ' '.join(ags.command)

        femtoshell.executeCmd()
    elif ags.mode.upper() == "GROUP":
        femtoshell.groupparams["RHOST"] = ags.target
        femtoshell.groupparams["RPORT"] = ags.port
        femtoshell.groupparams["TRANSPORT"] = ags.transport.upper() 
        femtoshell.groupparams["GROUP"] = ags.group
        femtoshell.groupparams["COMMAND"] = ' '.join(ags.command)

        if ags.file is not None and os.path.exists(ags.file):
            femtoshell.importConfig(ags.file)
        else:
            print(colored(f"[!] File {ags.file} doesn't exist.\n", "red"))
            return

        femtoshell.executeGroup()
    else:
        print( colored( f"[!] MODE {ags.mode} does not exist. Setting MODE value back to blank.\n", "red",))
    return
    # elif ags.mode.upper() == "PING":

def setup_args():
    parser = argparse.ArgumentParser(
        description="FIX ME"
    )
    parser.add_argument(
        "-l",
        "--local",
        type=str,
        nargs="?",
        const=1,
        help="IP to send the shell",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        nargs="?",
        const=1,
        help="IP to send the shell",
    )
    parser.add_argument(
        "-t",
        "--target",
        type=str,
        nargs="?",
        const=1,
        help="Target machine",
    )
    parser.add_argument(
        "-c",
        "--command",
        type=str,
        nargs="+",
        help="Target machine",
    )
    parser.add_argument(
        "-r",
        "--transport",
        type=str,
        nargs="?",
        const=1,
        help="Target machine",
        default="TCP",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        nargs="?",
        const=1,
        help="load file to utilize group mode",
    )
    parser.add_argument(
        "-g",
        "--group",
        type=str,
        nargs="?",
        const=1,
        help="target group from file",
    )
    parser.add_argument(
        "--pwnboard",
        type=str,
        nargs="?",
        const=1,
        help="pwnboard url to utilize",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        nargs="?",
        const=1,
        help="Port to target (default: 445)",
        default=445,
    )
    parser.add_argument("--debug", dest="debug", action="store_true", help="help")
    parser.set_defaults(debug=False)
    ags = parser.parse_args()
    if len(sys.argv) >= 3: 
        handle_args_main(ags)
        exit()