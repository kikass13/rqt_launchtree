#!/usr/bin/env python
import rospy
from rqt_gui_py.plugin import Plugin

from python_qt_binding.QtCore import Qt
from python_qt_binding.QtWidgets import QInputDialog

from rqt_launchtree.launchtree_widget import LaunchtreeWidget

import sys
import os

class LaunchtreePlugin(Plugin):

    _SETTING_LASTPKG = 'last_pkg'
    _SETTING_LASTLAUNCHFILE = 'last_launch'
    _SETTING_LASTLAUNCHARGS = 'last_args'

    def __init__(self, context):
        super(LaunchtreePlugin, self).__init__(context)
        self.kikassMode = False

        ##check argv for parameters
        specialArgDict = dict([(arg.split(":=")[0], arg.split(":=")[1]) for arg in sys.argv[1:]])
        print(specialArgDict)
        if("launchfile" in specialArgDict and "stack" in specialArgDict):
            self.kikassMode = True
            self.launchfilePath = specialArgDict["launchfile"]
            self.stackPath = specialArgDict["stack"]
            print("kikass mode =)")

        self._widget = LaunchtreeWidget(context, kikassMode=self.kikassMode)
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() +
                                        (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)

    def shutdown_plugin(self):
        self._widget.shutdown()

    def save_settings(self, plugin_settings, instance_settings):
        instance_settings.set_value('editor', self._widget.editor)
        if(not self.kikassMode):
            _curr_pkg = self._widget.package_select.currentText()
            rospy.logdebug('save_settings) currentIndex={}'.format(_curr_pkg))
            instance_settings.set_value(self._SETTING_LASTPKG, _curr_pkg)
            instance_settings.set_value(self._SETTING_LASTLAUNCHFILE, self._widget.launchfile_select.currentText())
            instance_settings.set_value(self._SETTING_LASTLAUNCHARGS, self._widget.args_input.text())

    def restore_settings(self, plugin_settings, instance_settings):
        self._widget.editor = instance_settings.value('editor', 'gedit')
        if(not self.kikassMode):
            self._widget.args_input.setText(instance_settings.value(self._SETTING_LASTLAUNCHARGS, ''))
        
        if(self.kikassMode):
            self._widget.block_load(False)
            if(os.path.isfile(self.launchfilePath)):
                self._widget.load_launchfile(self.launchfilePath, self.stackPath)

        else:
            pkg_idx = self._widget.package_select.findText(instance_settings.value(self._SETTING_LASTPKG))
            if pkg_idx >= 0:
                self._widget.package_select.blockSignals(True)
                self._widget.package_select.setCurrentIndex(pkg_idx)
                self._widget.package_select.blockSignals(False)
                self._widget.update_launchfiles(pkg_idx)
                # only set launch file if pkg was restored
                launch_idx = self._widget.launchfile_select.findText(instance_settings.value(self._SETTING_LASTLAUNCHFILE))
                if launch_idx >= 0:
                    self._widget.launchfile_select.blockSignals(True)
                    self._widget.launchfile_select.setCurrentIndex(launch_idx)
                    self._widget.launchfile_select.blockSignals(False)
            self._widget.block_load(False)

    def trigger_configuration(self):
        (text, ok) = QInputDialog.getText(self._widget,
            'Settings for %s' % self._widget.windowTitle(),
            'Command to edit launch files (vim, gedit, ...), can accept args:',
            text = self._widget.editor
        )
        if ok:
            self._widget.editor = text
