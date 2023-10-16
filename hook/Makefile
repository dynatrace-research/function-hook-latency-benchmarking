CC 			:= gcc
DEV_FLAGS 	:= -Wall -Wno-discarded-qualifiers
CFLAGS 		:= $(DEV_FLAGS) -std=gnu99 -shared -fPIC
LIBS 		:= -ldl

SRC 		:= ./src
OUT 		:= ./out

default: $(OUT)/readhook.so

$(OUT)/readhook.so: \
		$(SRC)/main.c $(SRC)/main.h \
		$(SRC)/hook.c $(SRC)/hook.h \
		$(SRC)/utils.c $(SRC)/utils.h
	$(CC) $(CFLAGS) -o $(OUT)/readhook.so \
		$(SRC)/main.c $(SRC)/hook.c $(SRC)/utils.c \
		$(LIBS)

clean:
	rm $(OUT)/readhook.so

format:
	find . -type f -iname "*.c" -o -iname "*.h" | xargs clang-format -i
