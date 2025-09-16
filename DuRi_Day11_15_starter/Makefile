AS_OF_DAY ?= 36
VAR ?= A
SEED ?= 42
CONFIG ?= configs/day36.yaml
PYTHONPATH := $(PWD)

.PHONY: run clean test gateA gateB day36 day37 day38 day39 gate

run:
	@echo "Running day $(AS_OF_DAY) VAR $(VAR) SEED $(SEED)"
	PYTHONPATH=$(PYTHONPATH) python -m src.pipeline.run --day $(AS_OF_DAY) --variant $(VAR) --seed $(SEED) --config $(CONFIG)

clean:
	rm -rf .cache .pytest_cache
	find outputs -mindepth 1 -maxdepth 1 ! -name '.gitkeep' -exec rm -rf {} +

test:
	pytest -q

gateA:
	python scripts/promotion_gate.py outputs/day36/var_A/results.json policies/promotion.yaml

gateB:
	python scripts/promotion_gate.py outputs/day36/var_B/results.json policies/promotion.yaml

day36:
	$(MAKE) run AS_OF_DAY=36 VAR=A SEED=42 && \
	$(MAKE) run AS_OF_DAY=36 VAR=B SEED=42

day37:
	$(MAKE) run AS_OF_DAY=37 VAR=A SEED=42 CONFIG=configs/day37.yaml && \
	$(MAKE) run AS_OF_DAY=37 VAR=B SEED=42 CONFIG=configs/day37.yaml

day38:
	$(MAKE) run AS_OF_DAY=38 VAR=A SEED=42 CONFIG=configs/day38.yaml && \
	$(MAKE) run AS_OF_DAY=38 VAR=B SEED=42 CONFIG=configs/day38.yaml

day39:
	$(MAKE) run AS_OF_DAY=39 VAR=A SEED=42 CONFIG=configs/day39.yaml && \
	$(MAKE) run AS_OF_DAY=39 VAR=B SEED=42 CONFIG=configs/day39.yaml

gate:
	python scripts/promotion_gate.py outputs/day$(DAY)/var_A/results.json policies/promotion.yaml || true
	python scripts/promotion_gate.py outputs/day$(DAY)/var_B/results.json policies/promotion.yaml || true
