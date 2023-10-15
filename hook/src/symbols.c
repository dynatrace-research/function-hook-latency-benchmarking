#include "symbols.h"
#include "utils.h"
#include "globals.h"

#include <arpa/inet.h>
#include <dlfcn.h>
#include <stdio.h>


int accept(int sockfd, struct sockaddr* address, socklen_t* addrlen) {
	int newSockfd = ((func_accept_t)dlsym(RTLD_NEXT, "accept"))(sockfd, address, addrlen);

	// Check if the file descriptor relevant and if it should open a IPv4 or IPv6 connection.
	if (sockfd > 2 && sockfd < SOCKET_FD_LIMIT && newSockfd < SOCKET_FD_LIMIT && address != NULL && isIp(address->sa_family)) {
		struct sockaddr_in* address_in = (struct sockaddr_in*)address;
		unsigned short newSockfdPort = htons(address_in->sin_port);

		if (newSockfdPort > 1) {
			// Track file descriptor for later methods.
			globals.socketTracedToPort[newSockfd] = 1;
		}
	}

	return newSockfd;
}

ssize_t read(int fd, void* buf, size_t count) {
	ssize_t bytesRead = ((func_read_t)dlsym(RTLD_NEXT, "read"))(fd, buf, count);

	if (fd > 2 && fd < SOCKET_FD_LIMIT && globals.socketTracedToPort[fd] > 0) {
		if (containsKeyword(buf, count)) {
			// We now can do some action since it contains a keyword.
			// This case don't needs to be reached for our prototype.
			globals.socketTracedToPort[fd] = 2;
		}
	}

	return bytesRead;
}

int close(int fd) {
	if (fd < SOCKET_FD_LIMIT && globals.socketTracedToPort[fd] > 0) {
		globals.socketTracedToPort[fd] = 0;
	}

	return ((func_close_t)dlsym(RTLD_NEXT, "close"))(fd);
}
