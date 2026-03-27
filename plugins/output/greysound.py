# SPDX-FileCopyrightText: 2026 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import json
from objects import globalstore
from functions import xtramath

def to_color(visual_obj):
	return '#'+visual_obj.color.get_hex()

def ticks_to_time(v, bpm):
	return int((v/480)*(120/bpm)*1000)

def do_track_visual(gs_track, cvpj_track, fallbackname):
	visual_obj = cvpj_track.visual
	visual_inst_obj = cvpj_track.visual_inst
	gs_track.name = visual_obj.name if visual_obj.name else fallbackname
	if visual_obj.comment: gs_track.comments = visual_obj.comment
	if visual_obj.color: gs_track.color = to_color(outcolor)
	elif visual_inst_obj.color: gs_track.color = to_color(visual_inst_obj)

def clipGain(clipGain):
	return xtramath.to_db(clipGain) if clipGain is not 0 else None

def do_track_params(gs_track, cvpj_track):
	gs_track.faderGainDb = clipGain(cvpj_track.params.get('vol', 1).value)

class output_greysound(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_shortname(self):
		return 'greysound'
	
	def get_name(self):
		return 'Greysound'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'
		in_dict['fxtype'] = 'none'
		in_dict['file_ext'] = ''

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import greysound as proj_greysound

		convproj_obj.change_timings(480)
		
		session_obj = proj_greysound.greysound_session()
		bpm = session_obj.tempo = int(convproj_obj.params.get('bpm', 120).value)

		session_obj.metadata['name'] = convproj_obj.metadata.name if convproj_obj.metadata.name else 'untitled'

		# master
		track_obj = convproj_obj.track_master

		greysound_track = proj_greysound.greysound_track()
		greysound_track.id = 5000000000
		greysound_track.type = 'MASTER'
		greysound_track.timeBase = 'TICKS'
		do_track_visual(greysound_track, track_obj, 'Master')
		do_track_params(greysound_track, track_obj)
		session_obj.tracks.append(greysound_track)

		# tracks
		tracknum = 0
		for trackid, track_obj in convproj_obj.track__iter():
			gtracknum = 1000000000+tracknum
			if track_obj.type in ['instrument']:
				visual_obj = track_obj.visual
				visual_inst_obj = track_obj.visual_inst

				greysound_track = proj_greysound.greysound_track()
				greysound_track.id = gtracknum
				do_track_visual(greysound_track, track_obj, 'Track')
				do_track_params(greysound_track, track_obj)
				greysound_track.type = 'INSTRUMENT'
				greysound_track.timeBase = 'TICKS'
				greysound_track.position = tracknum

				session_obj.tracks.append(greysound_track)

				for rnum, notespl_obj in enumerate(track_obj.placements.pl_notes):
					greysound_region = proj_greysound.greysound_region()
					greysound_region.id = 'converted_region_%s_%i' % (gtracknum, rnum)
					greysound_region.trackId = gtracknum
					start, end = notespl_obj.time.get_startend()
					greysound_region.start = {"ticks": start, "millis": ticks_to_time(start, bpm)}
					greysound_region.end = {"ticks": end, "millis": ticks_to_time(end, bpm)}

					for cnote in notespl_obj.notelist.iter_notes():
						note_obj = proj_greysound.greysound_midinote()
						note_obj.startTicks = int(cnote.pos)
						note_obj.durationTicks = int(cnote.dur)
						note_obj.pitch = int(cnote.key)+60
						note_obj.velocity = int(float(cnote.vol)*100)
						greysound_region.midiNotes.append(note_obj)

					session_obj.regions.append(greysound_region)

				tracknum += 1

		if dawvert_intent.output_mode == 'file':
			folder = dawvert_intent.output_folder
			namet = dawvert_intent.output_visname
			foldpath = os.path.join(folder, namet)
			
			os.makedirs(foldpath, exist_ok=True)

			outfile = os.path.join(foldpath, 'session.json')

			f = open(outfile, 'w')
			f.write(json.dumps(session_obj.write()))
