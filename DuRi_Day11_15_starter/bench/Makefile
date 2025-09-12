APP=trace_bench
PKG=github.com/duri/trace_bench/cmd/trace_bench

build:
	go build -ldflags "-s -w -X main.version=$(shell git describe --tags --always 2>/dev/null || echo v0.1.0)" -o bin/$(APP) $(PKG)

clean:
	rm -rf bin

.PHONY: build clean
