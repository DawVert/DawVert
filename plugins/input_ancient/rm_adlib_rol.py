# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os

from objects import globalstore

class input_adlib_rol(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'adlib_rol'
	
	def get_name(self):
		return 'AdLib Visual Composer'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['chip:fm:opl2']
		in_dict['projtype'] = 'rm'

	def get_configdef(self, configdef):
		configdef.add_file_open('bank_file', '', 'Bank File')
		configdef.set_group('visual', 'Visual')
		configdef.add_bool('keep_def_name', False, 'Keep Default Track Names')

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_adlib import rol as proj_adlib_rol
		from objects.file import adlib_bnk

		project_obj = proj_adlib_rol.adlib_rol_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.datapack.load('adlib_rol', './data/datapack/app/adlib_rol.xml')

		# ---------- bank file ----------
		native_insts = {}
		bank_file = dawvert_intent.input_get_param('bank_file', '')
		if bank_file:
			if os.path.exists(bank_file):
				adlibbnk_obj = adlib_bnk.bnk_file()
				adlibbnk_obj.read_file(bank_file)
				for instnum, used in enumerate(adlibbnk_obj.used):
					if used:
						instname = adlibbnk_obj.names[instnum].replace(" ", "").upper()
						native_insts[instname] = adlibbnk_obj.get_inst_index(instnum)

		keep_def_name = dawvert_intent.input_get_param('keep_def_name', '')

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks
		cvpj_insts = convproj_obj.instruments
		cvpj_automation = convproj_obj.automation
		
		# ---------- convproj params ----------
		convproj_obj.type = 'rm'
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.set_timings(project_obj.tickBeat)

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.track_nopl = True

		# ---------- transport ----------
		convproj_obj.timesig = [project_obj.beatMeasure, 4]

		bpm = project_obj.track_tempo.tempo
		convproj_obj.params.add('bpm', bpm, 'float')
		for pos, bpmmod in project_obj.track_tempo.events: 
			cvpj_automation.add_autotick(['main', 'bpm'], 'float', pos, bpmmod*bpm)

		# ---------- tracks ----------
		used_voices = []
		for tracknum, rol_track in enumerate(project_obj.tracks):
			cvpj_trackid = 'track'+str(tracknum+1)
			track_obj = cvpj_tracks.add(cvpj_trackid, 'instruments', 0, False)

			if (rol_track.voice.name!='Voix  %i'%tracknum) or keep_def_name:
				track_obj.visual.name = rol_track.voice.name
			elif not project_obj.isMelodic:
				if 5>tracknum: track_obj.visual.name = 'Melodic #%i'%(tracknum+1)
				elif tracknum==5: track_obj.visual.name = 'Bass Drum'
				elif tracknum==6: track_obj.visual.name = 'Snare Drum'
				elif tracknum==7: track_obj.visual.name = 'Tom Tom'
				elif tracknum==8: track_obj.visual.name = 'Top Cymbal'
				elif tracknum==9: track_obj.visual.name = 'Hi-Hat'

			cvpj_notelist = track_obj.placements.notelist
			
			curtrackpos = 0
			for note, pos in rol_track.voice.events:
				if note >= 12: cvpj_notelist.add_m(None, curtrackpos, pos, note-48-12, 1, None)
				curtrackpos += pos

			upper_timbre = [[i, p.upper()] for i, p in rol_track.timbre.events.copy()]
			cvpj_notelist.add_instpos(upper_timbre)

			for x in upper_timbre:
				if x[1] not in used_voices: used_voices.append(x[1])

			for pos, val in rol_track.volume.events: cvpj_automation.add_autotick(['track', cvpj_trackid, 'vol'], 'float', pos, val)
			for pos, val in rol_track.pitch.events: cvpj_automation.add_autotick(['track', cvpj_trackid, 'pitch'], 'float', pos, val)

		# ---------- insts ----------
		for used_voice in used_voices:
			instname_upper = used_voice.upper()
			inst_obj = cvpj_insts.add(instname_upper)
			inst_obj.visual.name = instname_upper
			inst_obj.visual.from_datapack('adlib_rol', 'inst', instname_upper, True)
			if instname_upper in native_insts:
				opli = native_insts[instname_upper]
				plugin_obj = opli.to_cvpj(convproj_obj, instname_upper)
				plugin_obj.midi_fallback__add_from_datapack('adlib_rol', 'inst', instname_upper)
				plugin_obj.midi_fallback__to_vis(inst_obj.visual, False)
			else:
				plugin_obj = convproj_obj.plugin__add(instname_upper, 'universal', 'midi', None)
				plugin_obj.midi.from_datapack('adlib_rol', 'inst', instname_upper)
				plugin_obj.midi.to_visual(inst_obj.visual, False)
			inst_obj.plugslots.set_synth(instname_upper)
