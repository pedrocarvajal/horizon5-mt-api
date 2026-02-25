CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -I.
SRC = $(shell find . -name '*.cpp' ! -path './libraries/*' ! -path './dist/*' ! -path './scripts/*')
DIST = dist
OUT = $(DIST)/index

ifeq ($(DEBUG),1)
	CXXFLAGS += -g -DDEBUG
else
	CXXFLAGS += -O2
endif

compile:
	@mkdir -p $(DIST)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(OUT)

run: compile
	./$(OUT)

clean:
	rm -rf $(DIST)

lint:
ifeq ($(SRC),)
	@echo "No source files to lint"
else
	@cppcheck --enable=all --std=c++17 --suppress=missingIncludeSystem -I. $(SRC) 2>&1
endif

format:
	@echo "Formatting files..."
	@find . -type f \( -name '*.cpp' -o -name '*.hpp' -o -name '*.h' -o -name '*.c' \) ! -path './dist/*' ! -path './libraries/*' | while read file; do \
		echo "  $$file"; \
		uncrustify -c uncrustify.cfg --replace --no-backup "$$file"; \
	done
	@echo "Done"

.PHONY: compile run clean lint format
