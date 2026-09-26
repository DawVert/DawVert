# SPDX-FileCopyrightText: 2026 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
from objects import globalstore
from functions import xtramath

def do_track_visual(magda_track, visual_obj):
	if visual_obj.name: magda_track.name = visual_obj.name
	if visual_obj.color: magda_track.color = 'FF'+visual_obj.color.get_hex()

def do_track_params(magda_track, params_obj):
	magda_track.volume = params_obj.get('vol', 1).value
	magda_track.manualVolume = magda_track.volume
	magda_track.pan = params_obj.get('pan', 0).value
	magda_track.manualPan = magda_track.pan
	magda_track.muted = not bool(params_obj.get('enabled', 1).value)
	magda_track.soloed = bool(params_obj.get('solo', 0).value)

def do_clip_visual(magda_clip, visual_obj):
	if visual_obj.name: magda_clip.name = visual_obj.name
	if visual_obj.color: magda_clip.color = 'FF'+visual_obj.color.get_hex()

def do_clips(session_obj, magda_track, placements_obj, convproj_obj):
	from objects.file_proj import magda as proj_magda

	tempo = convproj_obj.params.get('bpm', 120).value

	for notespl_obj in placements_obj.pl_notes:
		time_obj = notespl_obj.time
		position, duration = time_obj.get_posdur()
		magda_clip = proj_magda.magda_clip()
		magda_clip.id = len(session_obj.clips)
		magda_clip.trackId = magda_track.idnum
		magda_clip.type = 1
		magda_clip.placement = {"startBeat": position, "lengthBeats": duration}
		do_clip_visual(magda_clip, notespl_obj.visual)

		for cnote in notespl_obj.notelist.iter_notes():
			if 0 <= cnote.key+60 <= 128:
				magda_note = proj_magda.magda_clip_midiNote()
				magda_note.noteNumber = int(cnote.key+60)
				magda_note.velocity = float(cnote.vol)
				magda_note.startBeat = int(cnote.pos)
				magda_note.lengthBeats = int(cnote.dur)
				magda_clip.midiNotes.append(magda_note)

		session_obj.clips.append(magda_clip)

	for audiopl_obj in placements_obj.pl_audio:
		time_obj = audiopl_obj.time
		position, duration = time_obj.get_posdur()
		magda_clip = proj_magda.magda_clip()
		magda_clip.id = len(session_obj.clips)
		magda_clip.trackId = magda_track.idnum
		magda_clip.type = 0
		magda_clip.placement = {"startBeat": position, "lengthBeats": duration}
		do_clip_visual(magda_clip, audiopl_obj.visual)

		magda_clip.audio = proj_magda.magda_clip_audio()

		sp_obj = audiopl_obj.sample
		magda_clip.pan = sp_obj.pan
		magda_clip.pitchChange = sp_obj.pitch
		magda_clip.isReversed = sp_obj.reverse
		
		if not sp_obj.vol: magda_clip.volumeDB = -100
		else:
			dbval = xtramath.to_db(sp_obj.vol)
			magda_clip.volumeDB = min(dbval, 0)
			magda_clip.gainDB = max(dbval, 0)

		magda_clip.fadeIn = audiopl_obj.fade_in.get_dur_seconds(tempo)
		magda_clip.fadeOut = audiopl_obj.fade_out.get_dur_seconds(tempo)

		ref_found, sampleref_obj = convproj_obj.sampleref__get(audiopl_obj.sample.sampleref)
		manga_audio = magda_clip.audio
		if ref_found: 
			audiosource = manga_audio.source
			audiosource.filePath = sampleref_obj.fileref.get_path(None, False)
			audiosource.durationSeconds = sampleref_obj.get_dur_sec()

			audioplayback = manga_audio.playback
			if audiosource.durationSeconds: audioplayback.loopLengthSeconds = audiosource.durationSeconds

			audiointerpretation = manga_audio.interpretation

			stretch_obj = sp_obj.stretch
			stretch_timing = stretch_obj.timing

			if not stretch_timing.tempo_based: 
				audioplayback.speedRatio = stretch_timing.get__speed(sampleref_obj)
			else:
				offset = time_obj.get_offset()
				audioplayback.loopLengthBeats = stretch_timing.get__beats(sampleref_obj)
				audiointerpretation.totalBeats = audioplayback.loopLengthBeats
				audiointerpretation.totalBeatsLocked = True

				bpmcalc = (audiointerpretation.totalBeats/2)/audiosource.durationSeconds
				audiointerpretation.bpm = round(120*bpmcalc, 6)

				magda_clip.autoTempo = True
				manga_audio.timeStretchMode = 4
				magda_clip.loopEnabled = True

		session_obj.clips.append(magda_clip)

class output_magda(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_shortname(self):
		return 'magda'
	
	def get_name(self):
		return 'MAGDA'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'
		in_dict['fxtype'] = 'none'
		in_dict['file_ext'] = 'mgd'
		in_dict['track_hybrid'] = True
		in_dict['fxtype'] = ['route', 'groupreturn']

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import magda as proj_magda

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks
		cvpj_groups = convproj_obj.groups
		cvpj_transport = convproj_obj.transport
		
		# ---------- setup ----------
		convproj_obj.change_timings(1.0)
		
		numassoc_track = {}
		numassoc_group = {}
		numassoc_returns = {}

		objassoc_track = {}
		objassoc_group = {}
		objassoc_returns = {}

		auxbus = {}
		curbus = -1

		# ---------- project ----------
		session_obj = proj_magda.magda_session()
		session_obj.magdaVersion = "0.9.0"
		project_obj = session_obj.project
		project_obj.projectLength = convproj_obj.get_dur()

		# ---------- bpm ----------
		project_obj.tempo = convproj_obj.params.get('bpm', 120).value

		# ---------- metadata ----------
		if convproj_obj.metadata.name: project_obj.name = convproj_obj.metadata.name

		# ---------- transport ----------
		project_obj.loop.enabled = cvpj_transport.loop_active
		project_obj.loop.startBeats = cvpj_transport.loop_start
		project_obj.loop.endBeats = cvpj_transport.loop_end

		# ---------- groupreturn ----------
		if convproj_obj.fxtype in ['groupreturn', 'none']:
			tracknum = 1

			master_returns = convproj_obj.track_master.returns
			for returnid, return_obj in master_returns.items():
				numassoc_returns[returnid] = tracknum
				magda_track = proj_magda.magda_track()
				session_obj.tracks.append(magda_track)
				magda_track.idnum = tracknum
				magda_track.type = 4
				magda_track.viewSettings['Master'].visible = False
				magda_track.viewSettings['Live'].height = 60
				do_track_visual(magda_track, return_obj.visual)
				do_track_params(magda_track, return_obj.params)

				auxbus[tracknum] = curbus
				curbus += 1

				magda_track.auxBusIndex = curbus

				tracknum += 1

			for groupid, group_obj in cvpj_groups.iter():
				numassoc_group[groupid] = tracknum
				objassoc_group[groupid] = group_obj
				tracknum += 1

			for trackid, track_obj in cvpj_tracks.iter():
				numassoc_track[trackid] = tracknum
				objassoc_track[trackid] = track_obj
				tracknum += 1

			track_group = {}
			track_nongroup = []
	
			for groupid, group_obj in cvpj_groups.iter():
				if group_obj.group:
					if group_obj.group not in track_group: track_group[group_obj.group] = []
					track_group[group_obj.group].append(['GROUP', groupid])
				else: track_nongroup.append(['GROUP', groupid])
	
			for trackid, track_obj in cvpj_tracks.iter():
				if track_obj.group: 
					if track_obj.group not in track_group: track_group[track_obj.group] = []
					track_group[track_obj.group].append(['TRACK', trackid])
				else: track_nongroup.append(['TRACK', trackid])

			outbus = []
			groupchildren = {}

			def do_grouptracks(trackgroup, is_group, insidegroup):
				if insidegroup: groupchildren[insidegroup] = []
				for d in trackgroup:
					t, trackid = d
					if t=='GROUP':
						if insidegroup: groupchildren[insidegroup].append(['GROUP', trackid])
						if trackid in track_group:
							outbus.append([t, trackid, insidegroup])
							do_grouptracks(track_group[trackid], 1, trackid)
						#else:
						#	#logger_output.warning('Group not found: %s' % i)
						#	outbus.append([t, i, insidegroup])
					else:
						if insidegroup: groupchildren[insidegroup].append(['TRACK', trackid])
						outbus.append([t, trackid, insidegroup])

			do_grouptracks(track_nongroup, 0, None)

			for tracktype, trackid, insidegroup in outbus:
				if tracktype=='GROUP':
					group_obj = objassoc_group[trackid]
					magda_track = proj_magda.magda_track()
					session_obj.tracks.append(magda_track)
					do_track_visual(magda_track, group_obj.visual)
					do_track_params(magda_track, group_obj.params)

					magda_track.idnum = numassoc_group[trackid]
					magda_track.type = 3
					magda_track.viewSettings['Master'].visible = False
					magda_track.viewSettings['Live'].height = 60
					magda_track.midiInputDevice = 'all'
					if trackid in groupchildren:
						magda_track.childIds = []
						for gtt, gti in groupchildren[trackid]:
							if gtt=='GROUP': magda_track.childIds.append(numassoc_group[gti])
							if gtt=='TRACK': magda_track.childIds.append(numassoc_track[gti])

				if tracktype=='TRACK':
					track_obj = objassoc_track[trackid]
					magda_track = proj_magda.magda_track()
					session_obj.tracks.append(magda_track)
					do_track_visual(magda_track, track_obj.visual)
					do_track_params(magda_track, track_obj.params)

					magda_track.idnum = numassoc_track[trackid]
					magda_track.type = 0
					magda_track.viewSettings['Master'].visible = False
					magda_track.viewSettings['Live'].height = 60
					magda_track.midiInputDevice = 'all'
					do_clips(session_obj, magda_track, track_obj.placements, convproj_obj)

				if insidegroup: 
					magda_track.parentId = numassoc_group[insidegroup]
					magda_track.audioOutputDevice = 'track:'+str(magda_track.parentId)

		# ---------- output ----------
		if dawvert_intent.output_mode == 'file':
			session_obj.save_to_file(dawvert_intent.output_file)