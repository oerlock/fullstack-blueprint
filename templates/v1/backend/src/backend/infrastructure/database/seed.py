"""基础数据（seed）统一注册与执行。

各业务模块提供幂等的 seed 函数并在 SEEDS 中登记；测试夹具建库后与开发环境
初始化复用同一入口。当前尚无业务模块，登记表为空。
"""

from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

SeedFunc = Callable[[AsyncSession], Awaitable[None]]

SEEDS: tuple[SeedFunc, ...] = ()


async def run_seeds(session: AsyncSession) -> None:
    for seed in SEEDS:
        await seed(session)
