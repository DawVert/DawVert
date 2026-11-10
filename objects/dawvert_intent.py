# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os

class dawvert_intent:
	def __init__(self):
		self.dir_scriptfile = ''

		self.input_file = ''
		self.input_folder = ''
		self.input_data = b''
		self.input_mode = 'file'
		self.input_visname = ''
		self.input_params = {}
		self.input_dawinfo = None
		
		self.output_file = ''
		self.output_folder = ''
		self.output_mode = 'file'
		self.output_params = {}
		self.output_visname = ''
		self.output_samples = ''
		self.output_dawinfo = None

		self.convert_params = {}

		self.curdir = None

		self.plugin_set = True
		self.plugin_input = None
		self.plugin_output = None
		self.plugset_input = None
		self.plugset_output = None

		self.path_samples = {}
		self.path_soundfonts = {}
		self.path_external_data = ''

		self.splitter_mode = 'timesig'
		self.splitter_detect_start = 0

		self.flags_compat = []
		self.flag_overwrite = False

		self.extplug_cat = []
		self.songnum = 0

		self.custom_config = {}

		self.download_enabled = True

		self.set_defualt_path()

		self.debug_flags = []

	def input_get_param(self, name, fallback):
		return self.input_params[name] if name in self.input_params else fallback

	def output_get_param(self, name, fallback):
		return self.output_params[name] if name in self.output_params else fallback

	def convert_get_param(self, name, fallback):
		return self.convert_params[name] if name in self.convert_params else fallback

	def copy(self):
		return copy.deepcopy(self)

	def set_file_input(self, fileloc):
		if self.curdir: self.curdir = os.getcwd()
		self.input_mode = 'file'
		self.input_file = os.path.abspath(fileloc)
		self.input_folder = os.path.dirname(self.input_file)
		self.input_visname = os.path.basename(fileloc)
		self.input_visname = os.path.splitext(self.input_visname)[0]

	def set_file_output(self, fileloc):
		if self.curdir: self.curdir = os.getcwd()
		self.output_mode = 'file'
		self.output_file = os.path.abspath(fileloc)
		self.output_folder = os.path.dirname(self.output_file)
		self.output_visname = os.path.basename(fileloc)
		self.output_visname = os.path.splitext(self.output_visname)[0]

	def set_defualt_path(self):
		self.path_samples['extracted'] = os.getcwd() + '/__samples_extracted/'
		self.path_samples['downloaded'] = os.getcwd() + '/__samples_downloaded/'
		self.path_samples['generated'] = os.getcwd() + '/__samples_generated/'
		self.path_samples['converted'] = os.getcwd() + '/__samples_converted/'
		self.path_samples['global_downloaded'] = os.getcwd() + '/__downloaded/'

	def set_projname_path(self):
		file_name = self.input_visname
		self.set_defualt_path()
		self.path_samples['extracted'] += file_name + '/'
		self.path_samples['downloaded'] += file_name + '/'
		self.path_samples['generated'] += file_name + '/'
		self.path_samples['converted'] += file_name + '/'

	def create_folder_paths(self):
		os.makedirs(self.path_samples['extracted'], exist_ok=True)
		os.makedirs(self.path_samples['downloaded'], exist_ok=True)
		os.makedirs(self.path_samples['generated'], exist_ok=True)
		os.makedirs(self.path_samples['converted'], exist_ok=True)
		os.makedirs(self.path_samples['global_downloaded'], exist_ok=True)

	def do_fileref_global(self, convproj_obj):
		folder_prefixes = convproj_obj.folder_prefixes
		folder_prefixes.add('root', self.dir_scriptfile)
		folder_prefixes.add('project', self.input_folder)

		folder_prefixes.add('extracted', self.path_samples['extracted'])
		folder_prefixes.add('downloaded', self.path_samples['downloaded'])
		folder_prefixes.add('generated', self.path_samples['generated'])
		folder_prefixes.add('converted', self.path_samples['converted'])
		folder_prefixes.add('global_downloaded', self.path_samples['global_downloaded'])

		folder_prefixes.add('extdata', os.path.join(self.dir_scriptfile, '__external_data'))