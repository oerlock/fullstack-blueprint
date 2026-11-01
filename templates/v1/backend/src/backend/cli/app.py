"""命令行应用。"""

import typer

from backend.config import settings

cli_app = typer.Typer(no_args_is_help=True, help="后台管理命令")


@cli_app.callback()
def callback() -> None:
    """后台管理命令入口。"""


@cli_app.command("env")
def show_env() -> None:
    """输出当前运行环境。"""

    typer.echo(settings.runtime_env)
