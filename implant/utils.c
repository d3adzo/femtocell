#include "femtocell.h"

void XORCipher(char* data, int key, int dataLen) 
{
	for (int i = 0; i < dataLen; ++i) {
		data[i] = data[i] ^ key;
	}
}


struct sockaddr_in* getIP() 
{
	SOCKADDR_IN adress;
	SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	struct sockaddr_in remoteaddr = { 0 };
	remoteaddr.sin_family = AF_INET;
	remoteaddr.sin_addr.s_addr = inet_addr("8.8.8.8");
	remoteaddr.sin_port = htons(53);
	struct sockaddr_in ladder = { 0 };
	struct sockaddr_in* ret = (struct sockaddr_in*)malloc(sizeof(struct sockaddr_in));

	if (connect(sock, (struct sockaddr*)&remoteaddr, sizeof(remoteaddr)) == 0)
	{
		int len = sizeof(ladder);
		getsockname(sock, (struct sockaddr*)&ladder, &len);
		memcpy(ret, &ladder, len);
	}
	closesocket(sock);
	return ret;
}