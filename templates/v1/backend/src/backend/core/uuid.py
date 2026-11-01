"""UUIDv7 生成与 BINARY(16) 转换。"""

import os
import time
import uuid


def uuid7() -> uuid.UUID:
    """生成 UUIDv7（48 位毫秒时间戳 + 随机位）。"""

    timestamp_ms = time.time_ns() // 1_000_000 & (1 << 48) - 1
    rand = os.urandom(10)
    raw = bytearray(16)
    raw[0:6] = timestamp_ms.to_bytes(6, "big")
    raw[6] = 0x70 | rand[0] & 0x0F
    raw[7] = rand[1]
    raw[8] = 0x80 | rand[2] & 0x3F
    raw[9:16] = rand[3:10]
    return uuid.UUID(bytes=bytes(raw))


def uuid_to_bin(value: uuid.UUID) -> bytes:
    """UUID 转为 16 字节大端二进制，用于 BINARY(16) 存储。"""

    return value.bytes


def uuid_from_bin(value: bytes) -> uuid.UUID:
    """从 BINARY(16) 还原 UUID。"""

    if len(value) != 16:
        msg = f"BINARY(16) 长度应为 16 字节，实际 {len(value)} 字节"
        raise ValueError(msg)
    return uuid.UUID(bytes=bytes(value))
