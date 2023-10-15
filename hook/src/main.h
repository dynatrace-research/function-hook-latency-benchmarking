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
