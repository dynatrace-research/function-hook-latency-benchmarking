#pragma once

#include <sys/socket.h>
#include <sys/types.h>

#ifndef __USE_GNU
#    define __USE_GNU
#endif

typedef int (*accept_t)(int, struct sockaddr*, socklen_t*);
typedef ssize_t (*read_t)(int, void*, size_t);
typedef int (*close_t)(int);

/**
 * @brief Accept a connection on a socket (https://man7.org/linux/man-pages/man2/accept.2.html).
 * We will hook this function to check if the file descriptor is an ip socket.
 */
int accept(int sockfd, struct sockaddr* addr, socklen_t* addrlen);

/**
 * @brief Read from a file descriptor (https://man7.org/linux/man-pages/man2/read.2.html).
 * We will hook this function to check if the read buffer contains a disallowed keyword.
 */
ssize_t read(int fd, void* buf, size_t count);

/**
 * @brief Close a file descriptor (https://man7.org/linux/man-pages/man2/close.2.html).
 * We will hook this function to remove the file descriptor from our tracking array.
 */
int close(int fd);
