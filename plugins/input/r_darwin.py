# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json

def do_track_visual(dw_track, visual_obj):
	visual_obj.name = dw_track.name
	visual_obj.color.set_hex(dw_track.color)

def do_track_params(dw_track, params_obj):
	params_obj.add('enabled', not dw_track.muted, 'bool')
	params_obj.add('solo', dw_track.solo, 'bool')
	params_obj.add('vol', dw_track.volume, 'float')
	params_obj.add('pan', dw_track.pan, 'float')

class input_darwin(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'darwin'
	
	def get_name(self):
		return 'Darwin'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import darwin as proj_darwin

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'

		traits_obj = convproj_obj.traits
		traits_obj.audio_stretch = []
		traits_obj.auto_types = []
		traits_obj.placement_cut = False
		traits_obj.placement_loop = []
		traits_obj.time_seconds = False

		convproj_obj.set_timings(480)

		project_obj = proj_darwin.darwin_project()

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
		convproj_obj.metadata.name = project_obj.name

		track_master = convproj_obj.track_master
		do_track_params(project_obj.masterTrack, track_master.params)
		do_track_visual(project_obj.masterTrack, track_master.visual)

		for dw_track in project_obj.tracks:
			if not dw_track.isFolder:
				track_obj = convproj_obj.track__add(str(dw_track.id), 'instrument', 1, False)
				if dw_track.parentFolderId>1: track_obj.group = str(dw_track.parentFolderId)
				do_track_params(dw_track, track_obj.params)
				do_track_visual(dw_track, track_obj.visual)
				for dw_clip in dw_track.clips:
					if dw_clip.clipType=='midi':
						placement_obj = track_obj.placements.add_notes()
						time_obj = placement_obj.time
						time_obj.set_posdur(dw_clip.startTick, dw_clip.durationTicks)
						cvpj_notelist = placement_obj.notelist
						for note in dw_clip.notes:
							cvpj_notelist.add_r(note.startTick, note.durationTicks, note.pitch-60, note.velocity/127, None)
			else:
				track_obj = convproj_obj.fx__group__add(str(dw_track.id))
				track_obj.visual_track.group_expanded = bool(dw_track.folderExpanded)
				do_track_params(dw_track, track_obj.params)
				do_track_visual(dw_track, track_obj.visual)
