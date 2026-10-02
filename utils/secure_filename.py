import re
import unicodedata

def secure_filename(filename):
    """Return a safe ASCII filename without requiring Werkzeug."""
    filename = unicodedata.normalize("NFKD", filename).encode(
        "ascii", "ignore"
    ).decode("ascii")
    filename = re.sub(r"[^A-Za-z0-9_.-]", "_", filename)
    return filename.strip("._")