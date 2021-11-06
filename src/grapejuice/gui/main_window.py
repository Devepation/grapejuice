import uuid
from typing import Optional, List, Callable

from gi.repository import Gtk, Gdk

from grapejuice import gui_task_manager, background
from grapejuice.tasks import InstallRoblox, OpenLogsDirectory, ShowDriveC, ExtractFastFlags
from grapejuice_common import variables
from grapejuice_common.features.settings import current_settings
from grapejuice_common.features.wineprefix_configuration_model import WineprefixConfigurationModel
from grapejuice_common.gtk.gtk_base import GtkBase
from grapejuice_common.util.computed_field import ComputedField
from grapejuice_common.wine.wineprefix import Wineprefix
from grapejuice_common.wine.wineprefix_hints import WineprefixHint


class GtkListBoxRowWithIcon(Gtk.ListBoxRow):
    box: Gtk.Box

    def __init__(self, *args, icon_name: str = "security-low", **kwargs):
        super().__init__(*args, **kwargs)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(10)
        box.set_margin_end(10)

        image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        image.set_margin_right(10)
        box.add(image)

        self.box = box
        self.add(box)


class GtkWineprefixRow(GtkListBoxRowWithIcon):
    _prefix_model: WineprefixConfigurationModel = None
    _label = None

    def __init__(self, prefix: WineprefixConfigurationModel, *args, **kwargs):
        icon_name = "user-home-symbolic"

        if WineprefixHint.studio in prefix.hints_as_enum:
            icon_name = "grapejuice-roblox-studio"

        elif WineprefixHint.player in prefix.hints_as_enum:
            icon_name = "grapejuice-roblox-player"

        super().__init__(*args, icon_name=icon_name, **kwargs)

        self._prefix_model = prefix

        label = Gtk.Label()
        label.set_text(prefix.display_name)
        self._label = label

        self.box.add(label)

    @property
    def prefix_model(self) -> WineprefixConfigurationModel:
        return self._prefix_model

    def set_text(self, text: str):
        self._label.set_text(text)


class GtkStartUsingGrapejuiceRow(GtkListBoxRowWithIcon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, icon_name="user-home-symbolic", **kwargs)

        label = Gtk.Label()
        label.set_text("Start")

        self.box.add(label)


class GtkAddWineprefixRow(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            orientation=Gtk.Orientation.HORIZONTAL,
            **kwargs
        )

        self.set_margin_top(5)
        self.set_margin_bottom(5)
        self.set_halign(Gtk.Align.CENTER)

        image = Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)

        self.add(image)


class PrefixNameHandler:
    _wrapper = None
    _active_widget = None
    _prefix_name: str = ""
    _on_finish_editing_callbacks: List[Callable[["PrefixNameHandler"], None]]

    def __init__(self, prefix_name_wrapper):
        self._on_finish_editing_callbacks = []
        self._wrapper = prefix_name_wrapper

        label = Gtk.Label()
        label.set_text("__invalid__")
        self._label = label

        entry = Gtk.Entry()
        entry.connect("key-press-event", self._on_key_press)

        self._entry = entry

    def _on_key_press(self, _entry, event):
        key = Gdk.keyval_name(event.keyval)

        if key == "Return":
            self.finish_editing()

    def on_finish_editing(self, callback: Callable[["PrefixNameHandler"], None]):
        self._on_finish_editing_callbacks.append(callback)

    def finish_editing(self, use_entry_value: bool = True):
        self._set_active_widget(self._label)

        new_name = self._entry.get_text().strip()
        if not new_name:
            # Cannot use empty names
            use_entry_value = False

        if new_name == self.prefix_name:
            # No need to update
            use_entry_value = False

        if use_entry_value:
            self._prefix_name = new_name
            self._label.set_text(new_name)

            for cb in self._on_finish_editing_callbacks:
                cb(self)

    def _clear_active_widget(self):
        if self._active_widget is not None:
            self._wrapper.remove(self._active_widget)
            self._active_widget = None

    def _set_active_widget(self, widget):
        self._clear_active_widget()
        self._wrapper.add(widget)
        self._active_widget = widget
        widget.show()

    def set_prefix_name(self, name: str):
        self._set_active_widget(self._label)
        self._label.set_text(name)
        self._prefix_name = name

    def activate_entry(self):
        self._entry.set_text(self._prefix_name)
        self._set_active_widget(self._entry)
        self._entry.grab_focus()

    @property
    def is_editing(self):
        return self._active_widget is self._entry

    @property
    def prefix_name(self) -> str:
        return self._prefix_name


def _open_fast_flags_for(prefix: Wineprefix):
    from grapejuice.gui.fast_flag_warning import FastFlagWarning

    def show_fast_flag_window():
        from grapejuice.gui.fast_flag_editor import FastFlagEditor

        fast_flag_editor = FastFlagEditor(prefix=prefix)
        fast_flag_editor.window.show()

    def warning_callback(confirmed: bool):
        if not confirmed:
            return

        task = ExtractFastFlags(prefix)
        background.tasks.add(task)

        gui_task_manager.wait_for_task(task, show_fast_flag_window)

    warning_window = FastFlagWarning(warning_callback)
    warning_window.show()


class MainWindow(GtkBase):
    _current_page = None
    _current_prefix_model: Optional[WineprefixConfigurationModel] = None
    _prefix_name_handler: PrefixNameHandler
    _current_prefix: ComputedField[Wineprefix]

    def __init__(self):
        super().__init__(glade_path=variables.grapejuice_glade())

        self._prefix_name_handler = PrefixNameHandler(self.widgets.prefix_name_wrapper)

        self._connect_signals()
        self._populate_prefix_list()
        self._show_start_page()

        self._current_prefix = ComputedField(
            lambda: None if self._current_prefix_model is None else Wineprefix(self._current_prefix_model)
        )

    def _save_current_prefix(self):
        if self._current_prefix_model is not None:
            current_settings.save_prefix_model(self._current_prefix_model)

    def _connect_signals(self):
        self.widgets.main_window.connect("destroy", Gtk.main_quit)
        self.widgets.prefix_list.connect("row-selected", self._prefix_row_selected)

        self.widgets.edit_prefix_name_button.connect("clicked", self._edit_prefix_name)
        self.widgets.install_roblox_button.connect(
            "clicked",
            lambda _b: gui_task_manager.run_task_once(InstallRoblox, self._current_prefix.value)
        )
        self.widgets.view_logs_button.connect(
            "clicked",
            lambda _b: gui_task_manager.run_task_once(OpenLogsDirectory)
        )
        self.widgets.drive_c_button.connect(
            "clicked",
            lambda _b: gui_task_manager.run_task_once(ShowDriveC, self._current_prefix.value)
        )
        self.widgets.fflags_button.connect(
            "clicked",
            lambda _b: _open_fast_flags_for(self._current_prefix.value)
        )

        def do_finish_editing_prefix_name(_handler):
            if self._current_prefix_model is not None:
                self._current_prefix_model.display_name = self._prefix_name_handler.prefix_name
                self._update_prefix_in_prefix_list(self._current_prefix_model)
                self._save_current_prefix()

        self._prefix_name_handler.on_finish_editing(do_finish_editing_prefix_name)

    def _show_start_page(self):
        self._set_page(self.widgets.cc_start_page)

    def _edit_prefix_name(self, _button):
        if self._prefix_name_handler.is_editing:
            self._prefix_name_handler.finish_editing()

        else:
            self._prefix_name_handler.activate_entry()

    def _prefix_row_selected(self, _prefix_list, prefix_row):
        if isinstance(prefix_row, GtkWineprefixRow):
            self._show_prefix(prefix_row.prefix_model)

        elif isinstance(prefix_row, GtkStartUsingGrapejuiceRow):
            self._show_start_page()

        elif isinstance(prefix_row, Gtk.ListBoxRow):
            self._show_page_for_new_prefix()

    def _populate_prefix_list(self):
        listbox = self.widgets.prefix_list

        for child in listbox.get_children():
            listbox.remove(child)
            child.destroy()

        start_row = GtkStartUsingGrapejuiceRow()
        listbox.add(start_row)

        for prefix in current_settings.parsed_wineprefixes_sorted:
            row = GtkWineprefixRow(prefix)
            listbox.add(row)

        add_prefix_row = GtkAddWineprefixRow()
        listbox.add(add_prefix_row)

        listbox.show_all()

    def _update_prefix_in_prefix_list(self, prefix: WineprefixConfigurationModel):
        for child in self.widgets.prefix_list.get_children():
            if isinstance(child, GtkWineprefixRow):
                if child.prefix_model.id == prefix.id:
                    child.set_text(prefix.display_name)

    def _show_prefix(self, prefix: WineprefixConfigurationModel):
        self._current_prefix.clear_cached_value()
        self._set_page(self.widgets.cc_prefix_page)
        self._current_prefix_model = prefix
        self._prefix_name_handler.set_prefix_name(prefix.display_name)

    def _show_page_for_new_prefix(self):
        model = WineprefixConfigurationModel(
            str(uuid.uuid4()),
            0,
            "gaming",
            "New Wineprefix",
            "",
            "",
            dict(),
            list()
        )

        self._show_prefix(model)

    def _set_page(
        self,
        new_page: Optional = None,
        show_all: bool = True,
        clear_current_prefix: bool = True
    ):
        if self._current_page is not None:
            self.widgets.page_wrapper.remove(self._current_page)
            self._current_page = None

        if new_page is not None:
            self.widgets.page_wrapper.add(new_page)
            self._current_page = new_page

            if show_all:
                self._current_page.show_all()

        if clear_current_prefix:
            self._current_prefix_model = None

    def show(self):
        self.widgets.main_window.show()
