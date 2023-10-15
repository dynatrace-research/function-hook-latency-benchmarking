#pragma once

#include <stdbool.h>
#include <sys/types.h>

/**
 * @brief Tests if the buffer contains a disallowed keyword from the WORD_LIST.
 */
bool contains_keyword(void* buf, size_t count);

/**
 * @brief Tests if the file descriptor is a socket that should be traced in read.
 */
bool is_http_socket(int fd);

/**
 * @brief Logs the given format string to the LOG_FILE.
 */
void write_log(const char* format, ...);
