# DuRi Development Guidelines

## 🚫 Module Naming Restrictions

### Critical: Avoid Standard Library Shadowing

**NEVER** create files or directories with these names that could shadow Python's standard library:

- `logging.py` / `logging/` → Use `log_utils.py`, `logger.py`, or `log_helpers.py`
- `json.py` / `json/` → Use `json_utils.py`, `json_helpers.py`
- `os.py` / `os/` → Use `os_utils.py`, `system_utils.py`
- `sys.py` / `sys/` → Use `sys_utils.py`, `system_utils.py`
- `time.py` / `time/` → Use `time_utils.py`, `time_helpers.py`
- `datetime.py` / `datetime/` → Use `datetime_utils.py`, `date_helpers.py`

### Why This Matters

Creating files with standard library names causes **module shadowing**, where:
1. Python imports your local file instead of the standard library
2. Third-party libraries expect standard library behavior
3. Results in `AttributeError` and other runtime failures

### Examples

❌ **BAD:**
```python
# duri_common/logging.py
def get_logger():
    pass
```

✅ **GOOD:**
```python
# duri_common/log_utils.py
def get_logger():
    pass

# duri_common/__init__.py
from .log_utils import get_logger
```

## 🔍 Pre-commit Checks

Our CI automatically checks for:
- Files named `logging.py`
- Directories named `logging`
- Standard library module availability

## 🧪 Testing

Run the logging shadowing tests:
```bash
python -m pytest tests/test_logging_shadowing.py -v
```

## 📝 PR Template

When creating PRs, ensure:
- [ ] No new `logging.py` files created
- [ ] No new `logging/` directories created
- [ ] All logging tests pass
- [ ] Dockerfile guards are in place for stdlib verification
