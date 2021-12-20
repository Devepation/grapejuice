import os
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from grapejuice import background
from grapejuice_common import paths
from grapejuice_common.recipes.fps_unlocker_recipe import FpsUnlockerRecipe
from grapejuice_common.update_info_providers import UpdateInformationProvider
from grapejuice_common.util import xdg_open
from grapejuice_common.wine.wineprefix import Wineprefix


class RunRobloxStudio(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__("Launching Roblox Studio", **kwargs)

        self._prefix = prefix

    def work(self) -> None:
        from grapejuice_common.ipc.dbus_client import dbus_connection
        dbus_connection().launch_studio(self._prefix.configuration.id)


class ExtractFastFlags(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__("Extracting Fast Flags", **kwargs)

        self._prefix = prefix

    def work(self) -> None:
        from grapejuice_common.ipc.dbus_client import dbus_connection

        should_extract_flags = True

        # Only check fast flags every x minutes, checking more often is overkill
        # This also reduces overall compute time used, yay!

        if paths.fast_flag_cache_location().exists():
            ten_minutes_ago = datetime.now() - timedelta(minutes=10)

            stat = os.stat(paths.fast_flag_cache_location())
            if stat.st_mtime > ten_minutes_ago.timestamp():
                should_extract_flags = False

        if should_extract_flags:
            dbus_connection().extract_fast_flags()

        else:
            time.sleep(1)  # Make it feel like Grapejuice is doing something


class OpenLogsDirectory(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__("Opening logs directory", **kwargs)

    def work(self) -> None:
        path = paths.logging_directory()
        path.mkdir(parents=True, exist_ok=True)

        subprocess.check_call(["xdg-open", str(path)])


class OpenConfigFile(background.BackgroundTask):
    def __init__(self, **kwargs):
        super().__init__("Opening configuration file", **kwargs)

    def work(self) -> None:
        subprocess.check_call(["xdg-open", str(paths.grapejuice_user_settings())])


class PerformUpdate(background.BackgroundTask):
    def __init__(self, update_provider: UpdateInformationProvider, reopen: bool = False, **kwargs):
        super().__init__(name="Performing Update", **kwargs)
        self._update_provider = update_provider
        self._reopen = reopen

    def work(self) -> None:
        self._update_provider.do_update()

        if self._reopen:
            subprocess.Popen(["bash", "-c", f"{sys.executable} -m grapejuice gui & disown"], preexec_fn=os.setpgrp)

            from gi.repository import Gtk
            Gtk.main_quit()

            sys.exit(0)


class InstallRoblox(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(f"Installing Roblox in {prefix.configuration.display_name}", **kwargs)
        self._prefix = prefix

    def work(self):
        self._prefix.roblox.install_roblox()


class ShowDriveC(background.BackgroundTask):
    _path: Path

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(f"Opening Drive C in {prefix.configuration.display_name}", **kwargs)
        self._path = prefix.paths.drive_c

    def work(self):
        xdg_open(str(self._path))


class FaultyOnPurpose(background.BackgroundTask):
    _timeout: int

    def __init__(self, timeout: Optional[int] = None, **kwargs):
        super().__init__("Causing problems", **kwargs)
        self._timeout = timeout or random.randint(2, 5)

    def work(self):
        try:
            time.sleep(self._timeout)

        except KeyboardInterrupt:
            pass

        raise RuntimeError("Woops 😈")


class RunBuiltinWineApp(background.BackgroundTask):
    _prefix: Wineprefix
    _app: str

    def __init__(self, prefix: Wineprefix, app: str, **kwargs):
        super().__init__(f"Running {app} in {prefix.configuration.display_name}", **kwargs)

        self._prefix = prefix
        self._app = app

    def work(self):
        self._prefix.core_control.run_exe(self._app)


class RunLinuxApp(background.BackgroundTask):
    _prefix: Wineprefix
    _app: str

    def __init__(self, prefix: Wineprefix, app: str, **kwargs):
        super().__init__(f"Running {app} in {prefix.configuration.display_name}", **kwargs)

        self._prefix = prefix
        self._app = app

    def work(self):
        self._prefix.core_control.run_linux_command(self._app)


class KillWineserver(background.BackgroundTask):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, **kwargs):
        super().__init__(f"Killing wineserver for {prefix.configuration.display_name}", **kwargs)

        self._prefix = prefix

    def work(self):
        self._prefix.core_control.kill_wine_server()


class InstallFPSUnlocker(background.BackgroundTask):
    _prefix: Wineprefix
    _check_exists: bool  # Horrible name

    def __init__(self, prefix: Wineprefix, check_exists: bool = False, **kwargs):
        super().__init__(f"Installing FPS unlocker in {prefix.configuration.display_name}", **kwargs)

        self._prefix = prefix
        self._check_exists = check_exists

    def work(self):
        recipe = FpsUnlockerRecipe()

        if self._check_exists:
            self._log.info("Only installing FPS unlocker if its not present")

            if not recipe.exists_in(self._prefix):
                recipe.make_in(self._prefix)

        else:
            self._log.info("Installing FPS unlocker with /style/")

            recipe.make_in(self._prefix)
