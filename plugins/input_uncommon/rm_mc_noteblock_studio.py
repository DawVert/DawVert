# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import math
import plugins
import os

from objects import globalstore
from functions import xtramath

import logging
logger_input = logging.getLogger('input')

class external_data_zip():
	def __init__(self):
		self.zipfile = None

	def load_data(self, input_file):
		import zipfile
		try: zip_data = zipfile.ZipFile(input_file, 'r')
		except zipfile.BadZipFile as t: 
			logger_input.warning('mnbs: extdata: Bad ZIP File: '+str(t))
		self.zipfile = zip_data

	def extract(self, arch_file, out_file):
		if self.zipfile:
			try: 
				self.zipfile.extract(arch_file, path=out_file, pwd=None)
				logger_input.info('mnbs: extdata: extracted '+arch_file+' as '+out_file)
			except: 
				logger_input.warning('mnbs: extdata: error extracting file: '+arch_file)

class input_gt_mnbs(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'mnbs'
	
	def get_name(self):
		return 'Minecraft Note Block Studio'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:sampler:single', 'universal:midi']
		in_dict['projtype'] = 'rm'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import nbs as proj_nbs
		from objects.convproj import fileref

		convproj_obj.type = 'rm'
		convproj_obj.set_timings(4.0)
		
		traits_obj = convproj_obj.traits
		traits_obj.track_nopl = True
		traits_obj.audio_filetypes = ['wav']

		project_obj = proj_nbs.nbs_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		external_dat = external_data_zip()
		external_dat.load_data(os.path.join(dawvert_intent.path_external_data, 'mnbs', 'samples.zip'))

		globalstore.datapack.load('noteblockstudio', './data/datapack/app/noteblockstudio.xml')

		tempo = (project_obj.tempo/800)*120

		outtempo, notelen = xtramath.get_lower_tempo(tempo, 1, 180)

		convproj_obj.metadata.name = project_obj.name
		convproj_obj.metadata.author = project_obj.author
		convproj_obj.metadata.original_author = project_obj.orgauthor
		convproj_obj.metadata.comment_text = project_obj.description
		convproj_obj.params.add('bpm', outtempo, 'float')
		convproj_obj.timesig = [project_obj.numerator, 4]

		used_inst = []

		for nbs_layer, layer_obj in enumerate(project_obj.layers):
			cvpj_trackid = str(nbs_layer+1)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'instruments', 1, False)
			track_obj.visual.name = layer_obj.name if layer_obj.name else 'Layer #'+cvpj_trackid
			track_obj.params.add('vol', layer_obj.vol/100, 'float')
			track_obj.params.add('pan', (layer_obj.stereo/100)-1, 'float')

			cvpj_notelist = track_obj.placements.notelist

			for note_obj in layer_obj.notes: 
				if note_obj.inst not in used_inst:
					if note_obj.inst<16:
						used_inst.append(note_obj.inst)
				cvpj_notelist.add_m('NoteBlock'+str(note_obj.inst), note_obj.pos*notelen, 2*notelen, note_obj.key-39, note_obj.vel/100, None)
				if note_obj.pan!=100: cvpj_notelist.last_add_pan((note_obj.pan/100)-1)
				if note_obj.pitch: cvpj_notelist.last_add_finepitch(note_obj.pitch)

		for instnum in used_inst:
			instid = 'NoteBlock'+str(instnum)
			inst_obj = convproj_obj.instrument__add(instid)
			dpobj = globalstore.datapack.get_obj('noteblockstudio', 'inst', str(instnum))
			if dpobj:
				inst_obj.visual.from_datapack_obj(dpobj, True)

				plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'single')
				plugin_obj.role = 'synth'
				plugin_obj.midi_incompat_synth_on = True
				plugin_obj.midi_incompat_synth.from_datapack_obj(dpobj)

				if 'audiofile' in dpobj.data:
					wavfile = dpobj.data['audiofile']
					outfile = os.path.join(dawvert_intent.path_samples['extracted'], wavfile)
					external_dat.extract(wavfile, outfile)

					sampleref_obj = convproj_obj.sampleref__add(wavfile, outfile, None)

					samplepart_obj = plugin_obj.samplepart_add('sample')
					samplepart_obj.sampleref = wavfile
					inst_obj.plugslots.set_synth(pluginid)
					inst_obj.datavals.add('middlenote', 6)

		custominstid = 16
		for custominstid, custom_obj in enumerate(project_obj.custom):
			instid = 'NoteBlock'+str(custominstid+16)
			inst_obj = convproj_obj.instrument__add(instid)
			inst_obj.visual.name = custom_obj.name
			inst_obj.visual.color.set_hsv(custominstid*0.2, 1, 0.5)
			inst_obj.datavals.add('middlenote', -(custom_obj.key-51))
			plugin_obj, sampleref_obj, samplepart_obj = convproj_obj.plugin__addspec__sampler(instid, custom_obj.file, None)
			if sampleref_obj: 
				sampleref_obj.search_local(dawvert_intent.input_folder)
			plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 10, 1)
			inst_obj.plugslots.set_synth(instid)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')