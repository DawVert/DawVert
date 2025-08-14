# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_musicphrase(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'musicphrase'
	
	def get_name(self):
		return 'MusicPhrase XL'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'cs'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import musicphrase as proj_musicphrase

		project_obj = proj_musicphrase.musicphrase_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.set_timings(96)

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'cs'

		metadata_obj = convproj_obj.metadata

		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']

		track_pl = []
		for n, mpxl_track in enumerate(project_obj.tracks):
			track_obj = convproj_obj.track__add(str(n), 'midi', 1, False)
			track_obj.visual.name = mpxl_track.name
			track_obj.visual.color.set_int(list(mpxl_track.color[0:3]))

			track_obj.midi.out_enabled = True
			track_obj.midi.out_chanport.chan = mpxl_track.channel
			track_obj.midi.out_chanport.port = 0

			if mpxl_track.program != -1:
				track_obj.midi.out_inst.patch = mpxl_track.program

			for clip in mpxl_track.clips:
				placement_obj = track_obj.placements.add_midi()
				placement_obj.visual.name = clip.name
				placement_obj.visual.color.set_int(list(clip.color[0:3]))
				placement_obj.time.set_posdur(clip.start, clip.size)

				channel = mpxl_track.channel

				events_obj = placement_obj.midievents
				events_obj.has_duration = True
				events_obj.ppq = 96
				for note in clip.notes:
					events_obj.add_note_dur(note.pos, channel, note.note, note.vel, max(0, note.end-note.pos))

				for ctrl in clip.ctrls:
					event_type = ctrl.type
					if event_type == 10: events_obj.add_note_pressure(ctrl.pos, channel, ctrl.data1, ctrl.data2)
					elif event_type == 11: events_obj.add_control(ctrl.pos, channel, ctrl.data1, ctrl.data2)
					elif event_type == 12: events_obj.add_program(ctrl.pos, channel, ctrl.data1)
					elif event_type == 13: events_obj.add_chan_pressure(ctrl.pos, channel, ctrl.data1)
					elif event_type == 14: events_obj.add_pitch_hi_lo(ctrl.pos, channel, ctrl.data2, ctrl.data1)