#include "utils.h"
#include "main.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

bool is_http_socket(int fd) {
    return fd > 2 && fd < MAX_SOCKET_FD && SOCKET_PORT_MAPPING[fd] > 0;
}

bool contains_keyword(void* buf, size_t count) {
    for (int i = 0; i < WORD_LIST_LENGTH; i++) {
        if (strstr(buf, WORD_LIST[i]) != NULL) {
            write_log("buffer matches word '%s' from the word list\n", WORD_LIST[i]);
            return true;
        }
    }

    return false;
}

void write_log(const char* format, ...) {
    FILE* file = fopen(LOG_FILE, "a");
    if (file == NULL) {
        fprintf(stderr, "Could not open log file \"%s\"\n", LOG_FILE);
        return;
    }

    va_list args;
    va_start(args, format);
    vfprintf(file, format, args);
    va_end(args);

    fclose(file);
}
