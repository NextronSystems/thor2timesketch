class Thor2tsError(Exception):
    def __init__(self, error_msg : str = "An error occurred in thor2timesketch") -> None:
        self.error_msg = error_msg
        super().__init__(self.error_msg)

#input errors
class InputError(Thor2tsError):
    def __init__(self, error_msg: str = "Input validation error")  -> None:
        super().__init__(error_msg)


class FileValidationError(InputError):
    def __init__(self, error_msg: str = "File validation error") -> None:
        super().__init__(error_msg)


class JsonFileNotFoundError(FileValidationError):
    def __init__(self, error_msg: str = "JSON file not found") -> None:
        super().__init__(error_msg)


class JsonFileNotReadableError(FileValidationError):
    def __init__(self, error_msg: str = "JSON file is not readable") -> None:
        super().__init__(error_msg)


class JsonEmptyFileError(FileValidationError):
    def __init__(self, error_msg: str = "JSON file is empty") -> None:
        super().__init__(error_msg)


class JsonInvalidFileExtensionError(FileValidationError):
    def __init__(self, error_msg: str = "Invalid file extension") -> None:
        super().__init__(error_msg)


class JsonValidationError(InputError):
    def __init__(self, error_msg: str = "JSON validation error") -> None:
        super().__init__(error_msg)

class JsonParseError(InputError):
    def __init__(self, error_msg: str ="JSON parsing error") -> None:
        super().__init__(error_msg)

#processing errors

class ProcessingError(Thor2tsError):
    def __init__(self, error_msg: str = "Error processing THOR data") -> None:
        super().__init__(error_msg)


class MappingError(ProcessingError):
    def __init__(self, error_msg: str = "Error mapping THOR data") -> None:
        super().__init__(error_msg)


class VersionError(ProcessingError):
    def __init__(self, error_msg: str = "Unsupported THOR log version") -> None:
        super().__init__(error_msg)

class TimestampError(ProcessingError):
    def __init__(self, error_msg: str = "Error extracting timestamp") -> None:
        super().__init__(error_msg)

#output errors
class OutputError(Thor2tsError):
    def __init__(self, error_msg: str = "Error writing or sending output") -> None:
        super().__init__(error_msg)

class TimesketchError(OutputError):
    def __init__(self, error_msg: str = "Error connecting to Timesketch") -> None:
        super().__init__(error_msg)