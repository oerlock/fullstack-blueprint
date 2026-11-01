"""数据库公共类型。"""

import uuid

from sqlalchemy import BINARY, TypeDecorator

from backend.core.uuid import uuid_from_bin, uuid_to_bin


class GUID(TypeDecorator):
    """Python uuid.UUID 与 MySQL BINARY(16) 之间的转换。"""

    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            msg = f"GUID 类型要求 uuid.UUID，实际 {type(value)}"
            raise TypeError(msg)
        return uuid_to_bin(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid_from_bin(value)
