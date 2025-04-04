class FileValidationError(Exception):
    pass

class JsonFileNotFoundError(FileValidationError):
    pass

class JsonFileNotReadableError(FileValidationError):
    pass

class JsonEmptyFileError(FileValidationError):
    pass

class JsonInvalidFileExtensionError(FileValidationError):
    pass

class JsonValidationError(Exception):
    pass
