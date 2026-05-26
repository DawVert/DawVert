# SPDX-FileCopyrightText: 2026 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
from functions import xtramath

def get_color(color):
	return color[2:]

def do_track_base(magda_track, track_obj):
	track_obj.visual.name = magda_track.name
	track_obj.visual.color.set_hex(get_color(magda_track.colour))
	track_obj.params.add('vol', magda_track.manualVolume, 'float')
	track_obj.params.add('pan', magda_track.manualPan, 'float')
	track_obj.params.add('solo', magda_track.soloed, 'bool')
	track_obj.params.add('enabled', not magda_track.muted, 'bool')

def do_placement_base(magda_clip, placement_obj):
	placement_obj.visual.name = magda_clip.name
	placement_obj.visual.color.set_hex(get_color(magda_clip.colour))
	mpl = magda_clip.placement
	if 'startBeat' in mpl and 'lengthBeats' in mpl:
		time_obj = placement_obj.time
		time_obj.set_posdur(mpl['startBeat'], mpl['lengthBeats'])

def doautopoints(auto_obj, abspoints, minv, maxv):
	for point in abspoints: 
		auto_obj.add_autopoint(point.beatPosition, xtramath.between_from_one(minv, maxv, point.value), None)

class input_magda(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'magda'
	
	def get_name(self):
		return 'MAGDA'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import magda as proj_magda

		convproj_obj.type = 'r'

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav','flac','ogg','mp3']
		traits_obj.audio_stretch = ['warp', 'rate']
		traits_obj.auto_types = ['nopl_points']
		traits_obj.placement_cut = True
		traits_obj.placement_loop = ['loop', 'loop_eq', 'loop_off', 'loop_adv', 'loop_adv_off']
		traits_obj.plugin_ext = ['vst3']
		traits_obj.plugin_ext_arch = [64]
		traits_obj.plugin_ext_platforms = ['win', 'unix']
		traits_obj.time_seconds = False
		traits_obj.track_hybrid = True

		convproj_obj.set_timings(1.0)

		project_obj = proj_magda.magda_session()

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		projprop = project_obj.project

		tempo = projprop.tempo
		timesig = projprop.timeSignature
		convproj_obj.metadata.name = projprop.name
		convproj_obj.params.add('bpm', tempo, 'float')
		convproj_obj.timesig = timesig

		loopd = projprop.loop
		convproj_obj.transport.loop_active = loopd.enabled
		convproj_obj.transport.loop_start = loopd.startBeats
		convproj_obj.transport.loop_end = loopd.endBeats

		sends_all = [] # send > [src, target, level, tomaster, sendautoid, native, prefader]
		send_nums = []
		sends_nomaster = []

		for x in project_obj.tracks:
			trackid = x.idnum

			if x.type==4: send_nums.append(trackid)

			if x.parentId>-1:
				outsend = {
					'is_standard': False,
					'native': True,
					'src': trackid,
					'target': x.parentId,
					'level': 1.0,
					'tomaster': False,
					'sendautoid': None,
					'prefader': False
				}
				sends_all.append(outsend)
				sends_nomaster.append(trackid)

			for send in x.sends:
				sendautoid = 'send_%s_%s' % (trackid, send.busIndex)
				outsend = {
					'is_standard': False,
					'native': False,
					'src': trackid,
					'target': send.destTrackId,
					'level': send.level,
					'tomaster': True,
					'sendautoid': sendautoid,
					'prefader': send.preFader
				}
				sends_all.append(outsend)

		for x in sends_all:
			x['to_send'] = x['target'] in send_nums
			if (x['to_send']==True) and (x['native']==False): x['is_standard'] = True
			if (x['to_send']==False) and (x['native']==True): x['is_standard'] = True

		is_standard = all([x['is_standard'] for x in sends_all])

		numassoc_all = {}
		numassoc_norm = {}
		numassoc_sendsrc = {}

		if is_standard:
			for x in project_obj.tracks:
				trackid = x.idnum

				cvpj_trackid = str(trackid)

				if x.type==0:
					track_obj = convproj_obj.track__add(cvpj_trackid, 'hybrid', 1, False)
					do_track_base(x, track_obj)
					numassoc_norm[trackid] = track_obj
					numassoc_all[trackid] = ['track', cvpj_trackid]
					if x.parentId>-1: track_obj.group = str(x.parentId)
					numassoc_sendsrc[trackid] = track_obj.sends

				elif x.type in [2, 3]:
					route_on = False
					track_obj = convproj_obj.fx__group__add(cvpj_trackid)
					track_obj.visual_track.group_expanded = True
					do_track_base(x, track_obj)
					numassoc_all[trackid] = ['group', cvpj_trackid]
					if x.parentId>-1: track_obj.group = str(x.parentId)
					numassoc_sendsrc[trackid] = track_obj.sends

				elif x.type==4:
					route_on = False
					track_obj = convproj_obj.track_master.fx__return__add(cvpj_trackid)
					do_track_base(x, track_obj)
					numassoc_all[trackid] = ['return', cvpj_trackid]
					numassoc_sendsrc[trackid] = track_obj.sends
		else:
			for x in project_obj.tracks:
				trackid = x.idnum

				cvpj_trackid = str(trackid)

				track_obj = convproj_obj.track__add(cvpj_trackid, 'hybrid', 1, False)
				do_track_base(x, track_obj)
				numassoc_norm[trackid] = track_obj
				numassoc_all[trackid] = ['track', cvpj_trackid]
				numassoc_sendsrc[trackid] = track_obj.sends
				if x.parentId>-1: track_obj.group = str(x.parentId)

		if is_standard:
			convproj_obj.fxtype = 'groupreturn'
			for send in sends_all:
				if send['to_send']:
					sends_obj = numassoc_sendsrc[send['src']]
					sends_obj.add(str(send['target']), send['sendautoid'], send['level'])
		else:
			convproj_obj.fxtype = 'route'
			sendalready = []
			sendin = {}

			for send in sends_all:
				track_src = send['src']
				ald = [track_src, send['target']]
				if ald not in sendalready:
					sendalready.append(ald)
					if track_src not in sendin: sendin[track_src] = []
					sendin[track_src].append(send)

			for sendsrc, senddata in sendin.items():
				sends_obj = convproj_obj.fx__route__add(str(sendsrc))
				sends_obj.to_master_active = sendsrc not in sends_nomaster
				for send in senddata:
					send_obj = sends_obj.add(str(send['target']), send['sendautoid'], send['level'])

		for x in project_obj.clips:
			trackid = x.trackId
			if trackid in numassoc_norm:
				track_obj = numassoc_norm[trackid]
				if x.type==1:
					placement_obj = track_obj.placements.add_notes()
					do_placement_base(x, placement_obj)
					if x.loopEnabled:
						time_obj = placement_obj.time
						time_obj.set_loop_data(0, 0, x.loopLengthBeats)

					cvpj_notelist = placement_obj.notelist
					for note in x.midiNotes:
						cvpj_notelist.add_r(note.startBeat, note.lengthBeats, note.noteNumber-60, note.velocity/100, None)

					autocc = {}
					for cc in x.midiCCData:
						if cc.controller not in autocc: autocc[cc.controller] = []
						autocc[cc.controller].append(cc)

					for ccnum, autodata in autocc.items():
						autopoints_obj = placement_obj.add_autopoints('midi_cc_'+str(ccnum))
						for p in autodata:
							autopoints_obj.points__add_normal(p.beatPosition, p.value, 0, None)

				if x.type==0:
					placement_obj = track_obj.placements.add_audio()
					do_placement_base(x, placement_obj)
					time_obj = placement_obj.time

					sp_obj = placement_obj.sample
					sp_obj.pan = x.pan
					sp_obj.vol = xtramath.from_db(x.volumeDB+x.gainDB) if x.volumeDB>-100 else 0
					sp_obj.pitch = x.pitchChange
					sp_obj.reverse = x.isReversed

					stretch_obj = sp_obj.stretch
					stretch_obj.preserve_pitch = True
					s_timing_obj = stretch_obj.timing

					placement_obj.fade_in.set_dur(x.fadeIn, 'seconds')
					if x.fadeInType==2: placement_obj.fade_in.slope = 1
					if x.fadeInType==3: placement_obj.fade_in.slope = -1

					placement_obj.fade_out.set_dur(x.fadeOut, 'seconds')
					if x.fadeOutType==2: placement_obj.fade_out.slope = 1
					if x.fadeOutType==3: placement_obj.fade_out.slope = -1

					audiodata = x.audio
					if audiodata:
						audio_source = audiodata.source
						if audio_source.filePath:
							filePath = audio_source.filePath
							sampleref_obj = convproj_obj.sampleref__add(filePath, filePath, None)
							sp_obj.sampleref = filePath
							if audio_source.durationSeconds:
								sampleref_obj.set_dur_sec(audio_source.durationSeconds)

						audio_playback = audiodata.playback
						audio_warpEnabled = audiodata.warpEnabled
						audio_warpMarkers = audiodata.warpMarkers

						offsetSeconds = audio_playback.offsetSeconds

						time_obj.set_offset_real(offsetSeconds)

						if not audio_warpEnabled:
							loopLengthBeats = audio_playback.loopLengthBeats
							if x.autoTempo and loopLengthBeats:
								s_timing_obj.set__beats(loopLengthBeats)
							else:
								speed = audio_playback.speedRatio
								s_timing_obj.set__speed(speed)
						else:
							dur_sec = sampleref_obj.get_dur_sec()

							loopLengthBeats = audio_playback.loopLengthBeats
							if x.autoTempo and loopLengthBeats:
								with s_timing_obj.setup_warp(True) as warp_obj:
									for marker in audio_warpMarkers:
										sourcetime = marker['sourceTime'] if 'sourceTime' in marker else 0.0
										warpTime = marker['warpTime'] if 'warpTime' in marker else 0.0
										dd = loopLengthBeats/(dur_sec*4)
										warp_obj.points__add_beatsec((warpTime*dd)*4, sourcetime)
									warp_obj.fix__remove_dupe_sec()
							else:
								with s_timing_obj.setup_warp(True) as warp_obj:
									for marker in audio_warpMarkers:
										sourcetime = marker['sourceTime'] if 'sourceTime' in marker else 0.0
										warpTime = marker['warpTime'] if 'warpTime' in marker else 0.0
										warp_obj.points__add_beatsec(warpTime*2, sourcetime*(120/tempo))
									warp_obj.fix__remove_dupe_sec()

		for x in project_obj.automation.lanes:
			target = x.target
			targtype = target.type
			if target.trackId in numassoc_all:
				startloc = numassoc_all[target.trackId]
				if targtype==5:
					sendautoid = 'send_%s_%s' % (target.trackId, target.sendBusIndex)
					auto_obj = convproj_obj.automation.create(['send', sendautoid, 'amount'], 'float', True)
					doautopoints(auto_obj, x.absolutePoints, 0, 1)
				elif targtype==3:
					auto_obj = convproj_obj.automation.create(startloc+['vol'], 'float', True)
					doautopoints(auto_obj, x.absolutePoints, 0, 1)
				elif targtype==4:
					auto_obj = convproj_obj.automation.create(startloc+['pan'], 'float', True)
					doautopoints(auto_obj, x.absolutePoints, -1, 1)
				elif targtype==0:
					topLevelDeviceId = target.devicePath['topLevelDeviceId']
					startloc = numassoc_all[target.trackId]
					auto_obj = convproj_obj.automation.create(['plugin', '%s_%s'%(target.trackId, topLevelDeviceId), 'param_'+str(target.paramIndex)], 'float', True)
					doautopoints(auto_obj, x.absolutePoints, 0, 1)
