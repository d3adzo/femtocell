import os
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from termcolor import colored

import femtocell

def interactive_main():
    print(colored("FEMTOCELL // INTERACTIVE\n", "green"))
    if not os.path.exists("./history"):
        os.system("mkdir history")

    while True:
        user_in = prompt(
            "FEMTOCELL // ",
            history=FileHistory("history/main.history"),
            auto_suggest=AutoSuggestFromHistory(),
        ).split()

        if len(user_in) == 3:
            user_cmd = user_in[0].upper()
            op_1 = user_in[1].upper()
            op_2 = user_in[2].upper()

            if user_cmd == "SET":
                femtocell.baseparams[op_1] = op_2
                if op_1 == "MODE":
                    if ( femtocell.baseparams["MODE"] == "SHELL" or femtocell.baseparams["MODE"] == "CMD" or femtocell.baseparams["MODE"] == "GROUP"):
                        pass
                    else:
                        print( colored( f"[-] MODE {op_2} does not exist. Setting MODE value back to None.\n", "red",))
                        femtocell.baseparams["MODE"] = None
                        continue
                    print(colored(f"[*] Mode {op_2} set.\n", "cyan"))
                elif op_1 == "XOR":
                    if op_2 == "TRUE":
                        femtocell.baseparams["XOR"] = True
                    elif op_2 == "FALSE":
                        femtocell.baseparams["XOR"] = False
                    else:
                        print(
                            colored(f"[!] XOR can only be set to TRUE or FALSE.\n", "yellow")
                        )
                        continue
                    print(colored(f"[*] XOR set to {op_2}.\n", "cyan"))
                elif op_1 == "PWNBOARD":
                    op_2 = op_2.lower()
                    print(colored(f"[*] Pwnboard URL set to {op_2}.\n", "cyan"))
        elif len(user_in) == 2:
            user_cmd = user_in[0]
            op_1 = user_in[1]
            if user_cmd == "load":
                if os.path.exists(op_1):
                    femtocell.importConfig(op_1)
                else:
                    print(colored(f"[-] File {op_1} doesn't exist.\n", "red"))
                    continue
            else:
                femtocell.print_help("base")

        elif len(user_in) == 1:
            user_cmd = user_in[0].upper()

            if user_cmd == "EXIT":
                exit()
            elif user_cmd == "BANNER":
                femtocell.print_banner()
            elif user_cmd == "HELP":
                femtocell.print_help("base")
            elif user_cmd == "OPTIONS":
                femtocell.print_options(femtocell.baseparams)
            elif user_cmd == "READY":
                if femtocell.baseparams["MODE"] == "SHELL":
                    ready(femtocell.shellparams)
                elif femtocell.baseparams["MODE"] == "CMD":
                    ready(femtocell.cmdparams)
                elif femtocell.baseparams["MODE"] == "GROUP":
                    if len(femtocell.parsedConfig) == 0:
                        print(colored("[-] No config loaded.\n", "red"))
                        continue
                    ready(femtocell.groupparams)
                else:
                    print(colored("[-] No mode set.\n", "red"))
                    femtocell.print_options(femtocell.baseparams)
            else:
                femtocell.print_help("base")
        elif len(user_in) == 0:
            continue
        else:
            femtocell.print_help("base")


def ready(params):
    while True:
        user_in = prompt(
            f'FEMTOCELL // {femtocell.baseparams["MODE"]} // ',
            history=FileHistory("history/interact.history"),
            auto_suggest=AutoSuggestFromHistory(),
        ).split()

        if len(user_in) == 1:
            user_cmd = user_in[0].upper()

            if user_cmd == "BACK" or user_cmd == "EXIT":
                return
            elif user_cmd == "BANNER":
                femtocell.print_banner()
            elif user_cmd == "OPTIONS":
                femtocell.print_options(params)
            elif user_cmd == "HELP":
                femtocell.print_help("sub")
            elif femtocell.baseparams["MODE"] == "GROUP" and user_cmd == "TARGETS":
                if params["GROUP"] is None:
                    print(colored("[-] No GROUP set.\n", "red"))
                    continue
                femtocell.print_groups()
            elif user_cmd == "EXECUTE":
                if femtocell.baseparams["MODE"] == "CMD":
                    femtocell.executeCmd()
                elif femtocell.baseparams["MODE"] == "SHELL":
                    femtocell.executeShell()
                elif femtocell.baseparams["MODE"] == "GROUP":
                    femtocell.executeGroup()
                    
                else:
                    femtocell.print_help("sub")
                    continue
            elif user_cmd == "PING": 
                femtocell.executePing()
            else:
                femtocell.print_help("sub")
                continue
        elif len(user_in) == 3:
            user_cmd = user_in[0].upper()
            op_1 = user_in[1].upper()
            op_2 = user_in[2].upper()

            if user_cmd == "SET":
                if op_1 in params.keys():
                    if op_1 == "RPORT": 
                        op_2 = int(op_2)
                    elif op_1 == "GROUP" or op_1 == "COMMAND":
                        op_2 = op_2.lower()
                    params[op_1] = op_2
                    femtocell.print_options(params)
                elif op_1 == "IFACE":
                    femtocell.interface = op_2.lower()
                    print(colored(f"[*] Interface set to {femtocell.interface}.\n", "cyan"))
                else:
                    femtocell.print_help("sub")
            else:
                femtocell.print_help("sub")
        elif len(user_in) > 3:
            user_cmd = user_in[0].upper()
            op_1 = user_in[1].upper()

            if user_cmd == "SET":
                if op_1 == "COMMAND":
                    op_2 = ""
                    for i in range(2, len(user_in)):
                        op_2 = op_2 + user_in[i] + " "
                    params[op_1] = op_2.strip(" ")
                    femtocell.print_options(params)
            else:
                femtocell.print_help("sub")
        elif len(user_in) == 0:
            continue
        else:
            femtocell.print_help("sub")

