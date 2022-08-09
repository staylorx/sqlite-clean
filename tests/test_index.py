""" Tests for sqlite_clean.index """

import jsonschema

from sqlite_clean.index import SQLITE_CLEAN_INDEX

# jsonschema for SQLITE_CLEAN_INDEX
SQLITE_CLEAN_INDEX_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "properties": {
        "lint": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "desc": {"type": "string"},
                    "ref": {"type": "string"},
                },
                "required": ["desc", "id", "ref"],
            },
        },
        "fix": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "desc": {"type": "string"},
                    "ref": {"type": "string"},
                },
                "required": ["desc", "id", "ref"],
            },
        },
    },
    "required": ["fix", "lint"],
}


def test_sqlite_clean_index():
    """
    Testing SQLITE_CLEAN_INDEX
    """

    # test for unique id's
    ids = [x["id"] for x in SQLITE_CLEAN_INDEX["lint"] + SQLITE_CLEAN_INDEX["fix"]]
    assert len(ids) == len(set(ids))

    # build a modified version of index for jsonschema validation
    # note: we do this because functions are not json compatible values
    sqlite_clean_index_for_schema = {
        key: [
            {
                x_key: x_val.__name__ if x_key == "ref" else x_val
                for x_key, x_val in x.items()
            }
            for x in val
        ]
        for key, val in SQLITE_CLEAN_INDEX.items()
    }

    # validate against jsonschema
    # note: jsonschema.validate returns nonetype if no errors detected
    assert isinstance(
        jsonschema.validate(sqlite_clean_index_for_schema, SQLITE_CLEAN_INDEX_SCHEMA),
        type(None),
    )
