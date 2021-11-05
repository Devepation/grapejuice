from typing import Optional

from grapejuice import background
from grapejuice.background import BackgroundTask
from grapejuice_common.gtk.gtk_stuff import dialog
from grapejuice_common.util.event import Event

once_task_tracker = dict()
on_background_task_error = Event()
on_background_errors_shown = Event()
background_task_errors = []


def _generic_already_running():
    dialog("This task is already being performed!")


def run_task_once(
    task_class,
    *args,
    on_already_running: Optional[callable] = None,
    **kwargs
):
    if task_class in once_task_tracker.values():
        if on_already_running is None:
            _generic_already_running()

        else:
            on_already_running()

        return

    def on_error(*args2):
        on_background_task_error(*args2)

    def on_finish(finished_task):
        try:
            once_task_tracker.pop(finished_task)

        except KeyError:
            pass

    kwargs["on_error_callback"] = on_error
    kwargs["on_finish_callback"] = on_finish

    task: BackgroundTask = task_class(*args, **kwargs)
    once_task_tracker[task] = task_class

    background.tasks.add(task)
