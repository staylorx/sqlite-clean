"""
SQLite-clean constants to be used in other areas of this library.
"""

# A reference dictionary for SQLite affinity and storage class types
# See more here: https://www.sqlite.org/datatype3.html#affinity_name_examples
SQLITE_AFF_REF = {
    "INTEGER": [
        "INT",
        "INTEGER",
        "TINYINT",
        "SMALLINT",
        "MEDIUMINT",
        "BIGINT",
        "UNSIGNED BIG INT",
        "INT2",
        "INT8",
    ],
    "TEXT": [
        "CHARACTER",
        "VARCHAR",
        "VARYING CHARACTER",
        "NCHAR",
        "NATIVE CHARACTER",
        "NVARCHAR",
        "TEXT",
        "CLOB",
    ],
    "BLOB": ["BLOB"],
    "REAL": [
        "REAL",
        "DOUBLE",
        "DOUBLE PRECISION",
        "FLOAT",
    ],
    "NUMERIC": [
        "NUMERIC",
        "DECIMAL",
        "BOOLEAN",
        "DATE",
        "DATETIME",
    ],
}

# strings which may represent null values
LIKE_NULLS = ("null", "none", "nan")
