"""
utils/helpers.py — CLI Formatting & Input Validation Helpers

Shared utilities used across main.py and sub-menus to keep
the CLI output clean and consistent.
"""


def print_header(title: str):
    """Print a boxed section header.

    Example:
        ╔════════════════════════╗
        ║   Product Management   ║
        ╚════════════════════════╝
    """
    length = len(title) + 6
    top = "╔" + "═" * length + "╗"
    middle = f"║   {title}   ║"
    bottom = "╚" + "═" * length + "╝"
    print(f"\n{top}\n{middle}\n{bottom}\n")


def get_nested_val(d: dict, path: str):
    """Retrieve nested value using dot notation, e.g., 'attributes.color'."""
    parts = path.split('.')
    val = d
    for part in parts:
        if isinstance(val, dict):
            val = val.get(part)
        else:
            return None
    return val


def print_table(rows: list[dict], columns: list[str], headers: list[str] = None):
    """Print a list of dicts as a formatted CLI table.

    Args:
        rows:    list of dicts (each dict = one row).
        columns: list of keys to display as columns (supports dot notation).
        headers: optional custom display headers for columns.
    """
    if not rows:
        print("  (No data to display)")
        return

    if not headers:
        headers = columns

    # Pre-calculate widths
    col_widths = {col: len(head) for col, head in zip(columns, headers)}
    for row in rows:
        for col in columns:
            val = get_nested_val(row, col)
            val_str = str(val) if val is not None else ""
            col_widths[col] = max(col_widths[col], len(val_str))

    # Format header line
    header_line = " | ".join(head.ljust(col_widths[col]) for col, head in zip(columns, headers))
    print("  " + header_line)
    
    # Format divider
    divider = "-+-".join("-" * col_widths[col] for col in columns)
    print("  " + divider)

    # Format rows
    for row in rows:
        row_str = " | ".join((str(get_nested_val(row, col)) if get_nested_val(row, col) is not None else "").ljust(col_widths[col]) for col in columns)
        print("  " + row_str)
    print()


def input_int(prompt: str, default: int = None) -> int:
    """Prompt the user for an integer, with optional default."""
    while True:
        suffix = f" [{default}]" if default is not None else ""
        val = input(f"{prompt}{suffix}: ").strip()
        if not val and default is not None:
            return default
        try:
            return int(val)
        except ValueError:
            print("  ✗ Invalid input. Please enter a valid integer.")


def input_float(prompt: str, default: float = None) -> float:
    """Prompt the user for a float, with optional default."""
    while True:
        suffix = f" [{default}]" if default is not None else ""
        val = input(f"{prompt}{suffix}: ").strip()
        if not val and default is not None:
            return default
        try:
            return float(val)
        except ValueError:
            print("  ✗ Invalid input. Please enter a valid decimal number.")


def confirm(prompt: str) -> bool:
    """Ask yes/no confirmation, returns True for 'y'."""
    while True:
        val = input(f"{prompt} (y/n): ").strip().lower()
        if val in ('y', 'yes'):
            return True
        if val in ('n', 'no'):
            return False
        print("  ✗ Invalid input. Please enter 'y' or 'n'.")

