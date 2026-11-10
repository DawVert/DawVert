# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions import data_values
from objects import globalstore
from collections import Counter

import os
import logging

from objects.convproj import project_traits
from objects.convproj import song_compat
from objects.convproj import sample_entry
from objects.convproj import automation
from objects.convproj import params
from objects.convproj import tracks
from objects.convproj import visual
from objects.convproj import sends
from objects.convproj import autoticks
from objects.convproj import autopoints
from objects.convproj import notelist
from objects.convproj import stretch
from objects.convproj import videoref
from objects.convproj import sampleref
from objects.convproj import realdevices
from objects.convproj import placements_marker
from objects.convproj import fx_rack
from objects.convproj import groups
from objects.convproj import project_parts

from objects import tempocalc

typelist = {}
typelist['r'] = 'Regular'
typelist['ri'] = 'RegularIndexed'
typelist['rm'] = 'RegularMultiple'
typelist['m'] = 'Multiple'
typelist['mi'] = 'MultipleIndexed'
typelist['cm'] = 'ClassicalMultiple'
typelist['cs'] = 'ClassicalSingle'

typelist['ts'] = 'TrackerSingle'
typelist['ms'] = 'MultipleScened'
typelist['rs'] = 'RegularScened'

conv_act    = {}
conv_act_r  = conv_act['r'] = {}
conv_act_ri = conv_act['ri'] = {}
conv_act_rm = conv_act['rm'] = {}
conv_act_rs = conv_act['rs'] = {}
conv_act_m  = conv_act['m'] = {}
conv_act_mi = conv_act['mi'] = {}
conv_act_ms = conv_act['ms'] = {}
conv_act_cm = conv_act['cm'] = {}
conv_act_cs = conv_act['cs'] = {}
conv_act_ts = conv_act['ts'] = {}

conv_act_r['m'] =   ['r2m']
conv_act_r['mi'] =  ['r2m','compat','m2mi']
conv_act_r['cm'] =  ['r2cm']
conv_act_r['cs'] =  ['r2cs']

conv_act_ri['r'] =  ['ri2r']
conv_act_ri['mi'] = ['ri2mi']
conv_act_ri['cm'] = ['ri2r','compat','r2cm']
conv_act_ri['cs'] = ['ri2r','compat','r2cm']

conv_act_rm['r'] =  ['rm2r','compat']
conv_act_rm['m'] =  ['rm2m']
conv_act_rm['mi'] = ['rm2m','compat','m2mi']
conv_act_rm['cm'] = ['rm2r','compat','r2cm']
conv_act_rm['cs'] = ['rm2r','compat','r2cm']

conv_act_rs['r'] =  ['rs2r']
conv_act_rs['mi'] = ['rs2r','compat','r2m','compat','m2mi']
conv_act_rs['cm'] = ['rs2r','compat','r2cm']
conv_act_rs['cs'] = ['rs2r','compat','r2cm']

conv_act_m['r'] =   ['m2r']
conv_act_m['mi'] =  ['m2mi']
conv_act_m['cm'] =  ['m2r','compat','r2cm']
conv_act_m['cs'] =  ['m2r','compat','r2cm']

conv_act_mi['r'] =  ['mi2m','compat','m2r','compat']
conv_act_mi['m'] =  ['mi2m']
conv_act_mi['cm'] = ['mi2m','compat','m2r','compat','r2cm']
conv_act_mi['cs'] = ['mi2m','compat','m2r','compat','r2cm']

conv_act_ms['r'] =  ['ms2rm','compat','rm2r']
conv_act_ms['rm'] = ['ms2rm'] # unused
conv_act_ms['m'] =  ['ms2rm','compat','rm2m'] # unused
conv_act_ms['mi'] = ['ms2rm','compat','rm2m','m2mi']
conv_act_ms['cm'] = ['ms2rm','compat','rm2r','compat','r2cm']
conv_act_ms['cs'] = ['ms2rm','compat','rm2r','compat','r2cm']

conv_act_cm['r'] =  ['cm2cs','compat','cs2r']
conv_act_cm['rm'] = ['cm2rm'] # unused
conv_act_cm['m'] =  ['cm2rm','compat','rm2m']
conv_act_cm['mi'] = ['cm2rm','compat','rm2m','compat','m2mi']

conv_act_cs['r'] =  ['cs2r']
conv_act_cs['rm'] = ['cs2cm','cm2rm'] # unused
conv_act_cs['m'] =  ['cs2cm','cm2rm','rm2m']
conv_act_cs['mi'] = ['cs2cm','cm2rm','rm2m','compat','m2mi']
conv_act_cs['cm'] = ['cs2cm']

conv_act_ts['r'] =  ['ts2m','m2r']
conv_act_ts['m'] =  ['ts2m']
conv_act_ts['mi'] = ['ts2m','m2mi']
conv_act_ts['cm'] = ['ts2m','m2r','compat','r2cm']
conv_act_ts['cs'] = ['ts2m','m2r','compat','r2cm']

logger_project = logging.getLogger('project')

def autopath_encode(autol):
	return ';'.join(autol)

def autoloc_getname(autopath):
	if autopath[0] == 'main': autoname = 'Main'
	if autopath[0] == 'fxmixer': autoname = 'FX '+autopath[1]
	if autopath[0] == 'send': autoname = 'Send'
	if autopath[0] == 'plugin': autoname = autopath[1]
	if autopath[0] == 'track': autoname = 'Track'

class cvpj_scene:
	def __init__(self, time_ppq, projid):
		self.time_ppq = time_ppq
		self.visual = visual.cvpj_visual()
		self.automation = automation.cvpj_automation(time_ppq, projid)

	def change_timings(self, time_ppq):
		self.time_ppq = time_ppq
		self.automation.change_timings(time_ppq)

class cvpj_scenepl:
	def __init__(self):
		self.position = 0
		self.duration = 0
		self.id = ''

class cvpj_transport:
	def __init__(self, time_ppq):
		self.time_ppq = time_ppq

		self.is_seconds = False

		self.loop_active = False
		self.loop_start = 0
		self.loop_end = 0
		self.start_pos = 0

		self.current_pos = 0

	def change_timings(self, time_ppq):
		if not self.is_seconds:
			self.loop_start = xtramath.change_timing(self.time_ppq, time_ppq, self.loop_start)
			self.loop_end = xtramath.change_timing(self.time_ppq, time_ppq, self.loop_end)
			self.start_pos = xtramath.change_timing(self.time_ppq, time_ppq, self.start_pos)
			self.current_pos = xtramath.change_timing(self.time_ppq, time_ppq, self.current_pos)

	def change_seconds(self, is_seconds, bpm, ppq):
		if is_seconds and not self.is_seconds:
			self.loop_start = xtramath.step2sec(self.loop_start, bpm)/(ppq/4)
			self.loop_end = xtramath.step2sec(self.loop_end, bpm)/(ppq/4)
			self.start_pos = xtramath.step2sec(self.start_pos, bpm)/(ppq/4)
			self.current_pos = xtramath.step2sec(self.current_pos, bpm)/(ppq/4)
			self.is_seconds = True
		elif self.is_seconds:
			self.loop_start = xtramath.sec2step(self.loop_start, bpm)
			self.loop_end = xtramath.sec2step(self.loop_end, bpm)
			self.start_pos = xtramath.sec2step(self.start_pos, bpm)
			self.current_pos = xtramath.sec2step(self.current_pos, bpm)
			self.is_seconds = False
		
class cvpj_project_midi_custom_instrument:
	def __init__(self):
		self.track = None
		self.chan = None
		self.bank_hi = None
		self.bank = None
		self.patch = None
		self.visual = visual.cvpj_visual()
		self.pluginid = None

	def get_match_dict(self):
		out = {}
		if self.track is not None: out['track'] = self.track
		if self.chan is not None: out['chan'] = self.chan
		if self.bank_hi is not None: out['bank_hi'] = self.bank_hi
		if self.bank is not None: out['bank'] = self.bank
		if self.patch is not None: out['patch'] = self.patch
		return out

class cvpj_project_midi:
	def __init__(self):
		self.num_channels = 16
		self.num_ports = 1

class cvpj_project:
	def __init__(self):
		self.id = 'global'
		self.params = params.cvpj_paramset()
		self.folder_prefixes = project_parts.cvpj_project_folderprefixes(self)

		# type and traits
		self.type = None
		self.fxtype = 'none'
		self.traits = project_traits.cvpj_project_traits()

		# time
		self.time_ppq = 96
		self.time_tempocalc = tempocalc.tempocalc_store(self)
		tempocalc.global_stores[self.id] = self.time_tempocalc

		# tracks
		self.tracks = project_parts.cvpj_project_tracks(self)
		self.track_master = tracks.cvpj_track('master', self.time_ppq, False, False)

		# markers and automation
		self.timemarkers = placements_marker.cvpj_placements_marker(self.time_ppq)
		self.arranger = placements_marker.cvpj_placements_marker(self.time_ppq)
		self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, 'timesig')
		self.automation = automation.cvpj_automation(self.time_ppq, self.id)

		# file ref
		self.filerefs = project_parts.cvpj_project_filerefs(self)
		self.samplerefs = project_parts.cvpj_project_samplerefs(self)
		self.videorefs = {}

		# others
		self.plugins = project_parts.cvpj_project_plugins(self)
		self.timesig = [4,4]
		self.do_actions = []
		self.metadata = visual.cvpj_metadata()
		self.transport = cvpj_transport(self.time_ppq)
		self.window_data = {}
		self.sample_folders = []
		self.realdevices = realdevices.cvpj_realdevicelist()
		self.freq = 44100
		self._m2r_visual_playlist_first = False

		# ------------------- cvpj type -------------------
		# *Indexed
		self.sample_index = {}
		self.notelist_index = {}

		# Multiple, MultipleIndexed and similar
		self.playlist = {}
		self.instruments = project_parts.cvpj_project_instruments(self)

		# *Tracked
		self.tracker_single = None

		# *Scened
		self.scenes = {}
		self.scene_placements = []

		# MIDI
		self.midi = cvpj_project_midi()
		self.midi_cust_inst = []


		# ------------------- fxtype -------------------
		# groupreturn
		self.groups = groups.cvpj_groups(self)
		self.track_returns = {}

		# fxrack
		self.fxrack = fx_rack.cvpj_fxrack()

		# route
		self.trackroute = {}


# --------------------------------------------------------- MAIN ---------------------------------------------------------

	def main__create_tracker_single(self):
		from objects.convproj.tracker import pat_single
		self.type = 'ts'
		self.tracker_single = pat_single.convproj_tracker_patsong()
		return self.tracker_single

	def main__change_type(self, in_dawinfo, out_dawinfo, out_type, dawvert_intent):
		actions_obj = song_compat.compat_actions()
		actions_obj.convproj_obj = self
		actions_obj.in_dawinfo = in_dawinfo
		actions_obj.out_dawinfo = out_dawinfo
		actions_obj.out_type = out_type
		actions_obj.dawvert_intent = dawvert_intent

		traits_obj = self.traits
		if self.type in ['m', 'mi', 'rm', 'ms', 'ts', 'cs', 'cm', 'rs']:
			traits_obj.track_lanes = True

		actions_obj.makecompat()

		if self.type != out_type:
			notfound = False
			if self.type in conv_act:
				if out_type in conv_act[self.type]: actions_obj.do_cmd_order(conv_act[self.type][out_type])
				else: notfound = True
			else: notfound = True
			if notfound: logger_project.error(typelist[self.type]+' to '+typelist[out_type]+' is not supported.')

		elif self.type == out_type: pass
		
		else:
			logger_project.error(typelist[self.type]+' to '+typelist[out_type]+' is not supported.')
			exit()

		actions_obj.makecompat()

	def main__add_midi_custom_inst(self):
		cust_inst = cvpj_project_midi_custom_instrument()
		self.midi_cust_inst.append(cust_inst)
		return cust_inst

	def set_timings(self, time_ppq):
		self.time_ppq = time_ppq
		self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, 'timesig')
		self.automation.time_ppq = self.time_ppq
		self.timemarkers = placements_marker.cvpj_placements_marker(self.time_ppq)
		self.arranger = placements_marker.cvpj_placements_marker(self.time_ppq)
		self.transport = cvpj_transport(self.time_ppq)

	def change_timings(self, time_ppq):
		logger_project.info('Changing Timings from '+str(self.time_ppq)+' to '+str(time_ppq))
		self.tracks.change_timings(time_ppq)
		for p in self.playlist: self.playlist[p].change_timings(time_ppq)
		for _, n in self.notelist_index.items(): 
			n.notelist.change_timings(time_ppq)
			n.timesig_auto.change_timings(time_ppq)
		self.timemarkers.change_timings(time_ppq)
		self.arranger.change_timings(time_ppq)
		self.timesig_auto.change_timings(time_ppq)
		self.transport.change_timings(time_ppq)
		self.time_ppq = time_ppq
		self.automation.change_timings(time_ppq)
		for _, scene in self.scenes.items(): scene.change_timings(time_ppq)

	def get_dur(self):
		duration_final = 0
		for p in self.tracks.data: 
			track_data = self.tracks.data[p]
			trk_dur = track_data.placements.get_dur()
			if duration_final < trk_dur: duration_final = trk_dur
		for p in self.playlist: 
			track_data = self.playlist[p]
			trk_dur = track_data.placements.get_dur()
			if duration_final < trk_dur: duration_final = trk_dur
		return duration_final

	def add_timesig_lengthbeat(self, pat_len, notes_p_beat):
		self.timesig = xtramath.get_timesig(pat_len, notes_p_beat)

	def add_autopoints_twopoints(self, autopath, v_type, twopoints):
		for x in twopoints: self.add_autopoint(autopath, v_type, x[0], x[1], 'normal')

	def calc_pl_tempo(self): 
		if self.time_tempocalc.auto_found>=0:
			for x in self.iter__placements_obj():
				x.do_tempo(self.time_tempocalc)

# --------------------------------------------------------- SCENE ---------------------------------------------------------

	def scene__add(self, i_sceneid):
		scene_obj = cvpj_scene(self.time_ppq, self.id)
		#cpr_int('[project] Scene - '+str(i_sceneid), 'magenta')
		logger_project.info('Scene - '+str(i_sceneid))
		self.scenes[i_sceneid] = scene_obj
		return scene_obj

	def scene__add_pl(self):
		scene_obj = cvpj_scenepl()
		self.scene_placements.append(scene_obj)
		return scene_obj

# --------------------------------------------------------- TIMEMARKERS ---------------------------------------------------------

	def timemarker__add(self):
		return self.timemarkers.add()

	def timemarker__add_key(self, key):
		return self.timemarkers.add_key(key)

	def timemarker__from_patlenlist(self, PatternLengthList, pos_loop):
		prevtimesig = self.timesig
		currentpos = 0
		blockcount = 0

		self.loop_end = sum(PatternLengthList)
		self.loop_active = True

		for PatternLengthPart in PatternLengthList:
			temptimesig = xtramath.get_timesig(PatternLengthPart, self.timesig[1])
			if prevtimesig != temptimesig: 
				outtimesig = temptimesig.copy()
				if not outtimesig[0]%outtimesig[1]: outtimesig[0] = outtimesig[1]
				self.timesig_auto.add_point(currentpos, outtimesig)
			if pos_loop == blockcount: self.loop_start = currentpos
			prevtimesig = temptimesig
			currentpos += PatternLengthPart
			blockcount += 1

# --------------------------------------------------------- AUTOMATION ---------------------------------------------------------

	def automation__iter(self):
		for autopath in self.automation:
			yield autopath.split(';'), self.automation[autopath]

# --------------------------------------------------------- FX ---------------------------------------------------------

	def fx__route__add(self, trackid):
		if trackid not in self.trackroute: 
			#cpr_int('[project] Track Route - '+str(trackid), 'yellow')
			logger_project.info('Track Route - '+str(trackid))
			self.trackroute[trackid] = sends.cvpj_sends()
		return self.trackroute[trackid]

	def fx__route__clear(self):
		self.trackroute = {}

	def fx__return__add(self, track_id):
		self.track_returns[track_id] = tracks.cvpj_track('return', self.time_ppq, False, False)
		return self.track_returns[track_id]

	def fx__return__clear(self):
		self.track_returns = {}

# --------------------------------------------------------- NOTELIST INDEX ---------------------------------------------------------

	def notelistindex__add(self, i_id):
		self.notelist_index[i_id] = tracks.cvpj_nle(self.time_ppq)
		return self.notelist_index[i_id]

	def notelistindex__iter(self):
		for i_id in self.notelist_index: yield i_id, self.notelist_index[i_id]

# --------------------------------------------------------- SAMPLE INDEX ---------------------------------------------------------

	def sampleindex__add(self, i_id):
		self.sample_index[i_id] = sample_entry.cvpj_sample_entry()
		return self.sample_index[i_id]

	def sampleindex__iter(self):
		for i_id in self.sample_index: yield i_id, self.sample_index[i_id]

# --------------------------------------------------------- VISUAL WINDOW ---------------------------------------------------------

	def viswindow__add(self, windowpath):
		windowpath = autopath_encode(windowpath)
		self.window_data[windowpath] = visual.cvpj_window_data()
		return self.window_data[windowpath]

	def viswindow__get(self, windowpath):
		windowpath = autopath_encode(windowpath)
		if windowpath in self.window_data: return self.window_data[windowpath]

# --------------------------------------------------------- PLAYLIST ---------------------------------------------------------

	def playlist__add(self, idnum, uses_placements, is_indexed):
		if idnum not in self.playlist:
			logger_project.info('Playlist '+('NoPl' if not uses_placements else 'w/Pl')+(' + Indexed' if is_indexed else '')+' - '+str(idnum))
			self.playlist[idnum] = tracks.cvpj_track('hybrid', self.time_ppq, uses_placements, is_indexed)
		return self.playlist[idnum]

	def playlist__iter(self):
		for idnum, playlist_obj in self.playlist.items():
			yield idnum, playlist_obj

# --------------------------------------------------------- VIDEOREF ---------------------------------------------------------

	def videoref__add(self, fileid, filepath, os_type):
		if fileid not in self.videorefs: 
			self.videorefs[fileid] = videoref.cvpj_videoref(self)
			self.videorefs[fileid].set_path(os_type, filepath)
			logger_project.info('VideoRef - '+fileid+' - '+filepath)
		return self.videorefs[fileid]

	def videoref__iter(self):
		for videoref_id, videoref_obj in self.videorefs.items():
			yield videoref_id, videoref_obj

	def videoref__get(self, fileid):
		if fileid in self.videorefs: return True, self.videorefs[fileid]
		else: return False, None

	#def videoref__searchmissing(self, input_file):
	#	dirpath = os.path.dirname(input_file)
	#	files = fileref.filesearcher.searchcache

	#	for videoref_id, videoref_obj in self.videoref__iter():
	#		if not videoref_obj.found:
	#			fileref.filesearcher.scan_local_files(dirpath)
	#			videoref_obj.search_local(dirpath)

# --------------------------------------------------------- ITER ---------------------------------------------------------

	def iter__placements_obj(self):
		for _, track_obj in self.tracks.data.items():
			yield track_obj.placements
			for _, lane_obj in track_obj.lanes.items():
				yield lane_obj.placements
		for _, track_obj in self.playlist.items():
			yield track_obj.placements