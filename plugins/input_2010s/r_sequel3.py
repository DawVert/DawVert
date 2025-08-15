# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import numpy as np
from functions import xtramath
from objects import globalstore
from objects import colors
from objects.data_bytes import bytereader
import os

def do_visual(track_obj, track, track_node, colordata):
	track_obj.visual.name = track_node.name
	if 'Farb' in track.additional_attributes:
		farbcolor = track.additional_attributes['Farb']
		track_obj.visual.color.set_int(colordata.getcolornum(farbcolor))
	track_obj.visual_ui.height = track.height/73

def do_params(track_obj, track_device):
	if 'Volume' in track_device.deviceattributes:
		voldata = track_device.deviceattributes['Volume']
		track_obj.params.add('vol', voldata['Value']/25856, 'float')
	if 'Panner' in track_device.deviceattributes:
		pandata = track_device.deviceattributes['Panner']
		if 'audioComponent' in pandata:
			pannerdata = bytereader.bytereader()
			pannerdata.load_raw(pandata['audioComponent'])
			pandata = pannerdata.float()
			track_obj.params.add('pan', (pandata-0.5)*2, 'float')

def do_autopoints(convproj_obj, autoloc, auto_node, v_min, v_max, instant):
	auto_obj = convproj_obj.automation.create(autoloc, 'float' if not instant else 'bool', True)
	if 'Events' in auto_node:
		autoevents = auto_node['Events']
		if not instant:
			for x in autoevents:
				auto_obj.add_autopoint(x['Start'], xtramath.between_from_one(v_min, v_max, x['Value']), None)
		else:
			for x in autoevents:
				auto_obj.add_autopoint(x['Start'], xtramath.between_from_one(v_min, v_max, x['Value']), 'instant')

def do_auto(track_obj, convproj_obj, seq_automation, autoloc_start):
	from objects.file_proj_past._sequel import func
	for autotrack in seq_automation.tracks:
		nodeid = autotrack.node.obj_id
		trackdeviceid = autotrack.track_device.obj_id

		auto_node = None
		auto_device = None
		if nodeid in func.globalids: auto_node = func.globalids[nodeid]
		if trackdeviceid in func.globalids: auto_device = func.globalids[trackdeviceid]
		trackflags = autotrack.trackflags
		
		if auto_node is not None and auto_device is not None:
			con_type = auto_device['Connection Type']
			#dev_name = auto_device['Device Name'] if 'Device Name' in auto_device else None

			if con_type==2 and trackflags==0:
				do_autopoints(convproj_obj, autoloc_start+['vol'], auto_node, 0, 1, False)
			if con_type==2 and trackflags==1:
				do_autopoints(convproj_obj, autoloc_start+['enabled'], auto_node, 0, 1, True)
			if con_type==7 and trackflags==2:
				do_autopoints(convproj_obj, autoloc_start+['pan'], auto_node, 1, -1, False)
			#print(con_type, trackflags)

def do_effect_param(plugindata):
	name = plugindata.string(128)
	unkv = plugindata.uint32()
	value = plugindata.double()
	return name, value

native_names = {}
native_names['001DCD3345D14A13B59DAECF75A37536'] = 'stereodelay'
native_names['1CA6E894E4624F73ADEB29CD01DDE9EE'] = 'autopan'
native_names['25B0872DB12B44B89E32ABBC1D0B3D8A'] = 'morphfilter'
native_names['341FC589831D46A7A506BC0799E882AE'] = 'chorus'
native_names['37A3AA84E3A24D069C39030EC68768E1'] = 'pingpongdelay'
native_names['3B660266B3CA4B57BBD487AE1E6C0D2A'] = 'gate'
native_names['44A0C349905B45D0B97C72D2C6F5B565'] = 'maximizer'
native_names['54B0BB1DD40B4222BE4E876A87430F64'] = 'rotary'
native_names['56535452655642726F6F6D776F726B73'] = 'reverb'
native_names['5B38F28281144FFE80285FF7CCF20483'] = 'compressor'
native_names['6143DAECD6184AE2A570FE9F35065E24'] = 'dualfilter'
native_names['77BBA7CA90F14C9BB298BA9010D6DD78'] = 'stereoenhancer'
native_names['A990C1062CDE43839ECEF8FE91743DA5'] = 'distortion'
native_names['B11C7FF1D1C04E1CB83892F669540710'] = 'vibrato'
native_names['DDE3D98C0F22423AA2B32486ABEB2846'] = 'phaser'
native_names['E4B91D8420B74C48A8B10F2DB9CB707E'] = 'ampsimulator'
native_names['E97A6873690F40E986F3EE1007B5C8FC'] = 'tremolo'
native_names['FDD7243578EF434A833705ECC4E4CE46'] = 'flanger'

def do_effect(track_obj, slot, convproj_obj):
	if 'State' in slot:
		if slot['State']:
			if slot['Plugin isA'] == 'VstCtrlInternalEffect':
				#if native_names
				plugin = slot['Plugin']
				if 'Plugin UID' in plugin:
					if 'GUID' in plugin['Plugin UID']:
						guid = plugin['Plugin UID']['GUID']

						if guid in native_names:
							plugname = native_names[guid]

							plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'sequel', plugname)
							plugin_obj.role = 'effect'
							track_obj.plugslots.slots_audio.append(pluginid)

							plugindata = bytereader.bytereader()
							plugindata.load_raw(plugin['audioComponent'])
		
							unkd = plugindata.uint8()
							numparams = plugindata.uint8()
							plugindata.skip(2)

							params = {}

							while plugindata.remaining():
								name, value = do_effect_param(plugindata)
								params[name] = value

							for param_id, dset_param in globalstore.dataset.get_params('sequel', 'fx_plugin', plugname):
								paramval = params[param_id] if param_id in params else dset_param.defv
								plugin_obj.params.add(param_id, paramval, 'float')

						#else:
						#	print('plugin not found:', plugin['Plugin Name'], guid)

def do_effects(track_obj, track_device, convproj_obj):
	deviceattributes = track_device.deviceattributes
	#if 'hasEQ' in deviceattributes:
	#	if deviceattributes['hasEQ']:
	#		if 'EQ' in deviceattributes:
	#			seq_eq = deviceattributes['EQ']

	#			plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'eq', 'bands')
	#			plugin_obj.role = 'effect'
	#			track_obj.plugslots.slots_audio.append(pluginid)

	#			eqbands = seq_eq['Band']
	#			for num, band in enumerate(eqbands):
	#				filter_obj, filter_id = plugin_obj.eq_add()
	#				filter_obj.on = bool(band['Enable'])
	#				filter_obj.gain = band['Gain']
	#				filter_obj.type.set('peak', None)
	#				filter_obj.freq = band['Freq']
	#				#filter_obj.q = 1/(band['Q']/0.08851316571235657)
	#				if band['Type']:
	#					if num==0: filter_obj.type.set('high_pass', None)
	#					elif num==(len(eqbands)-1): filter_obj.type.set('low_pass', None)

	if 'InsertFolder' in deviceattributes:
		insertfolder = deviceattributes['InsertFolder']
		if 'Slot' in insertfolder:
			insertslots = insertfolder['Slot']
			for slot in insertslots:
				do_effect(track_obj, slot, convproj_obj)

class input_sequel3(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'sequel3'
	
	def get_name(self):
		return 'steinberg Sequel'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import sequel as proj_sequel
		from objects.file_proj_past._sequel import classobj
		from objects.file_proj_past._sequel import func
		from objects import audio_data

		samplefolder = dawvert_intent.path_samples['extracted']

		globalstore.dataset.load('z_maestro', './data_main/dataset/z_maestro.dset')

		convproj_obj.type = 'r'

		traits_obj = convproj_obj.traits
		traits_obj.audio_stretch = ['warp', 'rate']
		traits_obj.audio_filetypes = ['wav']
		traits_obj.auto_types = ['nopl_points']
		traits_obj.notes_midi = True
		traits_obj.placement_cut = True
		traits_obj.track_arranger = True

		project_obj = proj_sequel.sequel_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.dataset.load('sequel', './data_main/dataset/sequel.dset')
		colordata = colors.colorset.from_dataset('sequel', 'main', 'main')

		seq_project = project_obj.obj_project
		data_root = seq_project.data_root

		timebase = 480

		tempoid = data_root.tempo_track.obj_id
		if tempoid in func.globalids:
			tempo_track = classobj.get_object(func.globalids[tempoid])
			convproj_obj.params.add('bpm', tempo_track.rehearsaltempo, 'float')
			#for tempoevent in tempo_track.tempoevent:
			#	convproj_obj.automation.add_autotick(['main', 'bpm'], 'float', 0, tempoevent.bpm)

		convproj_obj.set_timings(timebase)

		tracklist = data_root.node
		for num, track in enumerate(tracklist.tracks):
			tracknum = 'track_'+str(num)

			if isinstance(track, classobj.class_MPlayRangeTrackEvent):
				track_node = track.node
				for event in track_node.events:
					timemarker_obj = convproj_obj.arranger.add()
					timemarker_obj.position = event.start
					timemarker_obj.duration = event.length
					timemarker_obj.type = 'region'
					timemarker_obj.visual.name = event.name

			if isinstance(track, classobj.class_MInstrumentTrackEvent):
				track_node = track.node
				track_device = track.track_device

				track_obj = convproj_obj.track__add(tracknum, 'instrument', 1, False)
				do_visual(track_obj, track, track_node, colordata)
				do_params(track_obj, track_device)
				do_effects(track_obj, track_device, convproj_obj)
				do_auto(track_obj, convproj_obj, track.automation, ['track', tracknum])

				for event in track_node.events:
					placement_obj = track_obj.placements.add_midi()
					delaystart = -min(event.offset, 0)

					placement_obj.time.set_posdur(event.start, event.length+delaystart)
					placement_obj.time.set_offset(event.offset)

					events_obj = placement_obj.midievents
					events_obj.has_duration = True
					events_obj.ppq = int(convproj_obj.time_ppq)

					if event.idnum in func.globalids:
						mmidipart = classobj.get_object(func.globalids[event.idnum])
						placement_obj.visual.name = mmidipart.name

						for event in mmidipart.events:
							startpos = max(0, event.start)+delaystart
							if isinstance(event, classobj.class_MMidiNote):
								events_obj.add_note_dur(startpos, 0, event.data1, event.data2, event.length)
							elif isinstance(event, classobj.class_MMidiController):
								events_obj.add_control(startpos, 0, event.data1, event.data2)

			if isinstance(track, classobj.class_MAudioTrackEvent):
				track_node = track.node
				track_device = track.track_device

				track_obj = convproj_obj.track__add(tracknum, 'audio', 1, False)
				do_visual(track_obj, track, track_node, colordata)
				do_params(track_obj, track_device)
				do_effects(track_obj, track_device, convproj_obj)
				do_auto(track_obj, convproj_obj, track.automation, ['track', tracknum])

				for event in track_node.events:
					placement_obj = track_obj.placements.add_audio()

					placement_obj.time.set_posdur(event.start, event.length)
					placement_obj.time.set_offset(event.offset)
					if event.idnum in func.globalids:
						paudioclip = classobj.get_object(func.globalids[event.idnum])
						placement_obj.visual.name = paudioclip.name

						audiopath = paudioclip.path
						filepath = audiopath.path+audiopath.name

						if event.flags == 2: placement_obj.muted = True

						sp_obj = placement_obj.sample
						sp_obj.gain = event.volume

						additional_attributes = event.additional_attributes
						if 'PitF' in additional_attributes:
							pitch = xtramath.speed_to_pitch(additional_attributes['PitF'])
							sp_obj.pitch = pitch
						if 'TransposeLock' in additional_attributes:
							sp_obj.usemasterpitch = not bool(paudioclip.additional_attributes['TransposeLock'])

						audiocluster = paudioclip.cluster.substreams

						if audiocluster:
							audiofile = audiocluster[0]
							partapath = paudioclip.path

							afilepath = partapath.path+partapath.name if partapath else filepath
							sampleref_obj = convproj_obj.sampleref__add(afilepath, afilepath, None)
							sampleref_obj.search_local(dawvert_intent.input_folder)
							sampleref_obj.set_hz(audiofile.rate)
							sampleref_obj.set_dur_samples(audiofile.framecount)
							sampleref_obj.set_channels(audiofile.channels)

							#sampleref_obj.search_local(dawvert_intent.input_folder)
							sp_obj.sampleref = filepath
							#for event in maudioevent.events:
	
							stretch_obj = sp_obj.stretch
							s_timing_obj = stretch_obj.timing
					
							stretch_obj.preserve_pitch = True

							if paudioclip.domain['Type'] == 10:
								placement_obj.time.set_dur_real(event.length/audiofile.rate)
								placement_obj.time.set_offset(event.offset/audiofile.rate)
								s_timing_obj.set__speed(1)
							else:
								if 'Warpscale' in paudioclip.additional_attributes:
									Warpscale = paudioclip.additional_attributes['Warpscale']
	
									with s_timing_obj.setup_warp(True) as warp_obj:
										dur_sec = sampleref_obj.get_dur_sec()
										hz = sampleref_obj.get_hz()
										dur_samples = sampleref_obj.get_dur_samples()
										if dur_sec: warp_obj.seconds = dur_sec
										for x in Warpscale.warptab:
											warp_pos = x.warped/timebase
											warp_sec = x.position/hz
											warp_obj.points__add_beatsec(warp_pos, warp_sec)

							if 'StretchPreset' in paudioclip.additional_attributes:
								StretchPreset = paudioclip.additional_attributes['StretchPreset']
								stretch_algo = stretch_obj.algorithm
								if isinstance(StretchPreset, classobj.class_ElastiquePreset):
									if StretchPreset.formantpreservation:
										stretch_algo.type = 'elastique_v3'
										stretch_algo.subtype = 'pro'
									else:
										stretch_algo.type = 'elastique_v3'
