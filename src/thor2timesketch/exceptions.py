class Thor2tsError(Exception):
    def __init__(self, error_msg: str = "An error occurred in thor2ts") -> None:
        self.error_msg = error_msg
        super().__init__(self.error_msg)


# input errors
class InputError(Thor2tsError):
    pass


class FileValidationError(InputError):
    pass


class FileNotFound(FileValidationError):
    pass


class FileNotReadableError(FileValidationError):
    pass


class EmptyFileError(FileValidationError):
    pass


class InvalidFileExtensionError(FileValidationError):
    pass


class FilterConfigError(FileValidationError):
    pass


class JsonValidationError(InputError):
    pass


class JsonParseError(InputError):
    pass


# processing errors
class ProcessingError(Thor2tsError):
    pass


class MappingError(ProcessingError):
    pass


class VersionError(ProcessingError):
    pass


class TimestampError(ProcessingError):
    pass


class FlattenJsonError(ProcessingError):
    pass


# output errors
class OutputError(Thor2tsError):
    pass


class TimesketchError(Thor2tsError):
    pass
