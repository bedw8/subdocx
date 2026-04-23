class MissingFieldInData(Exception):
    def __init__(self, var) -> None:
        super().__init__(
            f"El campo '{var}' presente en el template no se encuentra en los datos.",
        )
