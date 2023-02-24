import os
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from termcolor import colored

import femtoshell

def interactive_main():
    print('interactive mode')
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
                femtoshell.baseparams[op_1] = op_2
                if op_1 == "MODE":
                    if ( femtoshell.baseparams["MODE"] == "SHELL" or femtoshell.baseparams["MODE"] == "CMD" or femtoshell.baseparams["MODE"] == "GROUP"):
                        pass
                    else:
                        print( colored( f"[!] MODE {op_2} does not exist. Setting MODE value back to blank.\n", "red",))
                        femtoshell.baseparams["MODE"] = ""
                        continue
                    print(colored(f"[*] Mode {op_2} set.\n", "cyan"))
                elif op_1 == "XOR":
                    if op_2 == "TRUE":
                        femtoshell.baseparams["XOR"] = True
                    elif op_2 == "FALSE":
                        femtoshell.baseparams["XOR"] = False
                    else:
                        print(
                            colored(f"[!] XOR can only be set to TRUE or FALSE.\n", "red")
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
                    femtoshell.importConfig(op_1)
                else:
                    print(colored(f"[!] File {op_1} doesn't exist.\n", "red"))
                    continue
            else:
                femtoshell.print_help("base")

        elif len(user_in) == 1:
            user_cmd = user_in[0].upper()

            if user_cmd == "EXIT":
                exit()
            elif user_cmd == "BANNER":
                femtoshell.print_banner()
            elif user_cmd == "HELP":
                femtoshell.print_help("base")
            elif user_cmd == "OPTIONS":
                femtoshell.print_options(femtoshell.baseparams)
            elif user_cmd == "READY":
                if femtoshell.baseparams["MODE"] == "SHELL":
                    ready(femtoshell.shellparams)
                elif femtoshell.baseparams["MODE"] == "CMD":
                    ready(femtoshell.cmdparams)
                elif femtoshell.baseparams["MODE"] == "GROUP":
                    if len(parsedConfig) == 0:
                        print(colored("[!] No config loaded.\n", "red"))
                        continue
                    ready(femtoshell.groupparams)
                else:
                    print(colored("[!] No mode set.\n", "red"))
                    femtoshell.print_options(femtoshell.baseparams)
            else:
                femtoshell.print_help("base")
        elif len(user_in) == 0:
            continue
        else:
            femtoshell.print_help("base")


def ready(params):
    while True:
        user_in = prompt(
            f'FEMTOCELL // {femtoshell.baseparams["MODE"]} // ',
            history=FileHistory("history/interact.history"),
            auto_suggest=AutoSuggestFromHistory(),
        ).split()

        if len(user_in) == 1:
            user_cmd = user_in[0].upper()

            if user_cmd == "BACK" or user_cmd == "EXIT":
                return
            elif user_cmd == "BANNER":
                femtoshell.print_banner()
            elif user_cmd == "OPTIONS":
                femtoshell.print_options(params)
            elif user_cmd == "HELP":
                femtoshell.print_help("sub")
            elif femtoshell.baseparams["MODE"] == "GROUP" and user_cmd == "TARGETS":
                if params["GROUP"] == "":
                    print(colored("[!] No GROUP set.\n", "red"))
                    continue
                femtoshell.print_groups()
            elif user_cmd == "EXECUTE":
                if femtoshell.baseparams["MODE"] == "CMD":
                    femtoshell.executeCmd()
                elif femtoshell.baseparams["MODE"] == "SHELL":
                    femtoshell.executeShell()
                elif femtoshell.baseparams["MODE"] == "GROUP":
                    femtoshell.executeGroup()
                    
                else:
                    femtoshell.print_help("sub")
                    continue
            # elif user_cmd == "PING": # under contruction
            #     if femtoshell.baseparams["MODE"] == "CMD" and verify(femtoshell.cmdparams):
            #         plaintext = initPing(femtoshell.cmdparams)
            #         t = multiprocessing.Process(target=pingListen, args=())
            #         t.start()
            #         time.sleep(2)
            #         femtoshell.execute(plaintext, femtoshell.cmdparams)
            #         t.join()
            #     elif femtoshell.baseparams["MODE"] == "GROUP" and verify(femtoshell.groupparams):
            #         if parsedConfig.get(femtoshell.groupparams.get("GROUP")) == "":
            #             continue
            #         groupList = getGroup()
            #         plaintext = initPing(femtoshell.groupparams)
            #         t = multiprocessing.Process(target=pingListen, args=())
            #         t.start()
            #         time.sleep(2)
            #         for iplist in groupList:
            #             for ip in iplist:
            #                 femtoshell.groupparams["RHOST"] = ip
            #                 e = multiprocessing.Process(target=femtoshell.execute, args=(plaintext,femtoshell.groupparams,))
            #                 e.start()
            #         e.join()
            #         t.join()

                # else:
                #     print(colored("[!] PING only works on GROUP or CMD mode.\n", "red"))
                #     continue
            else:
                femtoshell.print_help("sub")
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
                    femtoshell.print_options(params)
                else:
                    femtoshell.print_help("sub")
            else:
                femtoshell.print_help("sub")
        elif len(user_in) > 3:
            user_cmd = user_in[0].upper()
            op_1 = user_in[1].upper()

            if user_cmd == "SET":
                if op_1 == "COMMAND":
                    op_2 = ""
                    for i in range(2, len(user_in)):
                        op_2 = op_2 + user_in[i] + " "
                params[op_1] = op_2.strip(" ")
                femtoshell.print_options(params)
            else:
                femtoshell.print_help("sub")
        elif len(user_in) == 0:
            continue
        else:
            femtoshell.print_help("sub")

