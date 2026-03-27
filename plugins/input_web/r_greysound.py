# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import zipfile
import os
from functions import xtramath

def do_track_visual(gs_track, cvpj_track):
	visual_obj = cvpj_track.visual
	visual_obj.name = gs_track.name
	visual_obj.color.set_hex(gs_track.color)
	visual_obj.comment = gs_track.comments

def do_track_params(gs_track, cvpj_track):
	channelCount = gs_track.channelCount
	channelPans = gs_track.channelPans
	cvpj_track.params.add('vol', clipGain(gs_track.faderGainDb), 'float')
	cvpj_track.params.add('enabled', bool(not gs_track.muted), 'bool')
	cvpj_track.params.add('solo', bool(gs_track.solo), 'bool')
	if channelPans: 
		if channelCount == 1:
			cvpj_track.params.add('pan', channelPans[0], 'float')
		if channelCount == 2:
			cvpj_track.datavals.add('pan_mode', 'split')
			cvpj_track.params.add('splitpan_left', channelPans[0], 'float')
			cvpj_track.params.add('splitpan_right', channelPans[1], 'float')

def extract_audio(clip, sampleref_obj, dawvert_intent, zipfile):
	filename = str(sampleref_obj.fileref.file)
	try: zipfile.extract(clip.storagePath, path=dawvert_intent.path_samples['extracted'], pwd=None)
	except PermissionError: pass
	filepath = os.path.join(dawvert_intent.path_samples['extracted'], clip.storagePath)
	sampleref_obj.set_path(None, filepath)

def clipGain(clipGain):
	return xtramath.from_db(clipGain) if clipGain is not None else 0

class input_greysound(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'greysound'
	
	def get_name(self):
		return 'Greysound'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import greysound as proj_greysound

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'route'

		traits_obj = convproj_obj.traits
		traits_obj.audio_stretch = []
		traits_obj.auto_types = []
		traits_obj.placement_cut = False
		traits_obj.placement_loop = []
		traits_obj.time_seconds = False

		convproj_obj.set_timings(960)

		try:
			if dawvert_intent.input_mode == 'file':
				zip_data = zipfile.ZipFile(dawvert_intent.input_file, 'r')
		except zipfile.BadZipFile as t:
			raise ProjectFileParserException('greysound: Bad ZIP File: '+str(t))

		samplefolder = dawvert_intent.path_samples['extracted']
		if 'session.json' not in zip_data.namelist(): 
			raise ProjectFileParserException('greysound: JSON file not found')

		t_greysound_session = zip_data.read('session.json')
		gs_proj = json.loads(t_greysound_session)
		session_obj = proj_greysound.greysound_session()
		session_obj.read(gs_proj)

		convproj_obj.transport.loop_active = session_obj.loopEnabled

		loopRange = session_obj.loopRange
		if loopRange is not None:
			if 'start' in loopRange:
				if 'ticks' in loopRange['start']:
					convproj_obj.transport.loop_start = loopRange['start']['ticks']
			if 'end' in loopRange:
				if 'ticks' in loopRange['end']:
					convproj_obj.transport.loop_end = loopRange['end']['ticks']

		playheadPosition = session_obj.playheadPosition
		if 'ticks' in playheadPosition:
			convproj_obj.transport.current_pos = playheadPosition['ticks']

		convproj_obj.params.add('bpm', session_obj.tempo, 'float')

		if 'name' in session_obj.metadata:
			convproj_obj.metadata.name = session_obj.metadata['name']

		gs_trackids = {}
		trackorder = {}
		routesends = {}

		for gs_track in session_obj.tracks:
			if gs_track.type == 'MASTER':
				track_obj = convproj_obj.track_master
				do_track_visual(gs_track, track_obj)
				do_track_params(gs_track, track_obj)
			else:
				if gs_track.type == 'INSTRUMENT': track_type = 'instrument'
				if gs_track.type == 'AUX': track_type = 'fx'
				if gs_track.type == 'AUDIO': track_type = 'audio'
				track_obj = convproj_obj.track__add(str(gs_track.id), track_type, 1, False)
				do_track_visual(gs_track, track_obj)
				do_track_params(gs_track, track_obj)
				track_obj.armed.on = gs_track.armed
				if gs_track.type == 'INSTRUMENT': track_obj.armed.in_keys = gs_track.armed
				if gs_track.type == 'AUDIO': track_obj.armed.in_audio = gs_track.armed
				trackorder[gs_track.position] = gs_track.id
				if gs_track.id not in routesends: 
					master_on = True
					outputRouting = gs_track.outputRouting
					if outputRouting is not None:
						if 'type' in outputRouting:
							if outputRouting['type']=='none': master_on = False
					routesends[gs_track.id] = [master_on, []]

			gs_trackids[gs_track.id] = track_obj

		for clip in session_obj.clips:
			sampleref_obj = convproj_obj.sampleref__add(clip.id, clip.filename, 'win')
			sampleref_obj.set_dur_sec(clip.durationSec)
			extract_audio(clip, sampleref_obj, dawvert_intent, zip_data)

		for region in session_obj.regions:
			track_obj = gs_trackids[region.trackId]
			if region.clipId:
				placement_obj = track_obj.placements.add_audio()
				sp_obj = placement_obj.sample
				sp_obj.sampleref = region.clipId
				sp_obj.vol = clipGain(region.clipGain)

				region_fadeIn = region.fadeIn
				region_fadeOut = region.fadeOut
				if 'millis' in region_fadeIn: placement_obj.fade_in.set_dur(region_fadeIn['millis']/1000, 'seconds')
				if 'millis' in region_fadeOut: placement_obj.fade_out.set_dur(region_fadeOut['millis']/1000, 'seconds')

			else:
				placement_obj = track_obj.placements.add_notes()
				cvpj_notelist = placement_obj.notelist
				for n in region.midiNotes: 
					cvpj_notelist.add_r(n.startTicks, n.durationTicks, n.pitch-60, n.velocity/127, None)

			time_obj = placement_obj.time

			reg_start = region.start
			reg_end = region.end
			if 'ticks' in reg_start and 'ticks' in reg_end:
				time_obj.position.set(reg_start['ticks'], 'ppq')
				time_obj.duration.set(reg_end['ticks']-reg_start['ticks'], 'ppq')
			elif 'millis' in reg_start and 'millis' in reg_end:
				time_obj.position.set(reg_start['millis']/1000, 'seconds')
				time_obj.duration.set((reg_end['millis']-reg_start['millis'])/1000, 'seconds')

			reg_offs = region.clipStartOffset
			if 'ticks' in reg_offs: time_obj.set_offset(reg_offs['ticks'])
			elif 'millis' in reg_offs: time_obj.set_offset_real(reg_offs['millis']/1000)

		for send in session_obj.sends:
			if send.sourceTrackId not in routesends: routesends[send.sourceTrackId] = [True, []]
			routesends[send.sourceTrackId][1].append(send)

		for srctrk, v in routesends.items():
			master_on, data = v
			sends_obj = convproj_obj.fx__route__add(str(srctrk))
			sends_obj.to_master_active = master_on
			for x in data:
				send_obj = sends_obj.add(str(x.destinationTrackId), None, clipGain(x.levelDb))
				send_obj.params.add('pan', x.channelPans[0], 'float')

		fxslots = {}
		for insert in session_obj.inserts:
			if region.trackId not in fxslots: fxslots[region.trackId] = {}
			fxslots[region.trackId][insert.slotIndex] = insert

		for trackid, slots in fxslots.items():
			track_obj = gs_trackids[trackid]
			for slotnum in sorted(slots):
				fxdata = slots[slotnum]
				fxid = 'fx_%i_%s' % (trackid, slotnum)
				plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'graysound', fxdata.pluginType.lower())
				plugin_obj.fxdata_add(not fxdata.bypassed, 1)
				plugin_obj.role = 'effect'
			
				for k, v in fxdata.parameters.items():
					if isinstance(v, int): plugin_obj.params.add(k, v, 'int')
					elif isinstance(v, float): plugin_obj.params.add(k, v, 'float')
					elif isinstance(v, bool): plugin_obj.params.add(k, v, 'bool')

		convproj_obj.track_order = [str(trackorder[x]) for x in sorted(trackorder)]
