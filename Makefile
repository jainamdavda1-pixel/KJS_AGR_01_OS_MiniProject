CC=gcc
CFLAGS=-std=c11 -O2 -Wall -Wextra -pedantic
all: bin/orchestrator bin/buffer
bin:
	mkdir -p bin
bin/orchestrator: src/orchestrator.c | bin
	$(CC) $(CFLAGS) $< -o $@
bin/buffer: src/buffer.c | bin
	$(CC) $(CFLAGS) -pthread $< -o $@
clean:
	rm -rf bin outputs/*.csv outputs/*.json outputs/*.txt logs/*.txt logs/*.log
