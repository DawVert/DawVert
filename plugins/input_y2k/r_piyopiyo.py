# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import struct
import os.path
from objects import globalstore
import zipfile

import logging
logger_input = logging.getLogger('input')

alt_drum_note_map = {
	0: [1.0, 0],
	1: [0.6, 0],
	2: [1.0, 1],
	3: [0.6, 1],
	4: [1.0, 2],
	5: [0.6, 2],
	8: [1.0, 3],
	9: [0.6, 3],
	10: [1.0, 4],
	11: [0.6, 4],
	12: [1.0, 5],
	13: [0.6, 5]
}

def parse_notes(convproj_obj, trackid, notes_data, track_obj, keyoffset):
	cvpj_notelist = track_obj.placements.notelist
	for pos, nd in enumerate(notes_data):
		notes, pan = nd
		cvpj_notelist.add_r_multi(pos, 1, [(x+keyoffset)-12 for x in notes], 1, None)
		if pan != 0: convproj_obj.automation.add_autotick(['track', trackid, 'pan'], 'float', pos, (pan-4)/3)
	cvpj_notelist.sort()

def parse_notes_drumalt(convproj_obj, trackid, notes_data, track_obj):
	cvpj_notelist = track_obj.placements.notelist
	for pos, nd in enumerate(notes_data):
		notes, pan = nd
		for x in notes:
			if x in alt_drum_note_map: 
				vol, key = alt_drum_note_map[x]
				cvpj_notelist.add_r(pos, 1, key, vol, None)
		if pan != 0: convproj_obj.automation.add_autotick(['track', trackid, 'pan'], 'float', pos, (pan-4)/3)
	cvpj_notelist.sort()

class external_data_zip():
	def __init__(self):
		self.zipfile = None

	def load_data(self, input_file):
		import zipfile
		try: zip_data = zipfile.ZipFile(input_file, 'r')
		except zipfile.BadZipFile as t: 
			logger_input.warning('piyopiyo: extdata: Bad ZIP File: '+str(t))
		self.zipfile = zip_data

	def extract(self, arch_file, out_file):
		if self.zipfile:
			try: 
				self.zipfile.extract(arch_file, path=out_file, pwd=None)
				logger_input.info('piyopiyo: extdata: extracted '+arch_file+' as '+out_file)
			except: 
				logger_input.warning('piyopiyo: extdata: error extracting file: '+arch_file)

class input_piyopiyo(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'piyopiyo'
	
	def get_name(self):
		return 'PiyoPiyo'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:synth-osc','universal:sampler:multi']
		in_dict['projtype'] = 'r'

	def get_configdef(self, configdef):
		configdef.add_bool('use_samples', True, 'Use Drum Samples')
		configdef.add_bool('drum_notes_alt', True, 'Alternate Drum Notes')

	def parse(self, convproj_obj, dawvert_intent):
		from objects import colors
		from objects.file_proj_past import piyopiyo as proj_piyopiyo

		project_obj = proj_piyopiyo.piyopiyo_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		from objects.convproj import fileref
		fileref.cvpj_fileref_global.add_prefix_extend('dawvert_external_data', 'piyopiyo_wav', ['piyopiyo'])

		globalstore.datapack.load('piyopiyo', './data/datapack/app/piyopiyo.xml')
		colordata = colors.colorset.from_datapack('piyopiyo', 'inst', 'main')

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks

		# ---------- convproj params ----------
		use_samples = dawvert_intent.input_get_param('use_samples', True)
		drum_notes_alt = dawvert_intent.input_get_param('drum_notes_alt', True)

		# ---------- convproj init ----------
		convproj_obj.type = 'r'
		convproj_obj.set_timings(4)
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.track_nopl = True

		# ---------- transport ----------
		convproj_obj.params.add('bpm', (120/project_obj.musicwait)*120, 'float')
		convproj_obj.transport.loop_active = True
		convproj_obj.transport.loop_start = project_obj.loopstart
		convproj_obj.transport.loop_end = project_obj.loopend

		# ---------- melody tracks ----------
		for tracknum in range(3):
			pmdtrack_obj = project_obj.tracks[tracknum]
			keyoffset = (pmdtrack_obj.octave-2)*12

			idval = str(tracknum)
			track_obj = cvpj_tracks.add(idval, 'instrument', 0, False)
			track_obj.visual.name = 'Inst #'+str(tracknum+1)
			track_obj.visual.color.set_int(colordata.getcolornum(tracknum))
			track_obj.params.add('vol', pmdtrack_obj.volume/250, 'float')

			plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'single')
			plugin_obj.role = 'synth'
			osc_data = plugin_obj.osc_add()
			osc_data.prop.type = 'wave'
			osc_data.prop.nameid = 'main'
			wave_obj = plugin_obj.wave_add('main')
			wave_obj.set_all_range(pmdtrack_obj.waveform, -128, 128)
			plugin_obj.env_blocks_add('vol', pmdtrack_obj.envelope, 1/64, 128, None, None)
			plugin_obj.env_points_from_blocks('vol')
			track_obj.plugslots.set_synth(pluginid)
			parse_notes(convproj_obj, idval, project_obj.notes_data[tracknum], track_obj, keyoffset)

		# ---------- drum track ----------
		track_obj = cvpj_tracks.add("3", 'instrument', False, False)
		track_obj.visual.name = 'Drums'
		track_obj.visual.color.set_int(colordata.getcolornum(3))
		track_obj.params.add('vol', (project_obj.perc_volume/250)/3, 'float')
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'drums')
		plugin_obj.role = 'synth'
		track_obj.is_drum = True
		track_obj.plugslots.set_synth(pluginid)

		if use_samples:
			try:
				external_dat = external_data_zip()
				external_dat.load_data(os.path.join(dawvert_intent.path_external_data, 'piyopiyo', 'piyopiyo.zip'))

				for sampname in ['BASS1', 'BASS2', 'SNARE1', 'HAT1', 'HAT2', 'SYMBAL1']:
					sampid = 'PIYOPIYO_%s' % sampname
					wavfilename = sampname+'.wav'
					outfile = os.path.join(dawvert_intent.path_samples['extracted'], wavfilename)
					external_dat.extract(wavfilename, outfile)
					sampleref_obj = convproj_obj.sampleref__add(sampname, outfile, None)
					sp_obj = plugin_obj.samplepart_add(sampid)
					sp_obj.sampleref = sampname
			except FileNotFoundError:
				logger_input.warning('piyopiyo: extdata: ZIP file missing.')

		if not drum_notes_alt:
			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = -12
			drumpad_obj.visual.name = 'Bass 1'
			layer_obj.samplepartid = 'PIYOPIYO_BASS1'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = -11
			drumpad_obj.vol = 0.6
			drumpad_obj.visual.name = 'Bass 1'
			layer_obj.samplepartid = 'PIYOPIYO_BASS1'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = -10
			drumpad_obj.visual.name = 'Bass 2'
			layer_obj.samplepartid = 'PIYOPIYO_BASS2'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = -9
			drumpad_obj.vol = 0.6
			drumpad_obj.visual.name = 'Bass 2'
			layer_obj.samplepartid = 'PIYOPIYO_BASS2'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = -8
			drumpad_obj.visual.name = 'Snare'
			layer_obj.samplepartid = 'PIYOPIYO_SNARE1'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = -7
			drumpad_obj.vol = 0.6
			drumpad_obj.visual.name = 'Snare'
			layer_obj.samplepartid = 'PIYOPIYO_SNARE1'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = -4
			drumpad_obj.visual.name = 'Hat 1'
			layer_obj.samplepartid = 'PIYOPIYO_HAT1'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = -3
			drumpad_obj.vol = 0.6
			drumpad_obj.visual.name = 'Hat 1'
			layer_obj.samplepartid = 'PIYOPIYO_HAT1'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = -2
			drumpad_obj.visual.name = 'Hat 2'
			layer_obj.samplepartid = 'PIYOPIYO_HAT2'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = -1
			drumpad_obj.vol = 0.6
			drumpad_obj.visual.name = 'Hat 2'
			layer_obj.samplepartid = 'PIYOPIYO_HAT2'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = 0
			drumpad_obj.visual.name = 'Symbal'
			layer_obj.samplepartid = 'PIYOPIYO_SYMBAL1'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = 1
			drumpad_obj.vol = 0.6
			drumpad_obj.visual.name = 'Symbal'
			layer_obj.samplepartid = 'PIYOPIYO_SYMBAL1'

			parse_notes(convproj_obj, '3', project_obj.notes_data[3], track_obj, 0)
		else:
			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = 0
			drumpad_obj.visual.name = 'Bass 1'
			layer_obj.samplepartid = 'PIYOPIYO_BASS1'

			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = 1
			drumpad_obj.visual.name = 'Bass 2'
			layer_obj.samplepartid = 'PIYOPIYO_BASS2'
			
			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = 2
			drumpad_obj.visual.name = 'Snare'
			layer_obj.samplepartid = 'PIYOPIYO_SNARE1'
			
			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = 3
			drumpad_obj.visual.name = 'Hat 1'
			layer_obj.samplepartid = 'PIYOPIYO_HAT1'
			
			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = 4
			drumpad_obj.visual.name = 'Hat 2'
			layer_obj.samplepartid = 'PIYOPIYO_HAT2'
			
			drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
			drumpad_obj.key = 5
			drumpad_obj.visual.name = 'Symbal'
			layer_obj.samplepartid = 'PIYOPIYO_SYMBAL1'
			
			parse_notes_drumalt(convproj_obj, '3', project_obj.notes_data[3], track_obj)
