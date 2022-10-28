CC = x86_64-w64-mingw32
CFLAGS = -static -lws2_32
OUTDIR = bin
MKDIR = mkdir -p bin
SF := $(wildcard *.c)
RC = $(OUTDIR)/resource.o

all: clean resource exe dll

debug: clean exe-debug dll-debug

resource:
	$(CC)-windres resource.rc -o {RC}

exe:
	$(CC)-gcc $(SF) $(RC) $(CFLAGS) -o $(OUTDIR)/femtocell.exe

exe-debug:
	$(CC)-gcc $(SF) $(CFLAGS) -D DEBUG -o $(OUTDIR)/femtocell-debug.exe

dll:
	$(CC)-gcc $(SF) $(RC) $(CFLAGS) -D DLL -shared -o $(OUTDIR)/femtocell.dll

dll-debug:
	$(CC)-gcc $(SF) $(CFLAGS) -D DLL -D DEBUG -shared -o $(OUTDIR)/femtocell-debug.dll

clean:
	$(MKDIR)
	rm -f $(OUTDIR)/*
