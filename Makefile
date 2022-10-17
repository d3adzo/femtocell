CC = x86_64-w64-mingw32-gcc
CFLAGS = -lws2_32
OUTDIR = bin
MKDIR = mkdir -p bin
SF := $(wildcard *.c)

all: clean exe dll

debug: clean exe-debug dll-debug

exe:
	$(CC) $(SF) $(CFLAGS) -o $(OUTDIR)/femtocell.exe

exe-debug:
	$(CC) $(SF) $(CFLAGS) -D DEBUG -o $(OUTDIR)/femtocell-debug.exe

dll:
	$(CC) $(SF) $(CFLAGS) -D DLL -shared -o $(OUTDIR)/femtocell.dll

dll-debug:
	$(CC) $(SF) $(CFLAGS) -D DLL -D DEBUG -shared -o $(OUTDIR)/femtocell-debug.dll

clean:
	$(MKDIR)
	rm -f $(OUTDIR)/*
