// Copyright 2023 Dynatrace LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// Portions of this code, as identified in remarks, are provided under the
// Creative Commons BY-SA 4.0 or the MIT license, and are provided without
// any warranty. In each of the remarks, we have provided attribution to the
// original creators and other attribution parties, along with the title of
// the code (if known) a copyright notice and a link to the license, and a
// statement indicating whether or not we have modified the code.

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
