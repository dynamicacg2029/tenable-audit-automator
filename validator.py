import re

def validate_regex(pattern):
    """Checks if a string is a valid PCRE pattern for Tenable."""
    if not pattern:
        return False, "Pattern is empty"
    try:
        re.compile(pattern)
        # Check for Tenable-specific requirement: double backslashes in Windows
        if "\\" in pattern and "\\\\" not in pattern:
            return False, "Windows paths require double backslashes (\\\\)"
        return True, None
    except re.error as e:
        return False, str(e)
