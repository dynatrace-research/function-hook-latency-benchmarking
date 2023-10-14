CC 			:= gcc
DEV_FLAGS 	:= -Wall -Wno-discarded-qualifiers
CFLAGS 		:= $(DEV_FLAGS) -std=gnu99 -shared -fPIC
LIBS 		:= -ldl

SRC 		:= ./src/
OUT_FOLDER 	:= ./benchmark/system-under-test/

default: $(OUT_FOLDER)ldpreload.so

$(OUT_FOLDER)ldpreload.so: \
						$(SRC)Main.c \
						$(SRC)GlobalVariables.c $(SRC)GlobalVariables.h \
						$(SRC)SharedLibraries.c $(SRC)SharedLibraries.h \
						$(SRC)Utils.c $(SRC)Utils.h 
	$(CC) $(CFLAGS) -o $(OUT_FOLDER)ldpreload.so \
		$(SRC)Main.c \
		$(SRC)SharedLibraries.c \
		$(SRC)Utils.c \
		$(LIBS)

# Global variable set with `export` will be set for the process. I.e. command have to be executed manually in the terminal to be within the scope of the terminal. 
link: 
	printf '-> Please manually execute the following code: \n   export LD_PRELOAD=/workspaces/ld-preload/bin/ldpreload.so\n'
unlink: 
	printf '-> Please manually execute the following code: \n   unset LD_PRELOAD\n'
	
clang:
	find . -type f -iname "*.c" -o -iname "*.h" | xargs clang-format -i

clean:
    # won't remove hidden (e.g., .gitkeep) files
	rm $(OUT_ARCHIVE_FOLDER)*
	rm ./bin/ldpreload.so
