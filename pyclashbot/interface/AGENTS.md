# interface/ — ttkbootstrap GUI

`ui.py` (`PyClashBotUI`) is a tabbed window that never talks to the worker directly: on any change it calls a `config_callback` (registered in `__main__.py`) with `get_all_values()` — a dict keyed by `UIField.value` strings. `__main__.py` persists that to `USER_SETTINGS_CACHE` and maps it to the worker config. `enums.py` names every field (`UIField`, `PRIMARY_JOB_TOGGLES`); `config.py` holds defaults/option lists; `widgets.py` holds custom widgets.

## Adding a setting / toggle / job

Wire the **same key string** across three files or it won't round-trip:
1. `enums.py` — add a `UIField` member (snake_case value).
2. `config.py` — add to the right list (`JOBS`, `MEMU_SETTINGS`, etc.) and to the persisted-keys set.
3. `ui.py` — create the widget in the relevant `_create_*_tab()`, register it, and handle it in `get_all_values()`/`set_all_values()` and `set_button_state()` (the run-time disable list is manual, not auto-discovered).

## Gotchas

- UI keys ≠ worker keys: `__main__.py.make_job_dictionary()` renames some (e.g. `card_upgrade_user_toggle` → `upgrade_user_toggle`) and is where late int-parsing/validation happens.
- The single emulator combobox expands to **four** boolean `UIField` toggles in get/set — edit all four together.
- Bulk updates (`set_all_values`) must bump `_suspend_traces` in try/finally to avoid recursive trace callbacks; Google Play comboboxes silently reset invalid persisted values to the first option.
