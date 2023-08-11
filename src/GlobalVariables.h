#pragma once

/**
 * LOG_FILE need to be a absolute path since the relative path depends on Shared-Libary execution folder which could be vary.
 * The folder (in that case /var/log) also have to exists, since the hole system will crash otherwise.
 */
// #define LOG_FILE "/var/log/ldpreload.log"
#define LOG_FILE "/var/log/ldpreload.log"

/**
 * Limit of socketFd value that will be traced at most. Currently limits memory allocation and will be unnecessary (or at least be
 * renamed) with a hashmap implementation instead of an array.
 */
#define SOCKET_FD_LIMIT 1000

#define WORD_LIST_LENGTH 200

/**
 * Structure Globals define all global variable that are available within the Agent.
 */
typedef struct {
	/**
	 * Boolean array of socketFd that are TCP connections.
	 */
	unsigned short socketTracedToPort[SOCKET_FD_LIMIT];
	char* wordList[WORD_LIST_LENGTH];
} Globals;

/**
 * Actual global values are defined within GlobalVariables.c
 */
extern Globals globals;