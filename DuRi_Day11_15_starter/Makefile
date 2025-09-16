AS_OF_DAY ?= 36
VAR ?= A
SEED ?= 42
CONFIG ?= configs/day36.yaml
PYTHONPATH := $(PWD)

.PHONY: run clean

run:
	@echo "Running day $(AS_OF_DAY) VAR $(VAR) SEED $(SEED)"
	PYTHONPATH=$(PYTHONPATH) python -m src.pipeline.run --day $(AS_OF_DAY) --variant $(VAR) --seed $(SEED) --config $(CONFIG)

clean:
	rm -rf .cache .pytest_cache
	find outputs -mindepth 1 -maxdepth 1 ! -name '.gitkeep' -exec rm -rf {} +
