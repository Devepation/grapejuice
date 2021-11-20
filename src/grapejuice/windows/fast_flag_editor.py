import os
from typing import Union, Optional

from gi.repository import Gtk

from grapejuice_common import variables, paths
from grapejuice_common.features.fast_flags import FastFlagList, FastFlag, FastFlagDictionary
from grapejuice_common.gtk.gtk_base import GtkBase
from grapejuice_common.gtk.gtk_paginator import GtkPaginator
from grapejuice_common.gtk.gtk_util import dialog
from grapejuice_common.util.paginator import Paginator
from grapejuice_common.wine.wine_functions import get_studio_wineprefix
from grapejuice_common.wine.wineprefix import Wineprefix


def _app_settings_paths(prefix: Wineprefix):
    return prefix.roblox.roblox_studio_app_settings_path, prefix.roblox.roblox_player_app_settings_path


class WidgetStuff:
    def __init__(self, widget, get_value, set_value):
        self.widget = widget
        self.get_value = get_value
        self.set_value = set_value
        self.icon_changes: Union[None, Gtk.Image] = None
        self.reset_button: Union[None, Gtk.Button] = None


def flag_to_widget(flag: FastFlag, on_changed: callable = None) -> Union[None, WidgetStuff]:
    widget = None

    if flag.is_a(bool):
        widget = Gtk.Switch()
        widget.set_active(flag.value)
        widget.set_vexpand(False)
        widget.set_vexpand_set(True)

        def get_value():
            return widget.get_active()

        def set_value(v):
            widget.set_active(v)

        if on_changed is not None:
            widget.connect("state-set", on_changed)

    elif flag.is_a(str):
        widget = Gtk.Entry()
        widget.set_text(flag.value)
        widget.set_hexpand(True)
        widget.set_hexpand_set(True)

        def get_value():
            return widget.get_text()

        def set_value(v):
            widget.set_text(str(v))

        if on_changed is not None:
            widget.connect("changed", on_changed)

    elif flag.is_a(int):
        adjustment = Gtk.Adjustment()
        adjustment.set_step_increment(1.0)
        adjustment.set_upper(2147483647)
        adjustment.set_value(flag.value)

        widget = Gtk.SpinButton()
        widget.set_adjustment(adjustment)
        widget.set_value(flag.value)

        def get_value():
            return int(adjustment.get_value())

        def set_value(v):
            adjustment.set_value(int(v))

        if on_changed is not None:
            adjustment.connect("value-changed", on_changed)

    else:
        return None

    return WidgetStuff(widget, get_value, set_value)


class FastFlagEditor(GtkBase):
    _prefix: Wineprefix

    def __init__(self, prefix: Wineprefix, fast_flags: Optional[FastFlagDictionary] = None):
        super().__init__(
            glade_path=paths.fast_flag_editor_glade(),
            handler_instance=self,
            root_widget_name="fast_flag_editor"
        )

        self._prefix = prefix

        if fast_flags is not None:
            self._fast_flags = FastFlagList(source_dictionary=fast_flags)

        else:
            studio_prefix = get_studio_wineprefix()

            self._fast_flags = FastFlagList(source_file=next(
                filter(
                    lambda f: f.exists(),
                    (paths.fast_flag_cache_location(), studio_prefix.roblox.fast_flag_dump_path)
                )
            ))

        studio_settings_path, player_settings_path = _app_settings_paths(prefix)
        studio_settings_exist = studio_settings_path and studio_settings_path.exists()
        player_settings_exist = player_settings_path and player_settings_path.exists()

        if studio_settings_exist and player_settings_exist:
            with open(studio_settings_path, encoding=variables.text_encoding()) as studio_settings:
                with open(player_settings_path, encoding=variables.text_encoding()) as player_settings:
                    if studio_settings.read() != player_settings.read():
                        dialog(
                            "The flags for the Roblox Player and Roblox Studio are different. "
                            "The editor will use the flags from Roblox Studio, which will replace "
                            "the flags from the Roblox Player when the flags are saved."
                        )

        for file in filter(lambda f: f.exists(), (studio_settings_path, player_settings_path)):
            self._fast_flags.overlay_flags(FastFlagList(source_file=file))

        self._paginator = Paginator(self._fast_flags, 50)
        self._gtk_paginator = GtkPaginator(self._paginator)
        self.gtk_pager_box.add(self._gtk_paginator.root_widget)

        self._flag_refs = dict()
        self._rows = dict()
        self._displayed_rows = list()

        self._populate()
        self._paginator.paged.add_listener(self._populate)

        self.__unsaved_changes = False

    def _populate(self):
        gtk_list = self.gtk_fast_flag_list

        for row in self._displayed_rows:
            gtk_list.remove(row)

        self._displayed_rows = list()

        for flag in self._paginator.page:
            if flag in self._rows:
                row = self._rows[flag]

            else:
                row = self.new_row(flag)
                self._rows[flag] = row

            gtk_list.add(row)
            self._displayed_rows.append(row)

        self.fast_flag_scroll.get_vadjustment().set_value(0)
        gtk_list.show_all()

        self._update_change_icons()

    @property
    def _unsaved_changes(self):
        return self.__unsaved_changes

    @_unsaved_changes.setter
    def _unsaved_changes(self, v):
        self.__unsaved_changes = v

        if self.__unsaved_changes:
            self.gtk_header.set_subtitle("Unsaved changes!")

        else:
            self.gtk_header.set_subtitle("")

    @property
    def window(self):
        return self.widgets.fast_flag_editor

    @property
    def gtk_fast_flag_list(self):
        return self.widgets.fast_flag_list

    @property
    def gtk_pager_box(self):
        return self.widgets.paginator_box

    @property
    def gtk_header(self):
        return self.widgets.fast_flag_editor_header

    @property
    def fast_flag_scroll(self):
        return self.widgets.fast_flag_scroll

    def new_row(self, flag: FastFlag):
        builder = self._create_builder()

        row = builder.get_object("fast_flag_row")

        name_label = builder.get_object("fflag_name_label")
        name_label.set_text(flag.name)

        widgets = builder.get_object("fast_flag_widgets")
        icon_changes = builder.get_object("icon_flag_changes")
        reset_button = builder.get_object("fflag_reset_button")

        stuff = None

        def reset_flag(*_):
            flag.reset()
            stuff.set_value(flag.value)
            reset_button.hide()

        reset_button.connect("clicked", reset_flag)

        def on_widget_changed(*_):
            flag.value = stuff.get_value()
            self._update_change_icons()

            if flag.has_changed and not flag.is_a(bool):
                reset_button.show()

            else:
                reset_button.hide()

            self._unsaved_changes = True

        stuff = flag_to_widget(flag, on_widget_changed)
        stuff.icon_changes = icon_changes
        stuff.reset_button = reset_button

        if stuff and stuff.widget is not None:
            self._flag_refs[flag] = stuff
            widgets.add(stuff.widget)

        wrapper = Gtk.ListBoxRow()
        wrapper.add(row)

        return wrapper

    def _input_values_to_flags(self):
        for flag, ref in self._flag_refs.items():
            flag.value = ref.get_value()

    def _flags_to_inputs(self):
        self._fast_flags.sort()

        for flag in filter(lambda f: f in self._flag_refs, self._fast_flags):
            ref = self._flag_refs[flag]
            ref.set_value(flag.value)

        self._paginator.paged()

    def _update_change_icons(self):
        for flag, ref in self._flag_refs.items():
            if flag.has_changed:
                ref.icon_changes.show()
                if not flag.is_a(bool):
                    ref.reset_button.show()

            else:
                ref.icon_changes.hide()
                ref.reset_button.hide()

            if flag.is_a(bool):
                ref.reset_button.hide()

    def save_flags(self, *_):
        self._input_values_to_flags()
        changed_flags = self._fast_flags.get_changed_flags()

        for file in _app_settings_paths(self._prefix):
            changed_flags.export_to_file(file)

        self._unsaved_changes = False

    def on_search_changed(self, search_entry):
        query = search_entry.get_text().lower()

        if query:
            def filter_function(flags_list):
                return filter(lambda flag: query in flag.name.lower(), flags_list)

            self._paginator.filter_function = filter_function

        else:
            self._paginator.filter_function = None

    def reset_all_flags(self, *_):
        self._fast_flags.reset_all_flags()
        self._flags_to_inputs()
        self._unsaved_changes = False

    def delete_user_flags(self, *_):
        self.reset_all_flags()

        for path in filter(lambda p: p and p.exists(), _app_settings_paths(self._prefix)):
            os.remove(path)
