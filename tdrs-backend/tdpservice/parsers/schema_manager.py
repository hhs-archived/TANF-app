"""Manager class for a datafile's schema's."""

from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.parsers.fields import TransformField
from tdpservice.parsers.dataclasses import ManagerPVResult
from tdpservice.parsers.schema_defs.utils import ProgramManager
import logging

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages all RowSchema's based on a file's program type and section."""

    def __init__(self, datafile, program_type, section):
        self.datafile = datafile
        self.program_type = program_type
        self.section = section
        self.schema_map = None
        self._init_schema_map()

    def _init_schema_map(self):
        """Initialize all schemas for the program type and section."""
        self.schema_map = ProgramManager.get_schemas(self.program_type, self.section)
        for schemas in self.schema_map.values():
            for schema in schemas:
                schema.datafile = self.datafile

    def parse_and_validate(self, row, generate_error):
        """Run `parse_and_validate` for each schema provided and bubble up errors."""
        try:
            records = []
            schemas = self.schema_map[row.record_type]
            for schema in schemas:
                record, is_valid, errors = schema.parse_and_validate(row, generate_error)
                records.append((record, is_valid, errors))
            return ManagerPVResult(records=records, schemas=schemas)
        except Exception:
            records = [(None, False, [
                generate_error(
                    schema=None,
                    error_category=ParserErrorCategoryChoices.PRE_CHECK,
                    error_message="Unknown Record_Type was found.",
                    record=None,
                    field="Record_Type",
                )
            ])]
            return ManagerPVResult(records=records, schemas=[])

    def update_encrypted_fields(self, is_encrypted):
        """Update whether schema fields are encrypted or not."""
        # This should be called at the begining of parsing after the header has been parsed and we have access
        # to is_encrypted for TANF/SSP/Tribal
        for schemas in self.schema_map.values():
            for schema in schemas:
                for field in schema.fields:
                    if type(field) == TransformField and "is_encrypted" in field.kwargs:
                        field.kwargs['is_encrypted'] = is_encrypted
