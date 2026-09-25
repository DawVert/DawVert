# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import counter as idcounter
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
from objects.convproj import plugin
from objects.convproj import fileref
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

from functions.convproj_types import convert_r2m
from functions.convproj_types import convert_ri2mi
from functions.convproj_types import convert_ri2r
from functions.convproj_types import convert_rm2r
from functions.convproj_types import convert_m2r
from functions.convproj_types import convert_m2mi
from functions.convproj_types import convert_mi2m
from functions.convproj_types import convert_rm2m
from functions.convproj_types import convert_ts2m
from functions.convproj_types import convert_ms2rm
from functions.convproj_types import convert_rs2r
from functions.convproj_types import convert_cm2rm
from functions.convproj_types import convert_cs2cm
from functions.convproj_types import convert_r2cm

from objects import tempocalc

typelist = {}
typelist['r'] = 'Regular'
typelist['ri'] = 'RegularIndexed'
typelist['rm'] = 'RegularMultiple'
typelist['rs'] = 'RegularScened'
typelist['m'] = 'Multiple'
typelist['mi'] = 'MultipleIndexed'
typelist['ms'] = 'MultipleScened'
typelist['ts'] = 'TrackerSingle'
typelist['cm'] = 'ClassicalMultiple'
typelist['cs'] = 'ClassicalSingle'

logger_project = logging.getLogger('project')

def autopath_encode(autol):
	return ';'.join(autol)

def vis_plugin(p_category, p_type, p_subtype):
	if p_category != None and p_type != None and p_subtype != None: return p_category+':'+p_type+':'+p_subtype
	elif p_category != None and p_type != None and p_subtype == None: return p_category+':'+p_type
	elif p_category != None and p_type == None and p_subtype == None: return p_category
	elif p_category == None and p_type == None and p_subtype == None: return 'None'

def autoloc_getname(autopath):
	if autopath[0] == 'main': autoname = 'Main'
	if autopath[0] == 'fxmixer': autoname = 'FX '+autopath[1]
	if autopath[0] == 'send': autoname = 'Send'
	if autopath[0] == 'plugin': autoname = autopath[1]
	if autopath[0] == 'track': autoname = 'Track'

plugin_id_counter = idcounter.counter(1000, 'plugin_')

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

class cvpj_project_instruments:
	def __init__(self, convproj_obj):
		self.data = {}
		self.order = []
		self.convproj_obj = convproj_obj

	def __getitem__(self, k):
		return self.data.__getitem__(k)

	def __contains__(self, k):
		return self.data.__contains__(k)

	def add(self, inst_id):
		logger_project.info('Instrument - '+str(inst_id))
		self.data[inst_id] = tracks.cvpj_instrument()
		self.order.append(inst_id)
		return self.data[inst_id]

	def iter(self):
		for inst_id in self.order:
			if inst_id in self.data: yield inst_id, self.data[inst_id]

	def enumerate(self):
		count = 0
		for inst_id in self.order:
			if inst_id in self.data: 
				yield count, inst_id, self.data[inst_id]
				count += 1

	def clear(self):
		self.data = {}
		self.order = []

class cvpj_project:
	def __init__(self):
		self.id = 'global'
		self.params = params.cvpj_paramset()

		# type and traits
		self.type = None
		self.fxtype = 'none'
		self.traits = project_traits.cvpj_project_traits()

		# time
		self.time_ppq = 96
		self.time_tempocalc = tempocalc.tempocalc_store(self)
		tempocalc.global_stores[self.id] = self.time_tempocalc

		# tracks
		self.tracks = tracks.cvpj_project_tracks(self)
		self.track_master = tracks.cvpj_track('master', self.time_ppq, False, False)

		# markers and automation
		self.timemarkers = placements_marker.cvpj_placements_marker(self.time_ppq)
		self.arranger = placements_marker.cvpj_placements_marker(self.time_ppq)
		self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, 'timesig')
		self.automation = automation.cvpj_automation(self.time_ppq, self.id)

		# file ref
		self.filerefs = {}
		self.samplerefs = {}
		self.videorefs = {}

		# others
		self.plugins = {}
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
		self.instruments = cvpj_project_instruments(self)

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
		compactclass = song_compat.song_compat()

		traits_obj = self.traits
		if self.type in ['m', 'mi', 'rm', 'ms', 'ts', 'cs', 'cm', 'rs']:
			traits_obj.track_lanes = True

		compactclass.makecompat(self, self.type, in_dawinfo, out_dawinfo, out_type, dawvert_intent)

		if self.type == 'ri' and out_type == 'mi': convert_ri2mi.convert(self)
		elif self.type == 'ri' and out_type == 'r': convert_ri2r.convert(self)
		elif self.type == 'ri' and out_type in ['r', 'cs', 'cm']: 
			convert_ri2r.convert(self)
			if out_type == 'cs':
				compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
				convert_r2cm.convert(self)
			if out_type == 'cm':
				compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
				convert_r2cm.convert(self)

		elif self.type == 'ts' and out_type == 'm':
			convert_ts2m.convert(self)
		elif self.type in ['m', 'ts'] and out_type == 'mi':
			if self.type == 'ts': convert_ts2m.convert(self)
			convert_m2mi.convert(self)
		elif self.type in ['m', 'ts'] and out_type in ['r', 'cs', 'cm']: 
			if self.type == 'ts': convert_ts2m.convert(self)
			convert_m2r.convert(self)
			if out_type == 'cs':
				compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
				convert_r2cm.convert(self)
			if out_type == 'cm':
				compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
				convert_r2cm.convert(self)

		elif self.type == 'r' and out_type == 'm': convert_r2m.convert(self)
		elif self.type == 'r' and out_type == 'mi': 
			convert_r2m.convert(self)
			compactclass.makecompat(self, 'm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_m2mi.convert(self)
		elif self.type == 'r' and out_type in ['cs', 'cm']: 
			convert_r2cm.convert(self)
			if out_type == 'cm': convert_cs2cm.convert(self)

		elif self.type == 'mi' and out_type == 'm': convert_mi2m.convert(self, dawvert_intent)
		elif self.type == 'mi' and out_type in ['r', 'cs', 'cm']: 
			convert_mi2m.convert(self, dawvert_intent)
			compactclass.makecompat(self, 'm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_m2r.convert(self)
			compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			if out_type == 'cs':
				convert_r2cm.convert(self)
			if out_type == 'cm':
				convert_r2cm.convert(self)
	
		elif self.type == 'rm' and out_type in ['r', 'cs', 'cm']: 
			convert_rm2r.convert(self)
			compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			if out_type == 'cs':
				convert_r2cm.convert(self)
			if out_type == 'cm':
				convert_r2cm.convert(self)
		elif self.type == 'rm' and out_type == 'm': convert_rm2m.convert(self, True)
		elif self.type == 'rm' and out_type == 'mi': 
			convert_rm2m.convert(self, True)
			compactclass.makecompat(self, 'm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_m2mi.convert(self)

		elif self.type == 'rs' and out_type == 'mi': 
			convert_rs2r.convert(self)
			compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_r2m.convert(self)
			compactclass.makecompat(self, 'm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_m2mi.convert(self)

		elif self.type == 'rs' and out_type == 'r': 
			convert_rs2r.convert(self)

		elif self.type == 'rs' and out_type in ['cs', 'cm']: 
			convert_rs2r.convert(self)
			compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_r2cm.convert(self)
			if out_type == 'cm': convert_cs2cm.convert(self)

		elif self.type == 'ms' and out_type == 'mi': 
			convert_ms2rm.convert(self, out_dawinfo)
			compactclass.makecompat(self, 'rm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_rm2m.convert(self, True)
			convert_m2mi.convert(self)

		elif self.type == 'ms' and out_type in ['r', 'cs', 'cm']: 
			convert_ms2rm.convert(self, out_dawinfo)
			compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_rm2r.convert(self)
			if out_type == 'cs':
				compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
				convert_r2cm.convert(self)
			if out_type == 'cm':
				compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
				convert_r2cm.convert(self)


		elif self.type == 'cm' and out_type == 'r':
			convert_cm2rm.convert(self)
			compactclass.makecompat(self, 'rm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_rm2r.convert(self)

		elif self.type == 'cm' and out_type == 'm':
			convert_cm2rm.convert(self)
			compactclass.makecompat(self, 'rm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_rm2m.convert(self, True)

		elif self.type == 'cm' and out_type == 'mi': 
			convert_cm2rm.convert(self)
			compactclass.makecompat(self, 'rm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_rm2m.convert(self, True)
			compactclass.makecompat(self, 'm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_m2mi.convert(self)

		elif self.type == 'cs' and out_type == 'cm':
			convert_cs2cm.convert(self)

		elif self.type == 'cs' and out_type == 'r':
			convert_cs2cm.convert(self)
			convert_cm2rm.convert(self)
			compactclass.makecompat(self, 'rm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_rm2r.convert(self)

		elif self.type == 'cs' and out_type == 'm':
			convert_cs2cm.convert(self)
			convert_cm2rm.convert(self)
			compactclass.makecompat(self, 'rm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_rm2m.convert(self, True)

		elif self.type == 'cs' and out_type == 'mi': 
			convert_cs2cm.convert(self)
			convert_cm2rm.convert(self)
			compactclass.makecompat(self, 'rm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_rm2m.convert(self, True)
			compactclass.makecompat(self, 'm', in_dawinfo, out_dawinfo, out_type, dawvert_intent)
			convert_m2mi.convert(self)

		elif self.type == out_type: 
			pass
		
		else:
			logger_project.error(typelist[self.type]+' to '+typelist[out_type]+' is not supported.')
			exit()

		compactclass.makecompat(self, out_type, in_dawinfo, out_dawinfo, out_type, dawvert_intent)

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

# --------------------------------------------------------- FILEREF ---------------------------------------------------------

	def fileref__add(self, fileid, filepath, os_type):
		if fileid not in self.filerefs: 
			self.filerefs[fileid] = fileref.cvpj_fileref()
			self.filerefs[fileid].set_path(os_type, filepath, 0)
			logger_project.info('FileRef - '+fileid+' - '+filepath)
		return self.filerefs[fileid]

	def fileref__add__prefix(self, fileid, prefix, filepath):
		if fileid not in self.filerefs: 
			self.filerefs[fileid] = fileref.cvpj_fileref()
			self.filerefs[fileid].set_path_prefix(prefix, filepath, 1)
			logger_project.info('FileRef - '+fileid+' - '+filepath)
		return self.filerefs[fileid]

	def fileref__get(self, fileid):
		if fileid in self.filerefs: return True, self.filerefs[fileid]
		else: return False, None

	def fileref__iter(self):
		for fileid_id, fileid_obj in self.filerefs.items():
			yield fileid_id, fileid_obj

# --------------------------------------------------------- SAMPLEREF ---------------------------------------------------------

	def sampleref__add(self, fileid, filepath, os_type):
		if fileid not in self.samplerefs: 
			self.samplerefs[fileid] = sampleref.cvpj_sampleref()
			self.samplerefs[fileid].set_path(os_type, filepath)
			logger_project.info('SampleRef - '+fileid+' - '+filepath)
		return self.samplerefs[fileid]

	def sampleref__add__prefix(self, fileid, prefix, filepath):
		if fileid not in self.samplerefs: 
			self.samplerefs[fileid] = sampleref.cvpj_sampleref()
			self.samplerefs[fileid].set_path_prefix(prefix, filepath)
			logger_project.info('SampleRef - '+fileid+' - '+filepath)
		return self.samplerefs[fileid]

	def sampleref__iter(self):
		for sampleref_id, sampleref_obj in self.samplerefs.items():
			yield sampleref_id, sampleref_obj

	def sampleref__get(self, fileid):
		if fileid in self.samplerefs: return True, self.samplerefs[fileid]
		else: return False, None

	def sampleref__searchmissing(self, input_file):
		dirpath = os.path.dirname(input_file)
		files = fileref.filesearcher.searchcache

		for sampleref_id, sampleref_obj in self.sampleref__iter():
			if not sampleref_obj.found:
				fileref.filesearcher.scan_local_files(dirpath)
				sampleref_obj.search_local(dirpath)

	def sampleref__remove_nonaudiopl(self):
		sflist = list(self.samplerefs)
		for trackid, track_obj in self.tracks.iter():
			for audiopl_obj in track_obj.placements.pl_audio:
				if audiopl_obj.sample.sampleref in sflist: sflist.remove(audiopl_obj.sample.sampleref)

			for nestedpl_obj in track_obj.placements.pl_audio_nested:
				for audiopl_obj in nestedpl_obj.events:
					if audiopl_obj.sample.sampleref in sflist: sflist.remove(audiopl_obj.sample.sampleref)

			for laneid, lane_obj in track_obj.lanes.items():
				for audiopl_obj in lane_obj.placements.pl_audio:
					if audiopl_obj.sample.sampleref in sflist: sflist.remove(audiopl_obj.sample.sampleref)
					
		for s in sflist: del self.samplerefs[s]

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

# --------------------------------------------------------- PLUGIN ---------------------------------------------------------

	def plugin__get(self, plug_id):
		if plug_id in self.plugins: return True, self.plugins[plug_id]
		else: return False, None

	def plugin__add(self, plug_id, i_category, i_type, i_subtype):
		logger_project.info('Plugin - '+str(plug_id)+' - '+vis_plugin(i_category, i_type, i_subtype))
		plugin_obj = plugin.cvpj_plugin()
		plugin_obj.replace(i_category, i_type, i_subtype)
		self.plugins[plug_id] = plugin_obj
		return self.plugins[plug_id]

	def plugin__add__genid(self, i_category, i_type, i_subtype):
		plug_id = plugin_id_counter.get_str_txt()
		logger_project.info('Plugin - '+str(plug_id)+' - '+vis_plugin(i_category, i_type, i_subtype))
		plugin_obj = plugin.cvpj_plugin()
		plugin_obj.replace(i_category, i_type, i_subtype)
		self.plugins[plug_id] = plugin_obj
		return self.plugins[plug_id], plug_id

	def plugin__addspec__sampler__genid(self, file_path, os_type, **kwargs):
		plug_id = plugin_id_counter.get_str_txt()
		plugin_obj, sampleref_obj, samplepart_obj = self.plugin__addspec__sampler(plug_id, file_path, os_type, **kwargs)
		plugin_obj.role = 'synth'
		return plugin_obj, plug_id, sampleref_obj, samplepart_obj

	def plugin__addspec__sampler(self, plug_id, file_path, os_type, **kwargs):
		if file_path:
			sampleref = kwargs['sampleid'] if 'sampleid' in kwargs else file_path
			prefix = kwargs['prefix'] if 'prefix' in kwargs else None
			if not prefix:
				sampleref_obj = self.sampleref__add(sampleref, file_path, os_type)
			else:
				sampleref_obj = self.sampleref__add__prefix(sampleref, kwargs['prefix'], file_path)
				sampleref_obj.fileref.resolve_prefix()

			is_drumsynth = sampleref_obj.fileref.file.extension.lower() == 'ds'
		else:
			sampleref_obj = None
			is_drumsynth = False

		if not is_drumsynth:
			plugin_obj = self.plugin__add(plug_id, 'universal', 'sampler', 'single')
			plugin_obj.role = 'synth'
			samplepart_obj = plugin_obj.samplepart_add('sample')
			if file_path: samplepart_obj.from_sampleref(self, sampleref)
		else:
			plugin_obj = self.plugin__add(plug_id, 'universal', 'sampler', 'drumsynth')
			plugin_obj.role = 'synth'
			samplepart_obj = plugin_obj.samplepart_add('sample')
			if file_path:
				samplepart_obj.sampleref = sampleref
				from objects.inst_params import drumsynth
				drumsynth_obj = drumsynth.drumsynth_main()
				drumsynth_obj.load_from_file(file_path)
				drumsynth_obj.to_plugin(plugin_obj)

		return plugin_obj, sampleref_obj, samplepart_obj

	def plugin__addspec__sampler__s_obj(self, plug_id, sampleref_obj, sampleref, **kwargs):
		plugin_obj = self.plugin__add(plug_id, 'universal', 'sampler', 'single')
		plugin_obj.role = 'synth'
		samplepart_obj = plugin_obj.samplepart_add('sample')
		samplepart_obj.from_sampleref(self, sampleref)
		return plugin_obj, samplepart_obj

	def plugin__addspec__sampler__genid__s_obj(self, sampleref_obj, sampleref, **kwargs):
		plug_id = plugin_id_counter.get_str_txt()
		plugin_obj, samplepart_obj = self.plugin__addspec__sampler__s_obj(plug_id, sampleref_obj, sampleref, **kwargs)
		plugin_obj.role = 'synth'
		return plugin_obj, plug_id, samplepart_obj

	def plugin__addspec__midi(self, plug_id, indict):
		plugin_obj = self.plugin__add(plug_id, 'universal', 'midi', None)
		plugin_obj.role = 'synth'
		plugin_obj.midi.from_dict(indict)
		return plugin_obj

	def plugin__addspec__midi_from_datapack(self, plug_id, ds_id, ds_cat, ds_obj):
		dso_obj = globalstore.datapack.get_obj(ds_id, ds_cat, ds_obj)
		dso_midi = dso_obj.midi if dso_obj else None

		if dso_midi:
			plugin_obj = self.plugin__add(plug_id, 'universal', 'midi', None)
			plugin_obj.role = 'synth'
			midi_obj = plugin_obj.midi
			midi_obj.bank = dso_midi.bank
			midi_obj.patch = dso_midi.patch
			midi_obj.drum = dso_midi.is_drum
			return plugin_obj

# --------------------------------------------------------- VIDEOREF ---------------------------------------------------------

	def videoref__add(self, fileid, filepath, os_type):
		if fileid not in self.videorefs: 
			self.videorefs[fileid] = videoref.cvpj_videoref()
			self.videorefs[fileid].set_path(os_type, filepath)
			logger_project.info('VideoRef - '+fileid+' - '+filepath)
		return self.videorefs[fileid]

	def videoref__iter(self):
		for videoref_id, videoref_obj in self.videorefs.items():
			yield videoref_id, videoref_obj

	def videoref__get(self, fileid):
		if fileid in self.videorefs: return True, self.videorefs[fileid]
		else: return False, None

	def videoref__searchmissing(self, input_file):
		dirpath = os.path.dirname(input_file)
		files = fileref.filesearcher.searchcache

		for videoref_id, videoref_obj in self.videoref__iter():
			if not videoref_obj.found:
				fileref.filesearcher.scan_local_files(dirpath)
				videoref_obj.search_local(dirpath)

# --------------------------------------------------------- ITER ---------------------------------------------------------

	def iter__placements_obj(self):
		for _, track_obj in self.tracks.data.items():
			yield track_obj.placements
			for _, lane_obj in track_obj.lanes.items():
				yield lane_obj.placements
		for _, track_obj in self.playlist.items():
			yield track_obj.placements