# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import value_midi
import xml.etree.ElementTree as ET
import plugins
import json

class clipinfo():
	def __init__(self):
		self.track_obj = None
		self.regioninfo = None
		self.clipstretch = None
		self.clipsize = None

class proj_state():
	def __init__(self, convproj_obj):
		self.convproj_obj = convproj_obj
		self.cur_track = None
		self.cur_tid = None
		self.cur_tpl = None
		self.cur_tnum = None
		self.cur_events = None
		self.cur_channel = None

		self.sysex_data = {}
		self.sysex_num = 0
		self.sysex_points = []
		self.segment_data_store = {}

	def chunk___1(self, parseddata): #Gen1:Global:Timebase
		cvpj_tracks = self.convproj_obj.tracks
		cvpj_trackid = str(parseddata.trackno)
		track_obj = cvpj_tracks.add(cvpj_trackid, 'midi_single', 1, False)
		track_obj.visual.name = parseddata.name.decode()
		if parseddata.channel != 255:
			trackmidi_obj = track_obj.midi
			trackmidi_obj.out_enabled = True
			trackmidi_obj.out_chanport.chan = parseddata.channel
			trackmidi_obj.out_chanport.port = parseddata.port
			trackchannel = parseddata.channel
		else:
			trackchannel = 0
		events_obj = track_obj.placements.midievents
		events_obj.has_duration = True
		events_obj.ppq = int(self.convproj_obj.time_ppq)

		self.cur_tid = cvpj_trackid
		self.cur_track = track_obj
		self.cur_tpl = track_obj.placements
		self.cur_tnum = parseddata.trackno
		self.cur_events = events_obj
		self.cur_channel = trackchannel

	def chunk___2(self, parseddata): #Gen1:Track:Events
		events_obj = self.cur_events
		trackchannel = self.cur_channel

		for event in parseddata.events:
			event_type = event.type
			event_data = event.data
			event_time = event.time

			if event_type == 0x90: events_obj.add_note_dur(event_time, trackchannel, event_data.data1, event_data.data2, event_data.dur)
			elif event_type == 0xA0: events_obj.add_note_pressure(event_time, trackchannel, event_data.data1, event_data.data2)
			elif event_type == 0xB0: events_obj.add_control(event_time, trackchannel, event_data.data1, event_data.data2)
			elif event_type == 0xC0: events_obj.add_program(event_time, trackchannel, event_data.data1)
			elif event_type == 0xD0: events_obj.add_chan_pressure(event_time, trackchannel, event_data.data1)
			elif event_type == 0xE0: events_obj.add_pitch_hi_lo(event_time, trackchannel, event_data.data2, event_data.data1)
			elif event_type == 0xF0: self.sysex_points.append([events_obj, event_time, event_data.data1])

	def chunk___6(self, parseddata): #Gen1:Global:SysEx
		self.sysex_num += 1
		self.sysex_data[self.sysex_num] = parseddata.data[1:-1]

	def chunk___8(self, parseddata): #Gen1:Global:Comment
		cvpj_metadata = self.convproj_obj.metadata
		if len(parseddata.data)>1:
			cvpj_metadata.comment_text = parseddata.data[1:].decode("windows-1252")

	def chunk__10(self, parseddata): #Gen1:Global:Timebase
		self.convproj_obj.set_timings(parseddata.timebase)

	def chunk__15(self, parseddata): #Gen1:Global:Auto:Tempo_V3
		cvpj_automation = self.convproj_obj.automation
		points = parseddata.points
		if points:
			firstpoint = points[0]
			if firstpoint[0]==0: self.convproj_obj.params.add('bpm', firstpoint[1]/100, 'float')
			for x in points:
				cvpj_automation.add_autotick(['main', 'bpm'], 'float', x[0], x[1]/100)

	def chunk__21(self, parseddata): #Gen1:Global:Markers
		cvpj_timemarkers = self.convproj_obj.timemarkers
		for realtime, pos, text in parseddata.markers:
			if not realtime:
				timemarker_obj = cvpj_timemarkers.add()
				timemarker_obj.time.set_pos(pos)
				timemarker_obj.visual.name = text.decode()

	def chunk__24(self, parseddata): #Gen1:Track:Name
		self.cur_track.visual.name = parseddata.name.decode()

	def chunk__26(self, parseddata): #Gen1:Global:VariablePart
		cvpj_metadata = self.convproj_obj.metadata

		vname = parseddata.name
		vvalue = parseddata.value

		if vname=="Title": cvpj_metadata.name = vvalue.decode("windows-1252")
		elif vname=="Subtitle": cvpj_metadata.subname = vvalue.decode("windows-1252")
		elif vname=="Instructions": cvpj_metadata.data['instructions'] = vvalue.decode("windows-1252")
		elif vname=="Author": cvpj_metadata.author = vvalue.decode("windows-1252")
		elif vname=="Copyright": cvpj_metadata.copyright = vvalue.decode("windows-1252")

	def chunk__36(self, parseddata): #Gen2:Track:Header
		cvpj_tracks = self.convproj_obj.tracks
		cvpj_trackid = str(parseddata.trackno)
		track_obj = cvpj_tracks.add(cvpj_trackid, 'hybrid', 1, False)
		track_obj.visual.name = parseddata.name.decode()
		if parseddata.channel != 255:
			trackchannel = max(0, parseddata.channel)
			trackmidi_obj = track_obj.midi
			trackmidi_obj.out_enabled = True
			trackmidi_obj.out_chanport.chan = trackchannel
			trackmidi_obj.out_chanport.port = parseddata.port
			trackmidi_obj.out_inst.patch = max(parseddata.patch, 0)
		else:
			trackchannel = 0

		events_obj = track_obj.placements.midievents
		events_obj.has_duration = True
		events_obj.ppq = int(self.convproj_obj.time_ppq)

		self.cur_tid = cvpj_trackid
		self.cur_track = track_obj
		self.cur_tpl = track_obj.placements
		self.cur_tnum = parseddata.trackno
		self.cur_events = events_obj
		self.cur_channel = trackchannel

	def chunk__49(self, parseddata): #Gen2:Track:Segment
		if parseddata.is_nonlinked: 
			self.segment_data_store[parseddata.id] = [parseddata.events, parseddata.name, parseddata.color, parseddata.offset]
		cw_events, cw_name, cw_color, startoffs = self.segment_data_store[parseddata.id]

		trackchannel = self.cur_channel
		
		placement_obj = self.cur_tpl.add_midi()
		events_obj = placement_obj.midievents
		events_obj.has_duration = True
		events_obj.ppq = int(self.convproj_obj.time_ppq)

		if cw_name: placement_obj.visual.name = cw_name.decode()
		if cw_color is not None: 
			placement_obj.visual.color.set_int(list(cw_color))
			placement_obj.visual.color.fx_allowed = ['saturate', 'brighter']

		for event in cw_events:
			event_type = event.type
			event_data = event.data
			event_time = event.time-startoffs

			if event_type == 0x90: events_obj.add_note_dur(event_time, trackchannel, event_data.data1, event_data.data2, event_data.dur)
			elif event_type == 0xA0: events_obj.add_note_pressure(event_time, trackchannel, event_data.data1, event_data.data2)
			elif event_type == 0xB0: events_obj.add_control(event_time, trackchannel, event_data.data1, event_data.data2)
			elif event_type == 0xC0: events_obj.add_program(event_time, trackchannel, event_data.data1)
			elif event_type == 0xD0: events_obj.add_chan_pressure(event_time, trackchannel, event_data.data1)
			elif event_type == 0xE0: events_obj.add_pitch_hi_lo(event_time, trackchannel, event_data.data2, event_data.data1)

		time_obj = placement_obj.time
		time_obj.set_posdur(parseddata.offset, int(events_obj.get_dur()))

	def chunk__45(self, parseddata): #Gen2:Track:Events
		cw_events = parseddata.events
		track_obj = self.cur_track
		trackchannel = self.cur_channel

		clipinfop = clipinfo()
		clipinfop.track_obj = track_obj

		isallaudio = False

		if cw_events:
			firstpos = cw_events[0].time

			placement_obj = self.cur_tpl.add_midi()
			events_obj = placement_obj.midievents
			events_obj.has_duration = True
			events_obj.ppq = int(self.convproj_obj.time_ppq)

			if parseddata.name: placement_obj.visual.name = parseddata.name.decode()

			for event in parseddata.events:
				event_type = event.type
				event_data = event.data
				event_time = event.time-firstpos

				if event_type == 0x90: events_obj.add_note_dur(event_time, trackchannel, event_data.data1, event_data.data2, event_data.dur)
				elif event_type == 0xA0: events_obj.add_note_pressure(event_time, trackchannel, event_data.data1, event_data.data2)
				elif event_type == 0xB0: events_obj.add_control(event_time, trackchannel, event_data.data1, event_data.data2)
				elif event_type == 0xC0: events_obj.add_program(event_time, trackchannel, event_data.data1)
				elif event_type == 0xD0: events_obj.add_chan_pressure(event_time, trackchannel, event_data.data1)
				elif event_type == 0xE0: events_obj.add_pitch_hi_lo(event_time, trackchannel, event_data.data2, event_data.data1)

			time_obj = placement_obj.time
			time_obj.set_posdur(firstpos, int(events_obj.get_dur()))

class input_cakewalk_wrk(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'cakewalk_wrk'
	
	def get_name(self):
		return 'Cakewalk WRK'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'multi'

	def parse(self, conversion_state, dawvert_intent):
		from objects.file_proj_past import cakewalk_wrk as proj_cakewalk_wrk
		project_obj = proj_cakewalk_wrk.cakewalk_wrk_file()
		if dawvert_intent.input_mode == 'file':
			if 'dataview_in' in dawvert_intent.debug_flags:
				import sys
				sys.stdout = open('out.log', 'w')
				project_obj.viewchunks(dawvert_intent.input_file)
				exit()
			project_obj.load_from_file(dawvert_intent.input_file)
			conversion_state.project = project_obj
			return True

	def to_convproj(self, convproj_obj, dawvert_intent, conversion_state):
		project_obj = conversion_state.project

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks
		cvpj_automation = convproj_obj.automation
		cvpj_timemarkers = convproj_obj.timemarkers
		cvpj_metadata = convproj_obj.metadata
		
		# ---------- convproj init ----------
		convproj_obj.set_timings(96)
		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.audio_filetypes = ['wav']
		traits_obj.track_hybrid = True

		# ---------- data ----------
		trackchannel = 0

		proj_gen = proj_state(convproj_obj)

		if project_obj.version == 2:
			convproj_obj.fxtype = 'rack'
			convproj_obj.type = 'cs'

			traits_obj.track_nopl = True
			convproj_obj.do_actions.append('do_addloop')
			convproj_obj.do_actions.append('do_singlenotelistcut')

			proj_gen.sysex_points = []

			for chunk in project_obj.chunks:
				if chunk.is_parsed:
					parseddata = chunk.content
					if   chunk.id ==   1: proj_gen.chunk___1(parseddata) #Gen1:Global:Timebase
					elif chunk.id ==   2: proj_gen.chunk___2(parseddata) #Gen1:Track:Events
					elif chunk.id ==   6: proj_gen.chunk___6(parseddata) #Gen1:Global:SysEx
					elif chunk.id ==   8: proj_gen.chunk___8(parseddata) #Gen1:Global:Comment
					elif chunk.id ==  10: proj_gen.chunk__10(parseddata) #Gen1:Global:Timebase
					elif chunk.id ==  15: proj_gen.chunk__15(parseddata) #Gen1:Global:Auto:Tempo_V3
					elif chunk.id ==  24: proj_gen.chunk__24(parseddata) #Gen1:Track:Name
					elif chunk.id ==  26: proj_gen.chunk__26(parseddata) #Gen1:Global:VariablePart

			for sysex_point in proj_gen.sysex_points:
				sysex_point[0].add_sysex(sysex_point[1], proj_gen.sysex_data[sysex_point[2]])

		if project_obj.version == 3:
			convproj_obj.fxtype = 'rack'
			convproj_obj.type = 'cs'

			convproj_obj.do_actions.append('do_addloop')

			for chunk in project_obj.chunks:
				if chunk.is_parsed:
					parseddata = chunk.content
	
					if   chunk.id ==   8: proj_gen.chunk___8(parseddata) #Gen1:Global:Comment
					elif chunk.id ==  10: proj_gen.chunk__10(parseddata) #Gen1:Global:Timebase
					elif chunk.id ==  15: proj_gen.chunk__15(parseddata) #Gen1:Global:Auto:Tempo_V3
					elif chunk.id ==  21: proj_gen.chunk__21(parseddata) #Gen1:Global:Markers
					elif chunk.id ==  26: proj_gen.chunk__26(parseddata) #Gen1:Global:VariablePart
					elif chunk.id ==  36: proj_gen.chunk__36(parseddata) #Gen2:Track:Header
					elif chunk.id ==  45: proj_gen.chunk__45(parseddata) #Gen2:Track:Events
					elif chunk.id ==  49: proj_gen.chunk__49(parseddata) #Gen2:Track:Segment

					#if chunk.id == 3: #Gen1:Global:Settings
					#	print(dir(parseddata))
						#print(parseddata.TempoOfs1)
						#print(parseddata.TempoOfs2)
						#print(parseddata.TempoOfs3)
						#convproj_obj.set_timings(parseddata.timebase, False)


					#elif chunk.id == 89: #Gen3:Track:RegionInfo
					#	isallaudio = all([(x.cmdnum == 0 and x.channum == 4) for x in parseddata.parts])
						#if isallaudio:
							#audioclips.append([track_obj, parseddata, None, None])
						#	print(len(audioclips))

					#elif chunk.id == 98: #Gen2:AudioClipStretch
					#	for n, x in enumerate(clipsdata_audio):
					#		print(parseddata.data)
						#for n, i in enumerate(parseddata.data):
						#	audioclips[n][2] = i

					#elif chunk.id == 99: #Gen2:AudioClipSize
						#print(len(parseddata.data))
						#for n, x in enumerate(parseddata.data):
						#	audioclips[n][3] = x

					#else:
					#	print(chunk, dir(parseddata))

			#for x in clipsdata:
			#	print(x.track_obj, x.regioninfo, x.clipstretch, x.clipsize)
			#print(clipsdata_audio)