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
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
sudo ./femtoshell 
```
### Windows
```ps1
cd .\cli
python -m venv venv
.\venv\scripts\activate
pip3 install -r requirements.txt
python femtoshell # running as admin
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
