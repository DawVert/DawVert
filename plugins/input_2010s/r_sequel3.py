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

#def do_effect(track_obj, slot):
#	if 'State' in slot:
#		if slot['State']:
#			if slot['Plugin isA'] == 'VstCtrlInternalEffect':
#				params = {}
#				#print(slot['Plugin isA'])
#				#if slot['Plugin isA'] == 

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

def do_effects(track_obj, track_device, convproj_obj):
	deviceattributes = track_device.deviceattributes
	if 'hasEQ' in deviceattributes:
		if deviceattributes['hasEQ']:
			if 'EQ' in deviceattributes:
				seq_eq = deviceattributes['EQ']

				plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'eq', 'bands')
				plugin_obj.role = 'effect'
				track_obj.plugslots.slots_audio.append(pluginid)

				eqbands = seq_eq['Band']
				for num, band in enumerate(eqbands):
					filter_obj, filter_id = plugin_obj.eq_add()
					filter_obj.on = bool(band['Enable'])
					filter_obj.gain = band['Gain']
					filter_obj.type.set('notch', None)
					filter_obj.freq = band['Freq']
					filter_obj.q = band['Q']/0.08851316571235657
					if band['Type']:
						if num==0: filter_obj.type.set('low_pass', None)
						elif num==(len(eqbands)-1): filter_obj.type.set('high_pass', None)

	#if 'hasEQ' in deviceattributes:
	#	insertfolder = track_device.deviceattributes['InsertFolder']
	#	if 'Slot' in insertfolder:
	#		insertslots = insertfolder['Slot']
	#		for slot in insertslots:
	#			do_effect(track_obj, slot)

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
					placement_obj.time.set_posdur(event.start, event.length)
					placement_obj.time.set_offset(event.offset)

					events_obj = placement_obj.midievents
					events_obj.has_duration = True
					events_obj.ppq = int(convproj_obj.time_ppq)

					if event.idnum in func.globalids:
						mmidipart = classobj.get_object(func.globalids[event.idnum])
						placement_obj.visual.name = mmidipart.name

						for event in mmidipart.events:
							startpos = max(0, event.start)
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

						sp_obj = placement_obj.sample

						if 'TransposeLock' in paudioclip.additional_attributes:
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
