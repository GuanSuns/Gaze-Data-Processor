# utils.py
# -----------------------


def increment_by_int(old_value, increment_value):
    if increment_value is None:
        return old_value
    else:
        return old_value + increment_value


def set_value_by_int(old_value, new_value):
    if new_value is None:
        return old_value
    else:
        return new_value