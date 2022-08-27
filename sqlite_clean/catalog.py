"""
sqlite-clean catalog - intended to be used for cataloging various linting and
fixing operations found within this repo.
"""
from .fix import clean_like_nulls
from .lint import contains_conflicting_aff_storage_class, contains_str_like_null

SQLITE_CLEAN_CATALOG = {
    "lint": [
        {
            "id": "L0001",
            "desc": (
                "Contains conflicting column affinity type vs column data storage class."
                " See https://www.sqlite.org/datatype3.html for more information"
            ),
            "ref": contains_conflicting_aff_storage_class,
        },
        {
            "id": "L0002",
            "desc": (
                "Contains string data storage class values which appear to be"
                "null-like values. Consider using SQLite NULL values instead."
            ),
            "ref": contains_str_like_null,
        },
    ],
    "fix": [
        {
            "id": "F0001",
            "desc": (
                "Updated string values which appeared to be"
                "null-like values to SQLite NULL values, removing NOT NULL column"
                " constraints where necessary."
            ),
            "ref": clean_like_nulls,
        },
    ],
}
