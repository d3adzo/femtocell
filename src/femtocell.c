#include "femtocell.h"

struct sockaddr_in* GetIP() {
	SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	struct sockaddr_in remoteaddr = { 0 };
	remoteaddr.sin_family = AF_INET;
	remoteaddr.sin_addr.s_addr = inet_addr("8.8.8.8");
	remoteaddr.sin_port = htons(53);
	struct sockaddr_in localaddr = { 0 };
	struct sockaddr_in* ret = (struct sockaddr_in*)malloc(sizeof(struct sockaddr_in));

	if (connect(sock, (struct sockaddr*)&remoteaddr, sizeof(remoteaddr)) == 0 && ret != 0)
	{
		int len = sizeof(localaddr);
		getsockname(sock, (struct sockaddr*)&localaddr, &len);
		memcpy(ret, &localaddr, len);
	}
	closesocket(sock);
	return ret;
}


int main(int argc, char** argv)
{
	WSADATA wsaData;
	if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
		exit(-1);

	SOCKET sd = socket(AF_INET, SOCK_RAW, IPPROTO_IP);
	if (sd == INVALID_SOCKET) 
	{
#ifdef _DEBUG
		fprintf(stderr, "socket() failed: %u", WSAGetLastError());
#endif
		exit(-1);
	}

	struct sockaddr_in* localaddr = GetIP();

	struct sockaddr_in addr;
	addr.sin_family = AF_INET;
	addr.sin_addr = localaddr->sin_addr;
	addr.sin_port = htons(0);

	int rc = bind(sd, (struct sockaddr*)&addr, sizeof(addr));
	if (rc == SOCKET_ERROR) 
	{
#ifdef _DEBUG
		fprintf(stderr, "bind() failed: %u", WSAGetLastError());
#endif
		exit(-1);
	}

	int value = RCVALL_IPLEVEL;
	DWORD out = 0;
	rc = WSAIoctl(sd, SIO_RCVALL, &value, sizeof(value), NULL, 0, &out, NULL, NULL);
	if (rc == SOCKET_ERROR) 
	{
#ifdef _DEBUG
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
#ifdef _DEBUG
			fprintf(stderr, "recv() failed: %u", WSAGetLastError());
#endif
			exit(-1);
		}

		struct ip_hdr_s* ip_header = (struct ip_hdr_s*)(buffer+BUFFER_OFFSET_IP);
		uint8_t l4_protocol = ip_header->ip_p;
		switch (l4_protocol)
		{
			case IPPROTO_ICMP:
				handleICMP(buffer, ip_header);
				break;
			case IPPROTO_TCP:
				handleTCP(buffer, ip_header);
				break;
			case IPPROTO_UDP:
				handleUDP(buffer, ip_header);
				break;
			default:
				break;
		}
	}
	return 0;
}