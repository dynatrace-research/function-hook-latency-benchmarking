#pragma once

#include <sys/socket.h>
#include <sys/types.h>

#ifndef __USE_GNU
#	define __USE_GNU
#endif

/**
 * Shared library signature.
 */
typedef int (*func_accept_t)(int, struct sockaddr*, socklen_t*);
typedef ssize_t (*func_read_t)(int, void*, size_t);
typedef ssize_t (*func_write_t)(int, const void*, size_t);
typedef int (*func_close_t)(int);


/**
 * Overwritten shared library methods.
 */
int accept(int socket, struct sockaddr* restrict address, socklen_t* restrict address_len);
ssize_t read(int fd, void* buf, size_t count);
ssize_t write(int fd, const void* buf, size_t count);
int close(int fd);
