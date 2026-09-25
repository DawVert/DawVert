#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import plug_conv
from objects import core as dv_core
from objects import globalstore
from objects import format_detect
from objects.exceptions import ProjectFileParserException
from pathlib import Path
from plugins import base as dv_plugins

from PyQt6 import QtWidgets, uic, QtCore, QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog

import logging
import os
import sys
import traceback
import functools
import json

from objects.convproj import fileref
fileref_global = fileref.cvpj_fileref_global

scriptfiledir = os.path.dirname(os.path.realpath(__file__))

from objects.ui.ui_pyqt import Ui_MainWindow
from objects.ui import ui_configmenu

from objects.ui import ui_configmenu_qt6 as ui_configmenu_interface
#from objects.ui import ui_configmenu_gtk3 as ui_configmenu_interface

logging.disable(logging.INFO)

class converterstate():
	is_converting = False
	is_plugscan = False

dragdroploctexts = ['Beside Original', 'In "output" folder', 'Always out.*']

dawvert_intent = dv_core.dawvert_intent()
dawvert_intent.config_load('./__config/config.ini')

dawvert_core = dv_core.core()

class gui_config():
	def __init__(self):
		self.main = {}
		self.main['songnum'] = dawvert_intent.songnum
		self.main['dd_outpath'] = 'beside_original'
		self.main['overwrite_out'] = False
		self.main['auto_convert'] = False
		self.main['language'] = 'english'

		self.session = {}
		self.session['current_in_plug'] = None
		self.session['current_in_set'] = 'main'
		self.session['current_out_plug'] = None
		self.session['current_out_set'] = 'main'

		self.conversion = {}
		self.conversion['splitter_mode'] = dawvert_intent.splitter_mode
		self.conversion['splitter_detect_start'] = dawvert_intent.splitter_detect_start
		self.conversion['output_unused_nle'] = False

		self.extplug = {}
		self.extplug['out_foss'] = True
		self.extplug['out_old'] = True
		self.extplug['out_freeware'] = True
		self.extplug['out_shareware'] = True

		self.soundfont = {}

		self.input_plugins = {}

		self.output_plugins = {}

	def save_in_plugin_config(self):
		plugname = dawvert_core.input_get_current()
		if plugname and dawvert_intent.input_params:
			self.input_plugins[plugname] = dawvert_intent.input_params
		dawvert_intent.input_params = {}

	def get_in_plugin_config(self):
		dawvert_intent.input_params = {}
		plugname = dawvert_core.input_get_current()
		if plugname in self.input_plugins:
			dawvert_intent.input_params = self.input_plugins[plugname]

	def save_out_plugin_config(self):
		plugname = dawvert_core.output_get_current()
		if plugname and dawvert_intent.output_params:
			self.output_plugins[plugname] = dawvert_intent.output_params
		dawvert_intent.output_params = {}

	def get_out_plugin_config(self):
		dawvert_intent.output_params = {}
		plugname = dawvert_core.output_get_current()
		if plugname in self.output_plugins:
			dawvert_intent.output_params = self.output_plugins[plugname]

	def load_json(self, indict):
		if 'main' in indict: self.main = indict['main']
		if 'session' in indict: self.session = indict['session']
		if 'conversion' in indict: self.conversion = indict['conversion']
		if 'extplug' in indict: self.extplug = indict['extplug']
		if 'soundfont' in indict: self.soundfont = indict['soundfont']
		if 'input_plugins' in indict: self.input_plugins = indict['input_plugins']
		if 'output_plugins' in indict: self.output_plugins = indict['output_plugins']

		if 'current_in_plug' not in self.session: self.session['current_in_plug'] = None
		if 'current_in_set' not in self.session: self.session['current_in_set'] = ''
		if 'current_out_plug' not in self.session: self.session['current_out_plug'] = None
		if 'current_out_set' not in self.session: self.session['current_out_set'] = ''

	def save_file(self, filename):
		current_in_plug = dawvert_core.input_get_current()
		current_out_plug = dawvert_core.output_get_current()
		if current_in_plug: self.session['current_in_plug'] = current_in_plug
		if current_out_plug: self.session['current_out_plug'] = current_out_plug

		outdict = {}
		outdict['main'] = self.main
		outdict['session'] = self.session
		outdict['conversion'] = self.conversion
		outdict['extplug'] = self.extplug
		outdict['soundfont'] = self.soundfont
		outdict['input_plugins'] = self.input_plugins
		outdict['output_plugins'] = self.output_plugins

		with open(filename, 'w') as f:
		    json.dump(outdict, f, indent=4)

	def load_file(self, filename):
		injson = {}

		if os.path.exists(filename):
			try:
				with open(filename) as f:
					injson = json.load(f)
			except:
				pass

		self.load_json(injson)


dawvert_config = gui_config()

miniconfmenu_store = ui_configmenu.miniconfmenu_store

configdef_main = miniconfmenu_store()
configdef_main.add_bool('language', False, 'Overwrite Output')
cfgpart = configdef_main.add_enum('language', 'english', 'Language')
cfgpart.add_choice('english','English')
cfgpart.add_choice('japanese','日本語 (Japanese)')
cfgpart.add_choice('russian','Русский (Russian)')
cfgpart.add_choice('chinese_trad','正體字 (Traditional Chinese)')
cfgpart.add_choice('chinese_simp','简化字 (Simplified Chinese)')

configdef_main.add_bool('overwrite_out', False, 'Overwrite Output')
configdef_main.set_group('dd', 'Drag/Drop')
configdef_main.add_bool('auto_convert', False, 'Auto-Convert')
cfgpart = configdef_main.add_enum('dd_outpath', 'out_file', 'Set Drag/Drop Out Path')
cfgpart.add_choice('beside_original','Beside Original')
cfgpart.add_choice('out_folder','In "output" folder')
cfgpart.add_choice('out_file','Always out.')

configdef_soundfont = miniconfmenu_store()
configdef_soundfont.add_text("gm", '', "GM")
configdef_soundfont.add_text("xg", '', "XG")
configdef_soundfont.add_text("gs", '', "GS")
configdef_soundfont.add_text("mt32", '', "MT32")
configdef_soundfont.add_text("mariopaint", '', "Mario Paint")

configdef_conversion = miniconfmenu_store()
configdef_conversion.add_int('songnum', 0, 'Song Number')
configdef_conversion.add_bool('output_unused_nle', False, 'MI2M: Output Unused Patterns')
configdef_conversion.set_group('splitter', 'Notelist Splitter')
configdef_conversion.add_int('splitter_mode', 0, 'Mode')
configdef_conversion.add_int('splitter_detect_start', 0, 'Detect Start')

configdef_extplugs = miniconfmenu_store()
configdef_extplugs.add_bool('out_foss', True, 'Use FOSS Plugins')
configdef_extplugs.add_bool('out_old', True, 'Use Old Plugins')
configdef_extplugs.add_bool('out_freeware', True, 'Use Freeware Plugins')
configdef_extplugs.add_bool('out_shareware', True, 'Use Shareware Plugins')

def debugtxt(intxt):
	if intxt == 'route': return 'RO'
	if intxt == 'rack': return 'CH'
	if intxt == 'groupreturn': return 'GR'
	return '__'

class ConversionWorker(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	update_ui = QtCore.pyqtSignal(list)

	def __init__(self, *args, **kwargs):
		super(ConversionWorker, self).__init__(*args, **kwargs)

	def run(self):
		try:
			converterstate.is_converting = True

			inname = dawvert_core.input_get_current_name()
			outname = dawvert_core.output_get_current_name()

			plug_conv.load_plugins()

			file_name = os.path.splitext(os.path.basename(dawvert_intent.input_file))[0]

			dawvert_intent.flags_compat = []
			if 'output_unused_nle' in dawvert_config.conversion: dawvert_intent.flags_compat.append('mi2m-output-unused-nle')
			dawvert_intent.splitter_mode = dawvert_config.conversion['splitter_mode']
			dawvert_intent.splitter_detect_start = dawvert_config.conversion['splitter_detect_start']

			extplug_cat = []
			if dawvert_config.extplug['out_foss']: extplug_cat.append('foss')
			if dawvert_config.extplug['out_old']: extplug_cat.append('old')
			if dawvert_config.extplug['out_freeware']: extplug_cat.append('nonfree')
			if dawvert_config.extplug['out_shareware']: extplug_cat.append('shareware')
			dawvert_intent.extplug_cat = extplug_cat

			if 'songnum' in dawvert_config.main: dawvert_intent.songnum = dawvert_config.main['songnum']

			if dawvert_intent.output_samples:
				dawvert_intent.output_samples += '/'

				dawvert_intent.path_samples['extracted'] = dawvert_intent.output_samples+'extracted/'
				dawvert_intent.path_samples['downloaded'] = dawvert_intent.output_samples+'downloaded/'
				dawvert_intent.path_samples['generated'] = dawvert_intent.output_samples+'generated/'
				dawvert_intent.path_samples['converted'] = dawvert_intent.output_samples+'converted/'

			else:
				dawvert_intent.set_projname_path()

			dawvert_intent.create_folder_paths()

			fileref_global.reset()
			fileref_global.add_prefix('project_root', None, os.path.dirname(dawvert_intent.input_file))
			fileref_global.add_prefix('dawvert_external_data', None, os.path.join(scriptfiledir, '__external_data'))
			dawvert_intent.do_fileref_global()

			self.update_ui.emit([1, 0])
			self.update_ui.emit([0, 'Processing Input...'])
			dawvert_core.parse_input(dawvert_intent)
			self.update_ui.emit([1, 25])
			self.update_ui.emit([0, 'Converting Project Type and Samples...'])
			dawvert_core.convert_type_output(dawvert_intent)
			self.update_ui.emit([1, 50])
			self.update_ui.emit([0, 'Converting Plugins...'])
			dawvert_core.convert_plugins(dawvert_intent)
			self.update_ui.emit([1, 75])
			self.update_ui.emit([0, 'Processing Output...'])
			dawvert_core.parse_output(dawvert_intent)
			converterstate.is_converting = False
			self.update_ui.emit([1, 100])
			self.update_ui.emit([2, ['OK', '']])
		except ProjectFileParserException:
			converterstate.is_converting = False
			ex_type, ex_value, ex_traceback = sys.exc_info()
			self.update_ui.emit([2, ['Project File Error', str(ex_value)]])
		except SystemExit:
			converterstate.is_converting = False
			ex_type, ex_value, ex_traceback = sys.exc_info()
			self.update_ui.emit([2, ['Exited with no output, See Console.', '']])
			print(traceback.format_exc())
		except:
			converterstate.is_converting = False
			ex_type, ex_value, ex_traceback = sys.exc_info()
			self.update_ui.emit([2, ['Error. See Console.', ex_type.__name__+': '+str(ex_value)]])
			print(traceback.format_exc())
		self.finished.emit()

filedetector_obj = format_detect.file_detector()
filedetector_obj.load_def('data_main/autodetect.xml')

DEBUG_VIEW = 0

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self, *args, obj=None, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)
		self.lab_cfg_main = "Main Config"
		self.lab_cfg_soundfonts = "Soundfont Config"
		self.lab_cfg_externalplugins = "External Plugs Config"
		self.lab_cfg_conversion = "Conversion Config"
		self.lab_cfg_inputplugin = "Input Config"
		self.lab_cfg_outputplugin = "Output Config"

		self.lab_stat_main = "Status: "
		self.lab_stat_convert = "Converting"
		self.lab_stat_notready = "Not Ready"
		self.lab_stat_file_no_input = "No input file."
		self.lab_stat_file_no_output = "No output file."
		self.lab_stat_plug_no_input = "Input plugin not selected."
		self.lab_stat_plug_no_output = "Output plugin not selected."
		self.lab_stat_ow_no_input = "Not overwriting input file."
		self.lab_stat_ow_no_output = "Not overwriting output file."
		self.lab_stat_plug_dead_input = "Input Plugin Unusable"
		self.lab_stat_plug_dead_output = "Output Plugin Unusable"
		self.lab_stat_ready = "Ready"

		wid = QtWidgets.QWidget(self)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(wid)
		self.setWindowTitle('DawVert - The DAW Converter')
		self.setWindowIcon(QtGui.QIcon('icon.png'))
		self.setCentralWidget(wid)
		self.setAcceptDrops(True)

		layout = QtWidgets.QVBoxLayout()

		self.ui.InputFileButton.clicked.connect(self.__choose_input)
		self.ui.OutputFileButton.clicked.connect(self.__choose_output)
		self.ui.OutputSampleButton.clicked.connect(self.__choose_samples)

		self.ui.ListWidget_InPlugSet.currentRowChanged.connect(self.__change_input_plugset)
		self.ui.ListWidget_InPlugin.currentRowChanged.connect(self.__change_input_plugin_nofb)

		self.ui.ListWidget_OutPlugSet.currentRowChanged.connect(self.__change_output_plugset)
		self.ui.ListWidget_OutPlugin.currentRowChanged.connect(self.__change_output_plugin)

		self.ui.ConvertButton.setEnabled(False)
		self.ui.ConvertButton.clicked.connect(self.__do_convert)

		self.ui.AutoDetectButton.clicked.connect(self.__do_auto_detect)

		for x in dawvert_core.input_get_pluginsets_names(): self.ui.ListWidget_InPlugSet.addItem(x)
		for x in dawvert_core.output_get_pluginsets_names(): self.ui.ListWidget_OutPlugSet.addItem(x)

		self.__update_convst()

		self.ui.ConfigMain.clicked.connect(functools.partial(self.open_configmenu, 'main'))
		self.ui.ConfigSoundFont.clicked.connect(functools.partial(self.open_configmenu, 'soundfont'))
		self.ui.ConfigExtPlug.clicked.connect(functools.partial(self.open_configmenu, 'extplug'))
		self.ui.ConfigConversion.clicked.connect(functools.partial(self.open_configmenu, 'conversion'))
		self.ui.ConfigOutput.clicked.connect(functools.partial(self.open_configmenu, 'output'))
		self.ui.ConfigInput.clicked.connect(functools.partial(self.open_configmenu, 'input'))

		cfgsession = dawvert_config.session

		current_in_plug = cfgsession['current_in_plug']
		current_in_set = cfgsession['current_in_set']

		if current_in_set is not None:
			plugsetlist = list(dv_core.pluginsets_input)
			if current_in_set in plugsetlist:
				self.__change_input_plugset_named(current_in_set)
				self.ui.ListWidget_InPlugSet.setCurrentRow(plugsetlist.index(current_in_set))
		if current_in_plug is not None:
			plugnames = dawvert_core.input_get_plugins()
			if current_in_plug in plugnames:
				self.ui.ListWidget_InPlugin.setCurrentRow(plugnames.index(current_in_plug))
				dawvert_core.input_set(current_in_plug)

		current_out_plug = cfgsession['current_out_plug']
		current_out_set = cfgsession['current_out_set']

		if current_out_set is not None:
			plugsetlist = list(dv_core.pluginsets_output)
			if current_out_set in plugsetlist:
				self.__change_output_plugset_named(current_out_set)
				self.ui.ListWidget_OutPlugSet.setCurrentRow(plugsetlist.index(current_out_set))
		if current_out_plug is not None:
			plugnames = dawvert_core.output_get_plugins()
			if current_out_plug in plugnames:
				self.ui.ListWidget_OutPlugin.setCurrentRow(plugnames.index(current_out_plug))
				dawvert_core.output_set(current_in_plug)

		if 'input_file' in cfgsession: self.ui.InputFilePath.setText(cfgsession['input_file'])
		if 'output_file' in cfgsession: 
			self.ui.OutputFilePath.setText(cfgsession['output_file'])
			dawvert_config.main['overwrite_out'] = False
			dawvert_config.main['auto_convert'] = False
		if 'output_samples' in cfgsession: self.ui.OutputSamplePath.setText(cfgsession['output_samples'])

	def closeEvent(self, event):
		ui_o = self.ui

		dawvert_config.save_in_plugin_config()
		dawvert_config.save_out_plugin_config()

		dawvert_config.session['input_file'] = ui_o.InputFilePath.text()
		dawvert_config.session['output_file'] = ui_o.OutputFilePath.text()
		dawvert_config.session['output_samples'] = ui_o.OutputSamplePath.text()

		dawvert_config.save_file('config.json')
		event.accept()

	def translate_from_ini(self, filename):
		ui_o = self.ui

		import configparser
		config = configparser.ConfigParser()
		config.read(filename, encoding="utf8")
		if 'main' in config:
			locpart = config['main']
			if 'title' in locpart: self.setWindowTitle(locpart['title'])
			if 'convert' in locpart: ui_o.ConvertButton.setText(locpart['convert'])
			if 'group_input' in locpart: ui_o.InputGroup.setTitle(locpart['group_input'])
			if 'group_output' in locpart: ui_o.OutputGroup.setTitle(locpart['group_output'])
			if 'group_config' in locpart: ui_o.ConfigArea.setTitle(locpart['group_config'])

		if 'input' in config:
			locpart = config['input']
			if 'file' in locpart: ui_o.InputTextFile.setText(locpart['file'])
			if 'autodetect' in locpart: ui_o.AutoDetectButton.setText(locpart['autodetect'])
			if 'inputplugin' in locpart: ui_o.label_4.setText(locpart['inputplugin'])
			if 'pluginset' in locpart: ui_o.label_7.setText(locpart['pluginset'])

		if 'output' in config:
			locpart = config['output']
			if 'file' in locpart: ui_o.OutputTextFile.setText(locpart['file'])
			if 'samples' in locpart: ui_o.OutputSampleFile.setText(locpart['samples'])
			if 'outputplugin' in locpart: ui_o.label_9.setText(locpart['outputplugin'])
			if 'pluginset' in locpart: ui_o.label_8.setText(locpart['pluginset'])

		if 'configbuttons' in config:
			locpart = config['configbuttons']
			if 'main' in locpart: ui_o.ConfigMain.setText(locpart['main'])
			if 'soundfonts' in locpart: ui_o.ConfigSoundFont.setText(locpart['soundfonts'])
			if 'externalplugins' in locpart: ui_o.ConfigExtPlug.setText(locpart['externalplugins'])
			if 'conversion' in locpart: ui_o.ConfigConversion.setText(locpart['conversion'])
			if 'inputplugin' in locpart: ui_o.ConfigInput.setText(locpart['inputplugin'])
			if 'outputplugin' in locpart: ui_o.ConfigOutput.setText(locpart['outputplugin'])

		if 'configwindows' in config:
			locpart = config['configwindows']
			if 'main' in locpart: self.lab_cfg_main = locpart['main']
			if 'soundfonts' in locpart: self.lab_cfg_soundfonts = locpart['soundfonts']
			if 'externalplugins' in locpart: self.lab_cfg_externalplugins = locpart['externalplugins']
			if 'conversion' in locpart: self.lab_cfg_conversion = locpart['conversion']
			if 'inputplugin' in locpart: self.lab_cfg_inputplugin = locpart['inputplugin']
			if 'outputplugin' in locpart: self.lab_cfg_outputplugin = locpart['outputplugin']

		if 'configwindows' in config:
			locpart = config['configwindows']
			if 'main' in locpart: self.lab_cfg_main = locpart['main']
			if 'soundfonts' in locpart: self.lab_cfg_soundfonts = locpart['soundfonts']
			if 'externalplugins' in locpart: self.lab_cfg_externalplugins = locpart['externalplugins']
			if 'conversion' in locpart: self.lab_cfg_conversion = locpart['conversion']
			if 'inputplugin' in locpart: self.lab_cfg_inputplugin = locpart['inputplugin']
			if 'outputplugin' in locpart: self.lab_cfg_outputplugin = locpart['outputplugin']

		if 'statustext' in config:
			locpart = config['statustext']
			if 'main' in locpart: self.lab_stat_main = locpart['main']+' '
			if 'convert' in locpart: self.lab_stat_convert = locpart['convert']
			if 'notready' in locpart: self.lab_stat_notready = locpart['notready']
			if 'file_no_input' in locpart: self.lab_stat_file_no_input = locpart['file_no_input']
			if 'file_no_output' in locpart: self.lab_stat_file_no_output = locpart['file_no_output']
			if 'plug_no_input' in locpart: self.lab_stat_plug_no_input = locpart['plug_no_input']
			if 'plug_no_output' in locpart: self.lab_stat_plug_no_output = locpart['plug_no_output']
			if 'ow_no_input' in locpart: self.lab_stat_ow_no_input = locpart['ow_no_input']
			if 'ow_no_output' in locpart: self.lab_stat_ow_no_output = locpart['ow_no_output']
			if 'plug_dead_input' in locpart: self.lab_stat_plug_dead_input = locpart['plug_dead_input']
			if 'plug_dead_output' in locpart: self.lab_stat_plug_dead_output = locpart['plug_dead_output']
			if 'ready' in locpart: self.lab_stat_ready = locpart['ready']

		self.__update_convst()

	def open_configmenu(self, name, _):
		config_values = {}
		config_def = miniconfmenu_store()
		window_title = 'Config'

		if name=='main':
			config_values = dawvert_config.main
			config_def = configdef_main
			window_title = self.lab_cfg_main
		if name=='soundfont':
			config_values = dawvert_config.soundfont
			config_def = configdef_soundfont
			window_title = self.lab_cfg_soundfonts
		if name=='extplug':
			config_values = dawvert_config.extplug
			config_def = configdef_extplugs
			window_title = self.lab_cfg_externalplugins
		if name=='conversion':
			config_values = dawvert_config.conversion
			config_def = configdef_conversion
			window_title = self.lab_cfg_conversion
		if name=='input':
			config_values = dawvert_intent.input_params
			plugin_obj = dawvert_core.input_get_current_plug()
			if plugin_obj is not None: config_def = plugin_obj.configdef
			window_title = self.lab_cfg_inputplugin
		if name=='output':
			config_values = dawvert_intent.output_params
			plugin_obj = dawvert_core.output_get_current_plug()
			if plugin_obj is not None: config_def = plugin_obj.configdef
			window_title = self.lab_cfg_outputplugin

		if config_def is not None:
			ui_configmenu_interface.show_gui(config_def, config_values, window_title)

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls(): event.accept()
		else: event.ignore()

	def set_dd_output(self, f):
		self.ui.InputFilePath.setText(f)
		if dawvert_config.main['dd_outpath'] == 'beside_original':
			self.ui.OutputFilePath.setText(f.rsplit('.',1)[0])
			self.ui.OutputSamplePath.setText(f.rsplit('.',1)[0]+'_samples')
		if dawvert_config.main['dd_outpath'] == 'out_folder':
			outfile = os.path.join(globalstore.dawvert_script_path, 'output', os.path.basename(f))
			self.ui.OutputFilePath.setText(outfile.rsplit('.',1)[0])
			self.ui.OutputSamplePath.setText(outfile.rsplit('.',1)[0]+'_samples')
		if dawvert_config.main['dd_outpath'] == 'out_file':
			outfile = os.path.join(globalstore.dawvert_script_path, 'out')
			self.ui.OutputFilePath.setText(outfile.rsplit('.',1)[0])
			samplepath = os.path.join(globalstore.dawvert_script_path, '__samples', os.path.basename(f))
			self.ui.OutputSamplePath.setText(samplepath)

	def dropEvent(self, event):
		files = [u.toLocalFile() for u in event.mimeData().urls()]
		if files:
			self.set_dd_output(files[0])
			self.__do_auto_detect()
			self.__change_output_path()
			if dawvert_config.main['auto_convert']:
				if self.__can_convert(): self.__do_convert()

	def __change_dd_setting(self, num):
		dawvert_config.main['dd_outpath'] = num

	def __change_overwrite_setting(self, val):
		dawvert_config.main['overwrite_out'] = val
		self.__update_convst()

	def __change_auto_convert_setting(self, val):
		dawvert_config.main['auto_convert'] = val

	def __choose_input(self):
		filename, _filter = QFileDialog.getOpenFileName(self, "Open File", "", "")
		self.ui.InputFilePath.setText(filename)

	def __choose_output(self):
		filename, _filter = QFileDialog.getSaveFileName(self, "Save File", "", "")
		self.ui.OutputFilePath.setText(filename)

	def __choose_samples(self):
		filename, _filter = QFileDialog.getSaveFileName(self, "Save File", "", "")
		self.ui.OutputSamplePath.setText(filename)

	def __do_auto_detect(self):
		filename = self.ui.InputFilePath.text()
		if os.path.exists(filename):
			try:
				plugsetlist = list(dv_core.pluginsets_input)
				outdetected = filedetector_obj.detect_file(filename)
				if outdetected:
					plugset, plugname = outdetected
					self.__change_input_plugset_named(plugset)
					self.ui.ListWidget_InPlugSet.setCurrentRow(plugsetlist.index(plugset))
					plugnames = dawvert_core.input_get_plugins()
					self.ui.ListWidget_InPlugin.setCurrentRow(plugnames.index(plugname))
					dawvert_core.input_set(plugname)
					return True
				return False
			except:
				pass

	def __can_convert(self):
		dawvert_intent.set_file_input(self.ui.InputFilePath.text().replace('/', '\\'))
		dawvert_intent.set_file_output(self.ui.OutputFilePath.text().replace('/', '\\'))
		inplug = dawvert_core.input_get_current()
		outplug = dawvert_core.output_get_current()
		not_same = dawvert_intent.input_file!=dawvert_intent.output_file
		out_exists = (not os.path.exists(dawvert_intent.output_file)) or dawvert_config.main['overwrite_out']
		in_usable, in_usable_msg = dawvert_core.input_get_usable()
		out_usable, out_usable_msg = dawvert_core.output_get_usable()
		return bool(inplug and outplug and not_same and out_exists and in_usable and out_usable)

	def __update_convst(self):
		dawvert_intent.input_file = self.ui.InputFilePath.text().replace('/', '\\')
		dawvert_intent.output_file = self.ui.OutputFilePath.text().replace('/', '\\')
		inplug = dawvert_core.input_get_current()
		outplug = dawvert_core.output_get_current()
		not_same = dawvert_intent.input_file!=dawvert_intent.output_file
		out_exists = (not os.path.exists(dawvert_intent.output_file)) or dawvert_config.main['overwrite_out']
		in_usable, in_usable_msg = dawvert_core.input_get_usable()
		out_usable, out_usable_msg = dawvert_core.output_get_usable()
		outstate = bool(inplug and outplug and not_same and out_exists and in_usable and out_usable)

		self.ui.ConvertButton.setEnabled(outstate and not converterstate.is_converting)
		if converterstate.is_converting: 
			self.ui.StatusText.setText('Status: Converting')
			self.ui.SubStatusText.setText('')
			return False
		elif not outstate:
			if not DEBUG_VIEW: self.ui.StatusText.setText(self.lab_stat_main+self.lab_stat_notready)
			else: self.ui.StatusText.setText(self.lab_stat_main+self.lab_stat_notready+' (DEBUG VIEW ON)')
			if not dawvert_intent.input_file: self.ui.SubStatusText.setText(self.lab_stat_file_no_input)
			elif not dawvert_intent.output_file: self.ui.SubStatusText.setText(self.lab_stat_file_no_output)
			elif not inplug: self.ui.SubStatusText.setText(self.lab_stat_plug_no_input)
			elif not outplug: self.ui.SubStatusText.setText(self.lab_stat_plug_no_output)
			elif not not_same: self.ui.SubStatusText.setText(self.lab_stat_ow_no_input)
			elif not out_exists: self.ui.SubStatusText.setText(self.lab_stat_ow_no_output)
			elif not in_usable: 
				self.ui.StatusText.setText(self.lab_stat_plug_dead_input)
				self.ui.SubStatusText.setText(in_usable_msg)
			elif not out_usable: 
				self.ui.StatusText.setText(self.lab_stat_plug_dead_output)
				self.ui.SubStatusText.setText(out_usable_msg)
			return False
		else:
			if not DEBUG_VIEW: self.ui.StatusText.setText(self.lab_stat_main+self.lab_stat_ready)
			else: self.ui.StatusText.setText(self.lab_stat_main+self.lab_stat_ready+' (DEBUG VIEW ON)')
			self.ui.SubStatusText.setText('')
			return True


	def __change_input_plugset_named(self, plugsetname):
		dawvert_core.input_load_plugins(plugsetname)
		self.__update_input_plugins()
		self.__change_input_plugin(0)

	def __change_input_plugset(self, num):
		plugsetname = dawvert_core.input_get_pluginsets_index(num)
		dawvert_core.input_load_plugins(plugsetname)
		self.__update_input_plugins()
		self.__change_input_plugin(0)
		dawvert_config.session['current_in_set'] = plugsetname

	def __change_input_plugin(self, num):
		dawvert_config.save_in_plugin_config()

		pluginname = dawvert_core.input_get_plugins_index(num)
		if pluginname: dawvert_core.input_set(pluginname)
		else: 
			plugnames = dawvert_core.input_get_plugins()
			if plugnames: dawvert_core.input_set(plugnames[0])
		self.__update_convst()
		dawvert_config.get_in_plugin_config()

	def __change_input_plugin_nofb(self, num):
		dawvert_config.save_in_plugin_config()

		pluginname = dawvert_core.input_get_plugins_index(num)
		if pluginname: dawvert_core.input_set(pluginname)
		self.__update_convst()
		dawvert_config.get_in_plugin_config()

	def __update_input_plugins(self):
		self.ui.ListWidget_InPlugin.clear()
		if not DEBUG_VIEW:
			for x in dawvert_core.input_get_plugins_names():
				self.ui.ListWidget_InPlugin.addItem(x)
		else:
			props = dawvert_core.input_get_plugins_props()
			for n, x in enumerate(dawvert_core.input_get_plugins_names()):
				o = x
				fxt = debugtxt(props[n].fxtype)
				fdt = props[n].projtype.upper()
				if DEBUG_VIEW == 1: o = ('[%s] ' % fxt)+o
				if DEBUG_VIEW == 2: o = ('[%s] ' % fdt)+o
				if DEBUG_VIEW == 3: o = ('[%s:%s] ' % (fxt, fdt)+o)
				self.ui.ListWidget_InPlugin.addItem(o)

	def __change_output_plugset_named(self, plugsetname):
		dawvert_core.output_load_plugins(plugsetname)
		self.__update_output_plugins()
		self.__change_output_plugin(0)

	def __change_output_plugset(self, num):
		plugsetname = dawvert_core.output_get_pluginsets_index(num)
		dawvert_core.output_load_plugins(plugsetname)
		self.__update_output_plugins()
		self.__change_output_path()
		dawvert_config.session['current_out_set'] = plugsetname

	def __change_output_plugin(self, num):
		dawvert_config.save_out_plugin_config()

		pluginname = dawvert_core.output_get_plugins_index(num)
		if pluginname: dawvert_core.output_set(pluginname)
		self.__update_convst()
		self.__change_output_path()

		dawvert_config.get_out_plugin_config()

	def __change_output_path(self):
		outfound = dawvert_core.output_get_current()
		filename = self.ui.OutputFilePath.text()
		if outfound and filename:
			try:
				fileext = dawvert_core.output_get_extension()
				filename = Path(filename)
				filename = filename.with_suffix('.'+fileext)
				self.ui.OutputFilePath.setText(str(filename))
			except:
				pass
		self.__update_convst()

	def __update_output_plugins(self):
		self.ui.ListWidget_OutPlugin.clear()
		if not DEBUG_VIEW:
			for x in dawvert_core.output_get_plugins_names():
				self.ui.ListWidget_OutPlugin.addItem(x)
		else:
			props = dawvert_core.output_get_plugins_props()
			for n, x in enumerate(dawvert_core.output_get_plugins_names()):
				o = x
				fxt = debugtxt(props[n].fxtype)
				fdt = props[n].projtype.upper()
				if DEBUG_VIEW == 1: o = ('[%s] ' % fxt)+o
				if DEBUG_VIEW == 2: o = ('[%s] ' % fdt)+o
				if DEBUG_VIEW == 3: o = ('[%s:%s] ' % (fxt, fdt)+o)
				self.ui.ListWidget_OutPlugin.addItem(o)


	def __update_ui_ele(self, n):
		update_type, update_data = n
		if update_type == 0:
			self.ui.SubStatusText.setText(update_data)
		if update_type == 1:
			self.ui.progressBar.setValue(update_data)
		if update_type == 2:
			self.ui.StatusText.setText('Status: '+update_data[0])
			self.ui.SubStatusText.setText(update_data[1])

	def __do_convert(self):
		if not converterstate.is_converting:
			converterstate.is_converting = True
			self.__update_convst()

			dawvert_intent.input_file = self.ui.InputFilePath.text()
			dawvert_intent.output_file = self.ui.OutputFilePath.text()
			dawvert_intent.output_samples = self.ui.OutputSamplePath.text()
	
			self.thread = QtCore.QThread(parent=self)
			self.worker = ConversionWorker()
			self.worker.moveToThread(self.thread)
			self.thread.started.connect(self.worker.run)
			self.worker.finished.connect(self.thread.quit)
			self.worker.finished.connect(self.worker.deleteLater)
			self.thread.finished.connect(self.thread.deleteLater)
			self.worker.update_ui.connect(self.__update_ui_ele)
			self.thread.start()

dawvert_config.load_file('config.json')
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
if 'language' in dawvert_config.main: window.translate_from_ini('translation/%s.ini' % dawvert_config.main['language'])
window.show()
app.exec()