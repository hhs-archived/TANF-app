"""Schema for HEADER row of all submission types."""

from tdpservice.parsers.dataclasses import FieldType
from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import TanfDataReportSchema
from tdpservice.parsers.validators import category1, category2


header = TanfDataReportSchema(
    record_type="HEADER",
    model=dict,
    preparsing_validators=[
        category1.recordHasLength(23),
        category1.recordStartsWith(
            "HEADER", lambda _: "Your file does not begin with a HEADER record."
        ),
    ],
    postparsing_validators=[],
    fields=[
        Field(
            item="2",
            name="title",
            friendly_name="title",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=0,
            endIndex=6,
            required=True,
            validators=[
                category2.isEqual("HEADER"),
            ],
        ),
        Field(
            item="4",
            name="year",
            friendly_name="year",
            type=FieldType.NUMERIC,
            startIndex=6,
            endIndex=10,
            required=True,
            validators=[category2.isBetween(2000, 2099, inclusive=True)],
        ),
        Field(
            item="5",
            name="quarter",
            friendly_name="quarter",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=10,
            endIndex=11,
            required=True,
            validators=[category2.isOneOf(["1", "2", "3", "4"])],
        ),
        Field(
            item="6",
            name="type",
            friendly_name="type",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=11,
            endIndex=12,
            required=True,
            validators=[category2.isOneOf(["A", "C", "G", "S"])],
        ),
        Field(
            item="1",
            name="state_fips",
            friendly_name="state fips",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=12,
            endIndex=14,
            required=False,
            validators=[
                category2.isOneOf([
                    "00", "01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13",
                    "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25",
                    "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36",
                    "37", "38", "39", "40", "41", "42", "44", "45", "46", "47", "48",
                    "49", "50", "51", "53", "54", "55", "56", "66", "72", "78"
                ]),
            ],
        ),
        Field(
            item="3",
            name="tribe_code",
            friendly_name="tribe code",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=14,
            endIndex=17,
            required=False,
            validators=[category2.isBetween(0, 999, inclusive=True, cast=int)],
        ),
        Field(
            item="7",
            name="program_type",
            friendly_name="program type",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=17,
            endIndex=20,
            required=True,
            validators=[category2.isOneOf(["TAN", "SSP"])],
        ),
        Field(
            item="8",
            name="edit",
            friendly_name="edit",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=20,
            endIndex=21,
            required=True,
            validators=[category2.isOneOf(["1", "2"])],
        ),
        Field(
            item="9",
            name="encryption",
            friendly_name="encryption",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=21,
            endIndex=22,
            required=False,
            validators=[category2.isOneOf([" ", "E"])],
        ),
        Field(
            item="10",
            name="update",
            friendly_name="update indicator",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=22,
            endIndex=23,
            required=True,
            validators=[category2.validateHeaderUpdateIndicator()],
            ignore_errors=True,
        ),
    ],
)
