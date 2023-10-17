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

#define LOG_FILE "/var/log/readhook.log" /* absolute path to logfile holding debug information */
#define MAX_SOCKET_FD 1000               /* highest possible socket fd, since our map is limited in size */
#define WORD_LIST_LENGTH 200             /* number of words in the word list */

#define SOCKET_FD_UNTRACEABLE 0           /* no ip socket or not seen yet */
#define SOCKET_FD_TRACEABLE 1             /* is ip socket */
#define SOCKET_FD_TRACEABLE_AND_BLOCKED 2 /* is ip socket and some content was already blocked */

/**
 * @brief Tracks if some socket file descriptor needs to be hooked in the next read call.
 * For better performance this should be a hashmap instead of an array in the future.
 */
extern unsigned char SOCKET_PORT_MAPPING[MAX_SOCKET_FD];

/**
 * @brief Holds a list of disallowed words that shall not be contained in any read call.
 */
extern const char* WORD_LIST[WORD_LIST_LENGTH];
