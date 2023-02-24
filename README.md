# femtocell
This was supposed to be a "Modular C2 Framework"
Now it's not.
It's way cooler now though. Trust me.

## Implant
### Building
You must have mingw-w64 installed in order to compile this. Run the 
```sh
make # compile exe and dll
make debug # compile debug versions of exe and dll
```
The debug version contains print statements and all data is sent in plaintext.

Make sure your binary runs with administrator privileges, or it will fail.
## Usage
### CLI
### Unix
```sh
cd cli/
pip3 install -r requirements.txt
sudo ./femtoshell.py
```
### Windows
```ps1
cd .\cli
pip3 install -r requirements.txt
python femtoshell.py # running as admin
```
### CLI Interaction with Implants
```
usage: femtoshell.py [-h] [-m [MODE]] [-t [TARGET]] [-l [LISTEN]] [-p [PORT]] [-c COMMAND [COMMAND ...]] [-r [TRANSPORT]] [-f [FILE]] [-g [GROUP]] [--ping [PING]] [--pwnboard [PWNBOARD]] [--debug]

Interact with a femtocell agent via CLI arguments or interactively. Run with no arguments to start interactive prompt.

optional arguments:
  -h, --help            show this help message and exit
  -m [MODE], --mode [MODE]
                        Set the targeting mode. Options: <shell>/<cmd>/<group>. Default: Shell
  -t [TARGET], --target [TARGET]
                        Target machine running the femtocell agent. Required if using <shell>/<cmd> mode.
  -l [LISTEN], --listen [LISTEN]
                        IP that is listening for a callback shell. This IP must be reachable from the target machine. Required if using <shell> mode.
  -p [PORT], --port [PORT]
                        Port open on target. Default: 445.
  -c COMMAND [COMMAND ...], --command COMMAND [COMMAND ...]
                        Run a single command. No output given. Required if using <cmd>/<group> mode.
  -r [TRANSPORT], --transport [TRANSPORT]
                        Transport protocol to use. Options: <tcp>/<udp>/<icmp>. Default: TCP.
  -f [FILE], --file [FILE]
                        Configuration file to load. Required if using <group> mode.
  -g [GROUP], --group [GROUP]
                        Set of targets specified in configuration file. Required if using <group> mode.
  --ping [PING]         Ethernet interface to listen on for ping callbacks. Only relevant to <cmd>/<group> mode.
  --pwnboard [PWNBOARD]
                        Link for pwnboard callback support.
  --debug               Debug mode. Disables initial packet encryption. For testing only.
```
### Interacting with Implants
There are three main modes of interaction: 
- `shell` - interactive command prompt
- `cmd` - no-output command execution on a single target
- `group` - no-output command execution on a number of targets
### Base Prompt

The base prompt is used to set the primary actions.  

Use `options` to see current set values.
```
FEMTOCELL // options
MODE: 
FILE: 
XOR: True
```
Use `load` to load a configuration file. This file must be syntactically correct.
```
FEMTOCELL // load test.yml
[+] Config test.yml loaded. MODE set to GROUP.
```
Use the `set` command to set values.
```
FEMTOCELL // set mode shell
[*] Mode SHELL set.
```
Enter `ready` to move on.
### Ready Prompt
Use `options` again to see what values can be modified. Any blank values are required.
```
FEMTOCELL // SHELL // options
RHOST: 
RPORT: 445
LHOST: 
LPORT: 443
TRANSPORT: TCP
```
There are three transports available: `TCP`, `UDP`, and `ICMP`. Change any modifiers with the `set` command.
```
FEMTOCELL // SHELL // set transport icmp
RHOST: 
RPORT: 445
LHOST: 
LPORT: 443
TRANSPORT: ICMP
```
Once all values are set, use `execute` to run your command.

Type `back` or `exit` to return to the base prompt.

### Ping Mode
If attempting to ping an implant, you must be in the `cmd` or `group` modes. Use `set iface <iface>` to set the listening interface for callbacks.