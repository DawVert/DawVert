# SPDX-FileCopyrightText: 2026 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
from objects import globalstore
from functions import xtramath

def to_color(visual_obj):
	return '#'+visual_obj.color.get_hex()

class output_darwin(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_shortname(self):
		return 'darwin'
	
	def get_name(self):
		return 'Darwin'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'
		in_dict['fxtype'] = 'none'
		in_dict['file_ext'] = 'darwin'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import darwin as proj_darwin

		convproj_obj.change_timings(480)
		
		project_obj = proj_darwin.darwin_project()
		project_obj.bpm = int(convproj_obj.params.get('bpm', 120).value)
		project_obj.masterTrack.volume = convproj_obj.track_master.params.get('vol', 1).value

		tracknum = 0
		for trackid, track_obj in convproj_obj.track__iter():
			if track_obj.type in ['instrument']:
				visual_obj = track_obj.visual
				visual_inst_obj = track_obj.visual_inst

				darwin_track = proj_darwin.darwin_track() 
				darwin_track.id = tracknum
				if visual_obj.color: darwin_track.color = to_color(outcolor)
				elif visual_inst_obj.color: darwin_track.color = to_color(visual_inst_obj)
				if visual_obj.name: darwin_track.name = visual_obj.name
				darwin_track.muted = not bool(track_obj.params.get('enabled', 1).value)
				darwin_track.pan = track_obj.params.get('pan', 1).value
				darwin_track.solo = bool(track_obj.params.get('solo', 1).value)
				darwin_track.volume = track_obj.params.get('vol', 1).value

				for notespl_obj in track_obj.placements.pl_notes:
					position, duration = notespl_obj.time.get_posdur()
					clip_obj = proj_darwin.darwin_clip()
					clip_obj.startTick = int(position)
					clip_obj.durationTicks = int(duration)

					notespl_obj.notelist.mod_limit(-60, 67)
					for cnote in notespl_obj.notelist.iter_notes():
						note_obj = proj_darwin.darwin_note()
						note_obj.startTick = int(cnote.pos)
						note_obj.durationTicks = int(cnote.dur)
						note_obj.pitch = int(cnote.key)+60
						note_obj.velocity = int(float(cnote.vol)*100)
						clip_obj.notes.append(note_obj)

					darwin_track.clips.append(clip_obj)

				project_obj.tracks.append(darwin_track)
				tracknum += 1

		if dawvert_intent.output_mode == 'file':
			project_obj.save_to_file(dawvert_intent.output_file)