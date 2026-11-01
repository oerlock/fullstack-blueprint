"""全局异常基类。"""


class AppError(Exception):
    code: int = 500001
    message = "Internal Server Error"
    metadata: dict[str, object] | None = None

    @property
    def status_code(self) -> int:
        return self.code // 1000

    def __init__(
            self,
            message: str | None = None,
            *,
            metadata: dict[str, object] | None = None,
    ) -> None:
        self.message = message if message is not None else type(self).message
        self.metadata = metadata
        super().__init__(self.message)
