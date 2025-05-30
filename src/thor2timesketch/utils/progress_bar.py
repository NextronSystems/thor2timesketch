from types import TracebackType
from typing import Optional, Type
from rich.progress import Progress, SpinnerColumn, TextColumn, ProgressColumn, Task
from rich.text import Text
from thor2timesketch.config.console_config import ConsoleConfig


class ElapsedColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        elapsed = task.elapsed or 0
        m, s = divmod(int(elapsed), 60)
        return Text(f"{m:02d}:{s:02d}", style=ConsoleConfig.LEVEL_STYLES["INFO"])


class ProgressBar:
    def __init__(self, description: str):
        columns = [
            TextColumn(" " * 22),
            ElapsedColumn(),
            SpinnerColumn(
                spinner_name="line", style=ConsoleConfig.LEVEL_STYLES["SUCCESS"]
            ),
            TextColumn(
                "   {task.description}", style=ConsoleConfig.LEVEL_STYLES["INFO"]
            ),
            TextColumn(
                "{task.completed} processed",
                style=ConsoleConfig.LEVEL_STYLES["SUCCESS"],
            ),
            TextColumn(
                "• {task.fields[errors]} errors",
                style=ConsoleConfig.LEVEL_STYLES["ERROR"],
            ),
        ]
        self.processed: int = 0
        self.errors: int = 0
        self.progress = Progress(
            *columns,
            console=ConsoleConfig.console,
            redirect_stdout=False,
            redirect_stderr=False,
            transient=True,
        )
        self.task_id = self.progress.add_task(description, completed=0, errors=0)

    def __enter__(self) -> "ProgressBar":
        self.progress.start()
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> None:
        self.progress.stop()

    def advance(self, step: int = 1, error: int = 0) -> None:
        self.processed += step
        self.errors += error
        self.progress.update(self.task_id, completed=self.processed, errors=self.errors)

    def update_description(self, description: str) -> None:
        self.progress.update(self.task_id, description=description)
