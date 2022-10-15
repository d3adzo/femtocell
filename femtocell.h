#pragma once

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <winsock2.h>
#include <mstcpip.h>
#include <iphlpapi.h>

#pragma comment(lib, "ws2_32.lib")


struct tcp_hdr_s {
	unsigned short int 	th_sport;
	unsigned short int 	th_dport;
	unsigned int 		th_seq;
	unsigned int 		th_ack;
	unsigned char 		th_x2 : 4, th_off : 4;
	unsigned char 		th_flags;
	unsigned short int 	th_win;
	unsigned short int 	th_sum;
	unsigned short int 	th_urp;
} tcp_hdr_t;


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
} ip_hdr_t;


#define BUFFER_SIZE_PKT ((256*256) - 1)
#define BUFFER_SIZE_ETH 14
#define BUFFER_SIZE_IP (BUFFER_SIZE_PKT - BUFFER_SIZE_ETH)
#define BUFFER_SIZE_TCP sizeof(struct tcp_hdr_s)

#define BUFFER_OFFSET_ETH 16
#define BUFFER_OFFSET_IP (BUFFER_OFFSET_ETH + BUFFER_SIZE_ETH)
#define BUFFER_OFFSET_L4 ( BUFFER_OFFSET_IP + sizeof(struct ip_hdr_s) )
#define BUFFER_OFFSET_DATA ( BUFFER_OFFSET_L4 + sizeof(struct tcp_hdr_s) )
