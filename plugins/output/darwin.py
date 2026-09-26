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

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks
		
		# ---------- setup ----------
		convproj_obj.change_timings(480)
		
		# ---------- project ----------
		project_obj = proj_darwin.darwin_project()
		project_obj.bpm = int(convproj_obj.params.get('bpm', 120).value)
		project_obj.masterTrack.volume = convproj_obj.track_master.params.get('vol', 1).value

		# ---------- tracks ----------
		tracknum = 0
		for trackid, track_obj in cvpj_tracks.iter():
			if track_obj.type in ['instrument']:
				darwin_track = proj_darwin.darwin_track() 
				darwin_track.id = tracknum
				project_obj.tracks.append(darwin_track)

				tracknum += 1

				# visual
				visual_obj = track_obj.visual
				visual_inst_obj = track_obj.visual_inst

				if visual_obj.color: darwin_track.color = to_color(outcolor)
				elif visual_inst_obj.color: darwin_track.color = to_color(visual_inst_obj)
				if visual_obj.name: darwin_track.name = visual_obj.name

				# params
				darwin_track.muted = not bool(track_obj.params.get('enabled', 1).value)
				darwin_track.pan = track_obj.params.get('pan', 1).value
				darwin_track.solo = bool(track_obj.params.get('solo', 1).value)
				darwin_track.volume = track_obj.params.get('vol', 1).value

				# placements notes
				for notespl_obj in track_obj.placements.pl_notes:
					position, duration = notespl_obj.time.get_posdur()
					darwin_clip = proj_darwin.darwin_clip()
					darwin_clip.startTick = int(position)
					darwin_clip.durationTicks = int(duration)
					darwin_track.clips.append(darwin_clip)

					cvpj_notelist = notespl_obj.notelist
					cvpj_notelist.sort()
					cvpj_notelist.mod_limit(-60, 67)
					for cnote in cvpj_notelist.iter_notes():
						darwin_note = proj_darwin.darwin_note()
						darwin_note.startTick = int(cnote.pos)
						darwin_note.durationTicks = int(cnote.dur)
						darwin_note.pitch = int(cnote.key)+60
						darwin_note.velocity = int(float(cnote.vol)*100)
						darwin_clip.notes.append(darwin_note)

		# ---------- output ----------
		if dawvert_intent.output_mode == 'file':
			project_obj.save_to_file(dawvert_intent.output_file)