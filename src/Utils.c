
#include "Utils.h"
#include "GlobalVariables.h"

#include <string.h>
#include <stdio.h>
#include <stdarg.h>

void simpleLogger(const char* format, ...) {

	FILE* logFile = fopen(LOG_FILE, "a");

	if (logFile == NULL) {
		fprintf(stderr,
				"!-- Process is running with LD_PRELOAD, but won't produce any logs. Reason: No permission to generate a log file \"%s\"!\n",
				LOG_FILE);
		return;
	}

	va_list args;

	va_start(args, format);
	vfprintf(logFile, format, args);
	va_end(args);

	fclose(logFile);
}

char* strnstr(char* haystack, const char* needle, int nHaystack) {
	char* needleInHaystack = strstr(haystack, needle);

	if (needleInHaystack == NULL || (needleInHaystack - haystack) < 0 || (needleInHaystack - haystack) > nHaystack) {
		return NULL;
	}

	return needleInHaystack;
}

bool strToBool(const char* stringToConvert) {
	char* TRUE_VALUES[] = {"y", "yes", "true", "on"};
	const int NUM_TRUE_VALUES = 4;

	for (int i = 0; i < NUM_TRUE_VALUES; i++) {
		if (strcasecmp(stringToConvert, TRUE_VALUES[i]) == 0) {
			return true;
		}
	}
	return false;
}

bool isIp(sa_family_t sockFamily) {
	return sockFamily == AF_INET || sockFamily == AF_INET6;
}

bool containsKeyword (void* buf, size_t count) {
	bool keywordContained = false;

	for(int i = 0; i < WORD_LIST_LENGTH && keywordContained == false;i++) {
		if (strstr(buf, globals.wordList[i]) != NULL) {
			simpleLogger("Match with word-list was found! The word is \"%s\".\n", globals.wordList[i]);
			keywordContained = true;
		}
	}

	return keywordContained;
}
