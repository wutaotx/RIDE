#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from os.path import abspath, dirname, join

import wx
from wx import Colour
from wx.lib.masked import NumCtrl

# from .. import widgets
from ..ui.preferences_dialogs import (PreferencesPanel, SpinChoiceEditor, IntegerChoiceEditor, boolean_editor,
                                      StringChoiceEditor, PreferencesColorPicker)
from ..widgets import Label
from .managesettingsdialog import SaveLoadSettings
from ..context import IS_WINDOWS

try:  # import installed version first
    from pygments.lexers import robotframework as robotframeworklexer
except ImportError: # Pygments is not installed
    robotframeworklexer = None

ID_SAVELOADSETTINGS = wx.NewId()
ID_LOAD = 5551
ID_SAVE = 5552
ID_CANCEL = -1

from functools import lru_cache

@lru_cache(maxsize=2)
def ReadFonts(fixed=False):
    """Returns list with fixed width fonts"""
    f = wx.FontEnumerator()
    f.EnumerateFacenames()
    names = f.GetFacenames(fixedWidthOnly=fixed)
    names = [n for n in names if not n.startswith('@')]
    names.sort()
    return names


class EditorPreferences(PreferencesPanel):

    def __init__(self, settings, *args, **kwargs):
        super(EditorPreferences, self).__init__(*args, **kwargs)
        self._settings = settings
        self._color_pickers = []

        # what would make this UI much more usable is if there were a
        # preview window in the dialog that showed all the colors. I
        # don't have the time to do that right now, so this will have
        # to suffice.

        font_editor = self._create_font_editor()
        colors_sizer = self.create_colors_sizer()
        main_sizer = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)
        buttons_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        reset = wx.Button(self, wx.ID_ANY, 'Reset colors to default')
        saveloadsettings = wx.Button(self, ID_SAVELOADSETTINGS, 'Save or Load settings')
        main_sizer.Add(font_editor)
        main_sizer.Add(colors_sizer)
        buttons_sizer.Add(reset)
        buttons_sizer.AddSpacer(10)
        buttons_sizer.Add(saveloadsettings)
        main_sizer.Add(buttons_sizer)
        self.SetSizer(main_sizer)
        self.Bind(wx.EVT_BUTTON, self.OnReset)
        self.Bind(wx.EVT_BUTTON, self.OnSaveLoadSettings)

    def OnSaveLoadSettings(self, event):
        raise NotImplementedError('Implement me')

    def OnReset(self, event):
        defaults = self._read_defaults()
        for picker in self._color_pickers:
            picker.SetColour(defaults[picker.key])

    def _read_defaults(self, plugin=False):
        settings = [s.strip() for s in open(self._get_path(), 'r').readlines()]
        name = ('[[%s]]' if plugin else '[%s]') % self.name
        start_index = settings.index(name) + 1
        defaults = {}
        for line in settings[start_index:]:
            if line.startswith('['):
                break
            if not line:
                continue
            key, value = [s.strip().strip('\'') for s in line.split("=")]
            defaults[key] = value
        return defaults

    def _get_path(self):
        return join(dirname(abspath(__file__)), 'settings.cfg')

    def _create_font_editor(self):
        f = IntegerChoiceEditor(
            self._settings, 'font size', 'Font Size',
            [str(i) for i in range(8, 16)])
        sizer = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=30)
        l_size = f.label(self)
        if IS_WINDOWS:
            background_color = Colour("light gray")
            foreground_color = Colour("black")
            l_size.SetBackgroundColour(background_color)
            l_size.SetOwnBackgroundColour(background_color)
            l_size.SetForegroundColour(foreground_color)
            l_size.SetOwnForegroundColour(foreground_color)
        sizer.AddMany([l_size, f.chooser(self)])
        fixed_font = False
        if 'zoom factor' in self._settings:
            z = SpinChoiceEditor(
                self._settings, 'zoom factor', 'Zoom Factor', (-10, 20))
            l_zoom = z.label(self)
            if IS_WINDOWS:
                l_zoom.SetForegroundColour(foreground_color)
                l_zoom.SetBackgroundColour(background_color)
                l_zoom.SetOwnBackgroundColour(background_color)
                l_zoom.SetOwnForegroundColour(foreground_color)
            sizer.AddMany([l_zoom, z.chooser(self)])
        if 'fixed font' in self._settings:
            l_ff, editor = boolean_editor(self, self._settings, 'fixed font', 'Use fixed width font')
            if IS_WINDOWS:
                l_ff.SetForegroundColour(foreground_color)
                l_ff.SetBackgroundColour(background_color)
                l_ff.SetOwnBackgroundColour(background_color)
                l_ff.SetOwnForegroundColour(foreground_color)
            sizer.AddMany([l_ff, editor])
            fixed_font = self._settings['fixed font']
        if 'font face' in self._settings:
            s = StringChoiceEditor(self._settings, 'font face', 'Font Face', ReadFonts(fixed_font))
            l_font = s.label(self)
            if IS_WINDOWS:
                l_font.SetForegroundColour(foreground_color)
                l_font.SetBackgroundColour(background_color)
                l_font.SetOwnBackgroundColour(background_color)
                l_font.SetOwnForegroundColour(foreground_color)
            sizer.AddMany([l_font, s.chooser(self)])
        return sizer

    def create_colors_sizer(self):
        raise NotImplementedError('Implement me')


class TextEditorPreferences(EditorPreferences):
    location = ("Text Editor",)
    title = "Text Editor Settings"
    name = "Text Edit"

    def __init__(self, settings, *args, **kwargs):
        super(TextEditorPreferences, self).__init__(
            settings[self.name], *args, **kwargs)

    def create_colors_sizer(self):
        container = wx.GridBagSizer()
        column = 0
        row = 0
        if robotframeworklexer:
            settings = (
                        ('argument', 'Argument foreground'),
                        ('comment', 'Comment foreground'),
                        ('error', 'Error foreground'),
                        ('gherkin', 'Gherkin keyword foreground'),
                        ('heading', 'Heading foreground'),
                        ('import', 'Import foreground'),
                        ('variable', 'Variable foreground'),
                        ('tc_kw_name', 'Keyword definition foreground'),
                        ('separator', 'Separator'),
                        ('setting', 'Setting foreground'),
                        ('syntax', 'Syntax characters'),
                        ('background', 'Text background'),
                       )
        else:
            settings = (
                        ('setting', 'Text foreground'),
                        ('background', 'Text background'),
                       )
        if IS_WINDOWS:
            background_color = Colour("light gray")
            foreground_color = Colour("black")
        for settings_key, label_text in settings:
            if column == 4:
                column = 0
                row += 1
            label = wx.StaticText(self, wx.ID_ANY, label_text)
            if IS_WINDOWS:
                label.SetForegroundColour(foreground_color)
                label.SetBackgroundColour(background_color)
                label.SetOwnBackgroundColour(background_color)
                label.SetOwnForegroundColour(foreground_color)
            button = PreferencesColorPicker(
                self, wx.ID_ANY, self._settings, settings_key)
            container.Add(button, (row, column),
                          flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=4)
            self._color_pickers.append(button)
            column += 1
            container.Add(label, (row, column),
                          flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=8)
            column += 1
        return container

    def OnSaveLoadSettings(self, event):
        if event.GetId() != ID_SAVELOADSETTINGS:
            event.Skip()
            return
        save_settings_dialog = SaveLoadSettings(self, self._settings)
        save_settings_dialog.CenterOnParent()
        value = save_settings_dialog.ShowModal()
        # print(f"DEBUG: Value returned by SaveLoadSettings: {value}")
        for picker in self._color_pickers:
            picker.SetColour(self._settings[picker.key])

    def OnReset(self, event):
        defaults = self._read_defaults()
        for picker in self._color_pickers:
            picker.SetColour(defaults[picker.key])


class GridEditorPreferences(EditorPreferences):
    location = ("Grid Editor",)
    title = "Grid Editor Settings"
    name = "Grid"

    def __init__(self, settings, *args, **kwargs):
        super(GridEditorPreferences, self).__init__(
            settings[self.name], *args, **kwargs)
        self.Sizer.Add(self._create_grid_config_editor())

    def _create_grid_config_editor(self):
        settings = self._settings
        sizer = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)
        l_col_size = self._label_for('Default column size')
        if IS_WINDOWS:
            background_color = Colour("light gray")
            foreground_color = Colour("black")
            l_col_size.SetForegroundColour(foreground_color)
            l_col_size.SetBackgroundColour(background_color)
            l_col_size.SetOwnBackgroundColour(background_color)
            l_col_size.SetOwnForegroundColour(foreground_color)
        sizer.Add(l_col_size)
        sizer.Add(self._number_editor(settings, 'col size'))
        l_auto_size, editor = boolean_editor(self, settings, 'auto size cols', 'Auto size columns')
        if IS_WINDOWS:
            l_auto_size.SetForegroundColour(foreground_color)
            l_auto_size.SetBackgroundColour(background_color)
            l_auto_size.SetOwnBackgroundColour(background_color)
            l_auto_size.SetOwnForegroundColour(foreground_color)
        sizer.AddMany([l_auto_size, editor])
        l_max_size = self._label_for('Max column size\n(applies when auto size is on)')
        if IS_WINDOWS:
            l_max_size.SetForegroundColour(foreground_color)
            l_max_size.SetBackgroundColour(background_color)
            l_max_size.SetOwnBackgroundColour(background_color)
            l_max_size.SetOwnForegroundColour(foreground_color)
        sizer.Add(l_max_size)
        sizer.Add(self._number_editor(settings, 'max col size'))
        l_word_wrap, editor = boolean_editor(self, settings, 'word wrap', 'Word wrap and auto size rows')
        if IS_WINDOWS:
            l_word_wrap.SetForegroundColour(foreground_color)
            l_word_wrap.SetBackgroundColour(background_color)
            l_word_wrap.SetOwnBackgroundColour(background_color)
            l_word_wrap.SetOwnForegroundColour(foreground_color)
        sizer.AddMany([l_word_wrap, editor])
        return sizer

    def _label_for(self, name):
        label = ('%s: ' % name).capitalize()
        return Label(self, label=label)

    def _number_editor(self, settings, name):
        initial_value = settings[name]
        editor = NumCtrl(self, value=initial_value, integerWidth=3, allowNone=True)
        """
        editor.SetBackgroundColour(Colour(200, 222, 40))
        editor.SetOwnBackgroundColour(Colour(200, 222, 40))
        editor.SetForegroundColour(Colour(7, 0, 70))
        editor.SetOwnForegroundColour(Colour(7, 0, 70))
        """
        editor.Bind(wx.EVT_TEXT, lambda evt: self._set_value(editor, name))
        return editor

    def _set_value(self, editor, name):
        # Guard against dead object
        if editor:
            value = editor.GetValue()
            if value is not None:
                self._settings.set(name, int(value))

    def create_colors_sizer(self):
        colors_sizer = wx.GridBagSizer()
        self._create_foreground_pickers(colors_sizer)
        self._create_background_pickers(colors_sizer)
        return colors_sizer

    def _create_foreground_pickers(self, colors_sizer):
        row = 0
        for key, label in (
            ('text user keyword', 'User Keyword Foreground'),
            ('text library keyword', 'Library Keyword Foreground'),
            ('text variable', 'Variable Foreground'),
            ('text unknown variable', 'Unknown Variable Foreground'),
            ('text commented', 'Comments Foreground'),
            ('text string', 'Default Foreground'),
            ('text empty', 'Empty Foreground'),
        ):
            lbl = wx.StaticText(self, wx.ID_ANY, label)
            if IS_WINDOWS:
                background_color = Colour("light gray")
                foreground_color = Colour("black")
                lbl.SetForegroundColour(foreground_color)
                lbl.SetBackgroundColour(background_color)
                lbl.SetOwnBackgroundColour(background_color)
                lbl.SetOwnForegroundColour(foreground_color)
            btn = PreferencesColorPicker(
                self, wx.ID_ANY, self._settings, key)
            self._color_pickers.append(btn)
            colors_sizer.Add(btn, (row, 2),
                             flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=4)
            colors_sizer.Add(lbl, (row, 3),
                             flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=4)
            row += 1

    def _create_background_pickers(self, colors_sizer):
        row = 0
        if IS_WINDOWS:
            background_color = Colour("light gray")
            foreground_color = Colour("black")
        for key, label in (
            ('background assign', 'Variable Background'),
            ('background keyword', 'Keyword Background'),
            ('background mandatory', 'Mandatory Field Background'),
            ('background optional', 'Optional Field Background'),
            ('background must be empty', 'Mandatory Empty Field Background'),
            ('background unknown', 'Unknown Background'),
            ('background error', 'Error Background'),
            ('background highlight', 'Highlight Background')
        ):
            lbl = wx.StaticText(self, wx.ID_ANY, label)
            if IS_WINDOWS:
                lbl.SetForegroundColour(foreground_color)
                lbl.SetBackgroundColour(background_color)
                lbl.SetOwnBackgroundColour(background_color)
                lbl.SetOwnForegroundColour(foreground_color)
            btn = PreferencesColorPicker(
                self, wx.ID_ANY, self._settings, key)
            self._color_pickers.append(btn)
            colors_sizer.Add(btn, (row, 0),
                             flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=4)
            colors_sizer.Add(lbl, (row, 1),
                             flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=4)
            row += 1

    def OnSaveLoadSettings(self, event):
        if event.GetId() != ID_SAVELOADSETTINGS:
            event.Skip()
            return
        save_settings_dialog = SaveLoadSettings(self, self._settings)
        save_settings_dialog.CenterOnParent()
        value = save_settings_dialog.ShowModal()
        # print(f"DEBUG: Value returned by SaveLoadSettings: {value}")
        for picker in self._color_pickers:
            picker.SetColour(self._settings[picker.key])


class TestRunnerPreferences(EditorPreferences):
    location = ("Test Runner",)
    title = "Test Runner Settings"
    name = "Test Runner"

    def __init__(self, settings, *args, **kwargs):
        super(TestRunnerPreferences, self).__init__(
            settings['Plugins'][self.name], *args, **kwargs)
        self.Sizer.Add(self._create_test_runner_config_editor())

    def _create_test_runner_config_editor(self):
        self._settings.get('confirm run', True)
        settings = self._settings
        sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        l_confirm, editor = boolean_editor(self, settings, 'confirm run',
                                           'Asks for confirmation to run all tests if none selected ')
        if IS_WINDOWS:
            background_color = Colour("light gray")
            foreground_color = Colour("black")
            l_confirm.SetForegroundColour(foreground_color)
            l_confirm.SetBackgroundColour(background_color)
            l_confirm.SetOwnBackgroundColour(background_color)
            l_confirm.SetOwnForegroundColour(foreground_color)
        sizer.AddMany([l_confirm, editor])
        return sizer

    def create_colors_sizer(self):
        container = wx.GridBagSizer()
        row = 0
        column = 0
        if IS_WINDOWS:
            background_color = Colour("light gray")
            foreground_color = Colour("black")
        for settings_key, label_text in (
            ('foreground', 'Text foreground'),
            ('background', 'Text background'),
            ('error', 'Error foreground'),
        ):
            if column == 4:
                column = 0
                row += 1
            label = wx.StaticText(self, wx.ID_ANY, label_text)
            if IS_WINDOWS:
                label.SetForegroundColour(foreground_color)
                label.SetBackgroundColour(background_color)
                label.SetOwnBackgroundColour(background_color)
                label.SetOwnForegroundColour(foreground_color)
            button = PreferencesColorPicker(
                self, wx.ID_ANY, self._settings, settings_key)
            container.Add(button, (row, column),
                          flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=4)
            self._color_pickers.append(button)
            column += 1
            container.Add(label, (row, column),
                          flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=8)
            column += 1
        return container

    def OnSaveLoadSettings(self, event):
        if event.GetId() != ID_SAVELOADSETTINGS:
            event.Skip()
            return
        save_settings_dialog = SaveLoadSettings(self, self._settings)
        save_settings_dialog.CenterOnParent()
        value = save_settings_dialog.ShowModal()
        # print(f"DEBUG: Value returned by SaveLoadSettings: {value}")
        for picker in self._color_pickers:
            picker.SetColour(self._settings[picker.key])

    def OnReset(self, event):
        defaults = self._read_defaults(plugin=True)
        for picker in self._color_pickers:
            picker.SetColour(defaults[picker.key])
