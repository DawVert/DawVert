# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import uuid
import os
import shutil
from objects import globalstore
from functions import data_values
from functions import xtramath

def calcsec(val, ppq):
	return int((val*50)*ppq)

class output_bandlab(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_shortname(self):
		return 'qtractor'
	
	def get_name(self):
		return 'Qtractor'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['audio_filetypes'] = ['wav']
		in_dict['file_ext'] = 'qtr'
		in_dict['auto_types'] = ['nopl_ticks']
		in_dict['audio_stretch'] = ['rate']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['projtype'] = 'r'
		in_dict['time_seconds'] = True

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import qtractor as proj_qtractor

		convproj_obj.change_timings(1.0)
		
		project_obj = proj_qtractor.qtractor_project()

		bpm = int(convproj_obj.params.get('bpm', 120).value)
		project_obj.properties.tempo = bpm
		project_obj.properties.sample_rate = convproj_obj.freq

		ppq = 960

		sampleref_filename = {}
		sampleref_filepath = {}

		for sampleref_id, sampleref_obj in convproj_obj.sampleref__iter():
			uuiddata = str( data_values.bytes__to_uuid( sampleref_id.encode() ) )
			filename = uuiddata+'.'+sampleref_obj.fileref.file.extension
			sampleref_filename[sampleref_id] = filename
			filepath = '/'.join(['.', 'Assets', 'Audio', filename])
			sampleref_filepath[sampleref_id] = filepath
			project_obj.files.audio_list[uuiddata] = filepath

		if dawvert_intent.output_mode == 'file':
			folder = dawvert_intent.output_folder
			namet = dawvert_intent.output_visname
			foldpath = os.path.join(folder, namet)
			
			os.makedirs(os.path.join(folder, namet, 'Assets'), exist_ok=True)
			os.makedirs(os.path.join(folder, namet, 'Assets', 'Audio'), exist_ok=True)
			os.makedirs(os.path.join(folder, namet, 'Assets', 'MIDI'), exist_ok=True)

			for sampleref_id, sampleref_obj in convproj_obj.sampleref__iter():
				a_in = sampleref_obj.fileref.get_path(None, False)
				a_out = os.path.join(folder, namet, 'Assets', 'Audio', sampleref_filename[sampleref_id])
				try:
					sampleref_obj.copy_resample(None, a_out)
				except:
					pass

		track_master = convproj_obj.track_master

		audio_engine = proj_qtractor.qtractor_audio_engine(None)
		audio_bus = audio_engine.audio_bus
		audio_bus.output_gain = track_master.params.get('vol', 1.0).value
		audio_bus.output_panning = track_master.params.get('pan', 0).value

		project_obj.devices.append(audio_engine)

		for trackid, track_obj in convproj_obj.track__iter():

			tracknotes_midinames = []

			if track_obj.type in ['instrument', 'audio']:
				qt_track = proj_qtractor.qtractor_track(None)
				if track_obj.type == 'instrument': qt_track.type = 'midi'

				qt_track.state.gain = track_obj.params.get('vol', 1).value
				qt_track.state.panning = track_obj.params.get('pan', 0).value
				qt_track.state.mute = int(not bool(track_obj.params.get('enabled', True).value))
				qt_track.state.solo = int(track_obj.params.get('solo', False).value)
				qt_track.state.record = int(track_obj.armed.on)

				if track_obj.visual.name: qt_track.name = track_obj.visual.name
				if track_obj.visual.color: 
					color = track_obj.visual.color
					qt_track.view.foreground_color = '#'+color.get_hex()
					qt_track.view.background_color = '#'+(color*0.6).get_hex()

				qt_track.view.height = int(track_obj.visual_ui.height*96)

				if track_obj.type == 'audio':
					qt_track.type = 'audio'
					for audiopl_obj in track_obj.placements.pl_audio:
						time_obj = audiopl_obj.time

						position, duration = time_obj.get_posdur_real()

						qt_clip = proj_qtractor.qtractor_clip(None)
						qt_clip.properties.start = calcsec(position, ppq)
						qt_clip.properties.length = calcsec(duration, ppq)
						qt_clip.properties.fade_in_type = 'InQuad'
						qt_clip.properties.fade_out_type = 'OutQuad'
						qt_clip.properties.fade_in = calcsec(audiopl_obj.fade_in.get_dur_seconds(bpm), ppq)
						qt_clip.properties.fade_out = calcsec(audiopl_obj.fade_out.get_dur_seconds(bpm), ppq)
						qt_clip.properties.mute = int(audiopl_obj.muted)
						qt_clip.audioclip = proj_qtractor.qtractor_clip_audioclip(None)

						sp_obj = audiopl_obj.sample
						qt_clip.audioclip.filename = sampleref_filepath[sp_obj.sampleref]
						qt_clip.audioclip.pitch_shift = xtramath.pitch_to_speed(sp_obj.pitch)
						qt_clip.properties.gain = sp_obj.vol
						qt_clip.properties.panning = sp_obj.pan

						_, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
						stretch_obj = sp_obj.stretch
						qt_clip.audioclip.time_stretch = 1/stretch_obj.timing.get__real_rate(sampleref_obj, time_obj.realtime_tempo)

						stretch_algo = stretch_obj.algorithm
						qt_clip.audioclip.rubberband_formant = int(stretch_algo.preserve_formants)

						name = audiopl_obj.visual.name if audiopl_obj.visual.name else ''
						qt_clip.properties.name = name
						qt_clip.name = name

						qt_track.clips.append(qt_clip)

				if track_obj.type == 'instrument':
					qt_track.type = 'midi'
					for notespl_obj in track_obj.placements.pl_notes:
						time_obj = notespl_obj.time
						
						position, duration = time_obj.get_posdur_real()
						
						qt_clip = proj_qtractor.qtractor_clip(None)
						qt_clip.properties.start = calcsec(position, ppq)
						qt_clip.properties.length = calcsec(duration, ppq)
						qt_clip.properties.name = notespl_obj.visual.name
						qt_clip.properties.mute = int(notespl_obj.muted)
						qt_clip.midiclip = proj_qtractor.qtractor_clip_midiclip(None)

						notelist = notespl_obj.notelist
						notelist.mod_limit(-60, 67)
						if notelist not in tracknotes_midinames:
							tracknotes_midinames.append(notelist)
							filename = 'track_%s_clip_%i' % (trackid, len(tracknotes_midinames)-1)
							project_obj.files.midi_list[filename] = '/'.join(['.', 'Assets', 'MIDI', filename+'.mid'])
							if dawvert_intent.output_mode == 'file':
								notelist.midi_to(os.path.join(folder, namet, 'Assets', 'MIDI', filename+'.mid'), bpm)

						notelist_id = 'track_%s_clip_%i' % (trackid, tracknotes_midinames.index(notelist))

						filepath = '/'.join(['.', 'Assets', 'MIDI', filename+'.mid'])
						qt_clip.midiclip.filename = filepath

						name = notespl_obj.visual.name if notespl_obj.visual.name else ''
						qt_clip.properties.name = name
						qt_clip.name = name

						qt_track.clips.append(qt_clip)

				project_obj.tracks.append(qt_track)

		if dawvert_intent.output_mode == 'file':
			namet = dawvert_intent.output_visname
			outfile = os.path.join(dawvert_intent.output_folder, namet, os.path.basename(dawvert_intent.output_file))
			project_obj.write_to_file(outfile)