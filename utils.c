#include "femtocell.h"

void XORCipher(char* data, char* key, int dataLen) {
	for (int i = 0; i < dataLen; ++i) {
		data[i] = data[i] ^ key[i];
	}
}


struct sockaddr_in* GetIP() 
{
	SOCKADDR_IN adress;
	SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	struct sockaddr_in remoteaddr = { 0 };
	remoteaddr.sin_family = AF_INET;
	remoteaddr.sin_addr.s_addr = inet_addr("8.8.8.8");
	remoteaddr.sin_port = htons(53);
	struct sockaddr_in localaddr = { 0 };
	struct sockaddr_in* ret = (struct sockaddr_in*)malloc(sizeof(struct sockaddr_in));

	if (connect(sock, (struct sockaddr*)&remoteaddr, sizeof(remoteaddr)) == 0)
	{
		int len = sizeof(localaddr);
		getsockname(sock, (struct sockaddr*)&localaddr, &len);
		memcpy(ret, &localaddr, len);
	}
	closesocket(sock);
	return ret;
}