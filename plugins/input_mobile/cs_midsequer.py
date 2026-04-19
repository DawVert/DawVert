# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import xtramath
from objects.convproj import fileref

class input_coolbeat(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'midsequer'
	
	def get_name(self):
		return 'Midsequer'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:soundfont2']
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_mobile import midsequer

		project_obj = midsequer.midsequer_project()

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'cs'

		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.track_nopl = True

		convproj_obj.set_timings(24)

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		master = project_obj.sng.data.mstr
		convproj_obj.params.add('bpm', master.tempo, 'float')
		convproj_obj.timesig_auto.add_point(0, master.tim_sig)

		for n, track in enumerate(project_obj.sng.data.tracks):
			trackinfo = track.ini
			trackevents = track.evts
			if (trackinfo.volume!=100) or (trackinfo.inst_pc!=0) or len(trackevents):
				track_obj = convproj_obj.track__add(str(n), 'midi', 1, False)
				track_obj.midi.out_enabled = True
				track_obj.midi.out_chanport.chan = n
				track_obj.midi.out_chanport.port = 0

				events_obj = track_obj.placements.midievents
				events_obj.add_program(0, n,trackinfo.inst_pc)
				events_obj.add_control(0, n, 7, trackinfo.volume)
				events_obj.has_duration = True

				for e in trackevents:
					if isinstance(e, midsequer.midsequer_event_note):
						events_obj.add_note_dur(e.time, n, e.note, e.vel, e.dur)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')