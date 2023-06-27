#include "femtocell.h"

// UuidCreate(&id);

#ifdef DLL
__declspec(dllexport) int function()
#else
int main()
#endif
{
	WSADATA wsaData;
	if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
		exit(-1);

	SOCKET sd = socket(AF_INET, SOCK_RAW, IPPROTO_IP);
	if (sd == INVALID_SOCKET)
	{
#ifdef DEBUG
		fprintf(stderr, "socket() failed: %u", WSAGetLastError());
#endif
		exit(-1);
	}

	localaddr = getIP();

	struct sockaddr_in addr;
	addr.sin_family = AF_INET;
	addr.sin_addr = localaddr->sin_addr;
	addr.sin_port = htons(0);

	int rc = bind(sd, (struct sockaddr*)&addr, sizeof(addr));
	if (rc == SOCKET_ERROR)
	{
#ifdef DEBUG
		fprintf(stderr, "bind() failed: %u", WSAGetLastError());
#endif
		exit(-1);
	}

	int value = RCVALL_IPLEVEL;
	DWORD out = 0;
	rc = WSAIoctl(sd, SIO_RCVALL, &value, sizeof(value), NULL, 0, &out, NULL, NULL);
	if (rc == SOCKET_ERROR)
	{
#ifdef DEBUG
		fprintf(stderr, "WSAIoctl() failed: %u", WSAGetLastError());
#endif
		exit(-1);
	}

	unsigned char buffer[BUFFER_SIZE_ETH + BUFFER_SIZE_PKT];
	memset(buffer, 0, sizeof(buffer));
	buffer[BUFFER_OFFSET_ETH + 12] = 0x08;

	while (1)
	{
		int rc = recv(sd, (char*)buffer + BUFFER_OFFSET_IP, BUFFER_SIZE_IP, 0);
		if (rc == SOCKET_ERROR)
		{
#ifdef DEBUG
			fprintf(stderr, "recv() failed: %u", WSAGetLastError());
#endif
			exit(-1);
		}

		struct ip_hdr_s* ip_header = (struct ip_hdr_s*)(buffer + BUFFER_OFFSET_IP);
		uint8_t l4_protocol = ip_header->ip_p;
		switch (l4_protocol)
		{
		case IPPROTO_ICMP:
			handleICMP(buffer, ip_header, localaddr);
			break;
		case IPPROTO_TCP:
			handleTCP(buffer, ip_header, localaddr);
			break;
		case IPPROTO_UDP:
			handleUDP(buffer, ip_header, localaddr);
			break;
		default:
			break;
		}
	}
	return 0;
}

#ifdef DLL
__declspec(dllexport)
BOOL WINAPI DllMain(
	HINSTANCE hinstDLL,  // handle to DLL module
	DWORD fdwReason,     // reason for calling function
	LPVOID lpvReserved)  // reserved
{
	// Perform actions based on the reason for calling.
	switch (fdwReason)
	{
	case DLL_PROCESS_ATTACH:
		// Initialize once for each new process.
		// Return FALSE to fail DLL load.
		   //function();
		CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)&function, NULL, 0, NULL);
		break;

	case DLL_THREAD_ATTACH:
		// Do thread-specific initialization.
		break;

	case DLL_THREAD_DETACH:
		// Do thread-specific cleanup.
		break;

	case DLL_PROCESS_DETACH:

		if (lpvReserved != NULL)
		{
			break; // do not do cleanup if process termination scenario
		}

		// Perform any necessary cleanup.
		break;
	}
	return TRUE;  // Successful DLL_PROCESS_ATTACH.
}
#endif
