"""Build two local-only WordPress practice packages using the Python standard library."""
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile

plugin_source = """<?php
/*
Plugin Name: Field Guide Practice
Version: VERSION_NUMBER
*/

add_shortcode('field_guide_marker', static function () {
    return 'field-guide-VERSION_NUMBER';
});
"""

output = Path(mkdtemp(prefix="wp-guide-packages-"))
for version in ("1.0.0", "2.0.0"):
    package = output / f"field-guide-practice-{version}.zip"
    with ZipFile(package, "x") as archive:
        archive.writestr(
            "field-guide-practice/field-guide-practice.php",
            plugin_source.replace("VERSION_NUMBER", version),
        )

print(output)
