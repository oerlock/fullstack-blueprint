"""通用错误码与 AE* 异常定义，错误码遵循六位规范。"""

from backend.errors.base import AppError


class AEBadRequest(AppError):
    """400001 参数无效。"""

    code = 400001
    message = "参数无效"


class AEUnauthorized(AppError):
    """401001 认证失败。"""

    code = 401001
    message = "认证失败"


class AEForbidden(AppError):
    """403001 权限不足。"""

    code = 403001
    message = "权限不足"


class AENotFound(AppError):
    """404001 资源不存在。"""

    code = 404001
    message = "资源不存在"


class AEConflict(AppError):
    """409001 资源冲突。"""

    code = 409001
    message = "资源冲突"


class AEValidationError(AppError):
    """422001 数据校验失败。"""

    code = 422001
    message = "数据校验失败"


class AETooManyRequests(AppError):
    """429001 请求频率超限。"""

    code = 429001
    message = "请求频率超限"


class AEInternalError(AppError):
    """500001 内部错误。"""

    code = 500001
    message = "内部错误"


class AEBadGateway(AppError):
    """502001 上游服务错误。"""

    code = 502001
    message = "上游服务错误"


class AEServiceUnavailable(AppError):
    """503001 依赖服务不可用。"""

    code = 503001
    message = "依赖服务不可用"
