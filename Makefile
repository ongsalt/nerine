compile:
	swift build -c release -Xswiftc -g

compile_unchecked:
	swift build -c release -Xswiftc -g -Xswiftc -Ounchecked

bench: compile
	perf record -o perf/sparse-strip.data --call-graph dwarf .build/release/strip102 tiger.svg --bench --fill sparse-strip
	perf record -o perf/banded.data --call-graph dwarf .build/release/strip102 tiger.svg --bench --fill banded-scanline
	perf record -o perf/scanline.data --call-graph dwarf .build/release/strip102 tiger.svg --bench

bench_st_nc: compile
	perf record -o perf/sparse-strip.data --call-graph dwarf .build/release/strip102 tiger.svg --bench --fill sparse-strip --threads 1 --no-cache
