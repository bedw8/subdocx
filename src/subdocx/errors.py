class SubdocxError(Exception):
    pass


class MissingFieldInData(SubdocxError):
    def __init__(self, var) -> None:
        super().__init__(
            f"El campo '{var}' presente en el template no se encuentra en los datos.",
        )


class InvalidSubstitutionOptions(SubdocxError):
    pass


class UnknownSubstitutionOption(SubdocxError):
    def __init__(self, key: str) -> None:
        super().__init__(f"Unknown substitution option '{key}'.")


class InvalidRepetitionConfiguration(SubdocxError):
    pass


class InvalidRepetitionData(SubdocxError):
    pass


class InvalidBatchTable(SubdocxError):
    pass


class EmptyBatchTable(SubdocxError):
    def __init__(self) -> None:
        super().__init__("Batch substitution requires a non-empty pandas DataFrame.")


class InvalidRepetitionCount(SubdocxError):
    def __init__(self, count) -> None:
        super().__init__(f"Repetition count must be a positive integer. Got: {count!r}.")
