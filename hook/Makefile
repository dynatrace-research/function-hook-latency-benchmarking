CC 			:= gcc
DEV_FLAGS 	:= -Wall -Wno-discarded-qualifiers
CFLAGS 		:= $(DEV_FLAGS) -std=gnu99 -shared -fPIC
LIBS 		:= -ldl

SRC 		:= ./src/
OUT_FOLDER 	:= ../benchmark/system-under-test/

default: $(OUT_FOLDER)ldpreload.so

$(OUT_FOLDER)ldpreload.so: \
						$(SRC)main.c \
						$(SRC)globals.c $(SRC)globals.h \
						$(SRC)symbols.c $(SRC)symbols.h \
						$(SRC)utils.c $(SRC)utils.h
	$(CC) $(CFLAGS) -o $(OUT_FOLDER)ldpreload.so \
		$(SRC)main.c \
		$(SRC)symbols.c \
		$(SRC)utils.c \
		$(LIBS)

clang:
	find ./hook -type f -iname "*.c" -o -iname "*.h" | xargs clang-format -i

clean:
    # won't remove hidden (e.g., .gitkeep) files
	rm $(OUT_ARCHIVE_FOLDER)*
	rm ./bin/ldpreload.so
