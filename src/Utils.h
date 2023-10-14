#pragma once

#include <sys/socket.h>
#include <stdbool.h>

/**
 * Log the @format to the LOG_FILE
 */
void simpleLogger(const char* format, ...);

/**
 * Look if the @needle exists in the first @nHaystack chars within the @haystack.
 * For example the HTTP version attribute(@needle) is only valid within the first
 * line (given by @nHaystack) of the HTTP header buffer (@haystack), because the
 * occurrence in lines below could be just a text or header property.
 */
char* strnstr(char* haystack, const char* needle, int nHaystack);

bool strToBool(const char* stringToConvert);

/**
 * Check if the flag is IPv4 or IPv6 flag.
 */
bool isIp(sa_family_t sockFamily);

bool containsKeyword (void* buf, size_t count);