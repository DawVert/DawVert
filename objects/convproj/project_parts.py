# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import counter as idcounter

from objects.convproj import fileref
from objects.convproj import plugin
from objects.convproj import tracks
from objects.convproj import sampleref

from objects import globalstore

import logging
import zlib

logger_project = logging.getLogger('project')

# ------------------- folder prefixes -------------------

def fprefix_split(groupname):
	splitname = groupname.split(':', 1)
	if splitname:
		group = splitname[0]
		name = splitname[1] if len(splitname)==2 else 'main'
		return group, name
	return 'unknown', 'main'

class cvpj_project_folderprefixes:
	def __init__(self, convproj_obj):
		self.convproj_obj = convproj_obj
		self.data = {}

	def __getitem__(self, k):
		return self.data.__getitem__(k)

	def __contains__(self, k):
		return self.data.__contains__(k)

	def add(self, groupname, in_path):
		t_fileref = fileref.cvpj_fileref(self.convproj_obj)
		t_fileref.set_folder(in_path)

		group, name = fprefix_split(groupname)
		if group not in self.data: self.data[group] = {}
		self.data[group][name] = t_fileref

		return t_fileref

	def get(self, groupname):
		group, name = fprefix_split(groupname)
		if group in self.data:
			if name in self.data[group]:
				return self.data[group][name]

	def extend(self, in_groupname, out_groupname, pathadd):
		filer = self.get(in_groupname)
		if filer is not None:
			filec = filer.copy()
			filec.folder.path.loc += pathadd
			group, name = fprefix_split(out_groupname)
			if group not in self.data: self.data[group] = {}
			self.data[group][name] = filec

# ------------------- plugins -------------------

def vis_plugin(p_category, p_type, p_subtype):
	if p_category != None and p_type != None and p_subtype != None: return p_category+':'+p_type+':'+p_subtype
	elif p_category != None and p_type != None and p_subtype == None: return p_category+':'+p_type
	elif p_category != None and p_type == None and p_subtype == None: return p_category
	elif p_category == None and p_type == None and p_subtype == None: return 'None'

plugin_id_counter = idcounter.counter(1000, 'plugin_')

class cvpj_project_plugins:
	def __init__(self, convproj_obj):
		self.convproj_obj = convproj_obj
		self.data = {}
		self.last_id = None
		self.last_obj = None

	def get_lastid(self): return self.last_id

	def __getitem__(self, k):
		return self.data.__getitem__(k)

	def __contains__(self, k):
		return self.data.__contains__(k)

	def get(self, plug_id):
		if plug_id in self.data: return True, self.data[plug_id]
		else: return False, None

	def add(self, i_category, i_type, i_subtype, plug_id=None):
		if not plug_id: plug_id = plugin_id_counter.get_str_txt()
		logger_project.info('Plugin - '+str(plug_id)+' - '+vis_plugin(i_category, i_type, i_subtype))
		plugin_obj = plugin.cvpj_plugin()
		plugin_obj.replace(i_category, i_type, i_subtype)
		self.last_id = plug_id
		self.last_obj = plugin_obj
		self.data[plug_id] = plugin_obj
		return self.data[plug_id]

	def add_uni(self, i_category, i_plugname, plug_id=None):
		return self.add('universal', i_category, i_plugname, plug_id)

	def add_simple(self, i_category, i_plugname, plug_id=None):
		return self.add('simple', i_category, i_plugname, plug_id)

	def add_native(self, i_daw, i_plugname, plug_id=None):
		return self.add('native', i_daw, i_plugname, plug_id)

	def add_external(self, i_plugtype, i_platform, plug_id=None):
		return self.add('external', i_plugtype, i_platform, plug_id)

	def addspec_sampler(self, file_path, os_type, plug_id=None, **kwargs):
		convproj_obj = self.convproj_obj
		cvpj_samplerefs = convproj_obj.samplerefs
		if file_path:
			sampleref = kwargs['sampleid'] if 'sampleid' in kwargs else file_path
			prefix = kwargs['prefix'] if 'prefix' in kwargs else None
			if not prefix:
				sampleref_obj = cvpj_samplerefs.add(sampleref, file_path, os_type)
			else:
				sampleref_obj = cvpj_samplerefs.add__prefix(sampleref, kwargs['prefix'], file_path)
				sampleref_obj.fileref.resolve_prefix()
			is_drumsynth = sampleref_obj.fileref.get_fileext() == 'ds'
		else:
			sampleref_obj = None
			is_drumsynth = False

		if not is_drumsynth:
			plugin_obj = self.add('universal', 'sampler', 'single', plug_id)
			samplepart_obj = plugin_obj.samplepart_add('sample')
			if file_path: samplepart_obj.from_sampleref(self.convproj_obj, sampleref)
		else:
			plugin_obj = self.add('universal', 'sampler', 'drumsynth', plug_id)
			samplepart_obj = plugin_obj.samplepart_add('sample')
			if file_path:
				samplepart_obj.sampleref = sampleref
				from objects.inst_params import drumsynth
				drumsynth_obj = drumsynth.drumsynth_main()
				drumsynth_obj.load_from_file(file_path)
				drumsynth_obj.to_plugin(plugin_obj)
		plugin_obj.role = 'synth'
		return plugin_obj, sampleref_obj, samplepart_obj

	def addspec_sampler__sampleref(self, sampleref_id, plug_id=None, **kwargs):
		plugin_obj = self.add('universal', 'sampler', 'single', plug_id)
		plugin_obj.role = 'synth'
		samplepart_obj = plugin_obj.samplepart_add('sample')
		samplepart_obj.from_sampleref(self.convproj_obj, sampleref)
		return plugin_obj, samplepart_obj

	def addspec_midi(self, plug_id=None):
		plugin_obj = self.add('universal', 'midi', None, plug_id)
		plugin_obj.role = 'synth'
		return plugin_obj

	def addspec_midi__prop(self, indict, plug_id=None):
		plugin_obj = self.addspec_midi(plug_id)
		plugin_obj.midi.from_dict(indict)
		return plugin_obj

	def addspec_midi__datapack(self, ds_id, ds_cat, ds_obj, plug_id=None):
		dso_obj = globalstore.datapack.get_obj(ds_id, ds_cat, ds_obj)
		dso_midi = dso_obj.midi if dso_obj else None

		if dso_midi:
			plugin_obj = self.addspec_midi(plug_id)
			midi_obj = plugin_obj.midi
			midi_obj.bank = dso_midi.bank
			midi_obj.patch = dso_midi.patch
			midi_obj.drum = dso_midi.is_drum
			return plugin_obj

# ------------------- tracks -------------------

class cvpj_project_tracks:
	__slots__ = ['data','order','convproj_obj']
	
	def __init__(self, convproj_obj):
		self.data = {}
		self.order = []
		self.convproj_obj = convproj_obj

	def __getitem__(self, k):
		return self.data.__getitem__(k)

	def __contains__(self, k):
		return self.data.__contains__(k)

	def change_timings(self, time_ppq):
		for p in self.data: 
			track_data = self.data[p]
			track_data.change_timings(time_ppq)
			for e in track_data.notelist_index: 
				track_data.notelist_index[e].notelist.change_timings(time_ppq)

	def clear(self):
		self.data = {}
		self.order = []

	def remove(self, trackid):
		if trackid in self.data: del self.data[trackid]
		if trackid in self.order: self.order.remove(trackid)

	def get(self, trackid):
		return self.data[trackid] if trackid in self.data else None

	def iter(self):
		for trackid in self.order:
			if trackid in self.data: yield trackid, self.data[trackid]

	def iter_num(self):
		num = 0
		for trackid in self.order:
			if trackid in self.data: 
				yield num, trackid, self.data[trackid]
				num += 1

	def add_scene(self, i_track, i_sceneid, i_lane):
		if i_track in self.data: return self.data[i_track].scene__add(i_sceneid, i_lane)
		else: return None

	def add(self, track_id, tracktype, uses_placements, is_indexed):
		logger_project.info('Track '+('NoPl' if not uses_placements else 'w/Pl')+(' + Indexed' if is_indexed else '')+' - '+track_id)
		self.data[track_id] = tracks.cvpj_track(tracktype, self.convproj_obj.time_ppq, uses_placements, is_indexed)
		self.order.append(track_id)
		return self.data[track_id]

	def count(self):
		return len(self.order)

	def addspec__midi(self, track_id, uses_placements, is_indexed, indict):
		plugin_obj = self.convproj_obj.plugins.addspec_midi__prop(indict, track_id)
		plugin_obj.role = 'synth'

		track_obj = self.add(track_id, 'instrument', uses_placements, is_indexed)
		track_obj.plugslots.set_synth(track_id)
		track_obj.params.add('usemasterpitch', not m_drum, 'bool')
		return track_obj, plugin_obj

	def sort(self):
		sortpos = {}
		for track_id, track_data in self.data.items():
			trackstart = track_data.placements.get_start()
			if trackstart not in sortpos: sortpos[trackstart] = []
			sortpos[trackstart].append([track_id])
		self.order = []
		for n in sorted(sortpos):
			for i in sortpos[n]: self.order += i

	def do_lanefit(self):
		for trackid, track_obj in self.data.items():
			oldnum = len(track_obj.lanes)
			track_obj.lanefit()
			logger_project.info('LaneFit: '+ trackid+': '+str(oldnum)+' > '+str(len(track_obj.lanes)))

	def get_midi_max_ppq(self):
		max_ppq = 0
		for trackid, track_obj in self.data.items():
			max_ppq = max(max_ppq, track_obj.placements.get_midi_max_ppq())
		return max_ppq

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


# ------------------- fileref -------------------

fileref_id_counter = idcounter.counter(1000, 'fileref_')

class cvpj_project_filerefs:
	def __init__(self, convproj_obj):
		self.convproj_obj = convproj_obj
		self.data = {}
		self.last_id = None
		self.last_obj = None

	def __getitem__(self, k):
		return self.data.__getitem__(k)

	def __contains__(self, k):
		return self.data.__contains__(k)

	def get_lastid(self): return self.last_id

	def add(self, fileid, filepath, os_type=None):
		if not fileid: fileid = fileref_id_counter.get_str_txt()
		if fileid not in self.data: 
			ref_obj = fileref.cvpj_fileref(self.convproj_obj)
			ref_obj.set_file(filepath, os_type)
			logger_project.info('FileRef - '+fileid+' - '+filepath)
			self.data[fileid] = ref_obj
			self.last_obj = ref_obj
		self.last_id = fileid
		return self.data[fileid]

	def iter(self):
		for fileid_id, fileid_obj in self.data.items():
			yield fileid_id, fileid_obj

# ------------------- fileref -------------------

class cvpj_project_samplerefs:
	def __init__(self, convproj_obj):
		self.convproj_obj = convproj_obj
		self.data = {}
		self.last_id = None
		self.last_obj = None

	def __getitem__(self, k):
		return self.data.__getitem__(k)

	def __contains__(self, k):
		return self.data.__contains__(k)

	def add(self, fileid, filepath, os_type=None):
		if not fileid: fileid = zlib.crc32(filepath) if filepath else 'null'
		if fileid not in self.data: 
			ref_obj = sampleref.cvpj_sampleref(self.convproj_obj)
			ref_obj.set_path(os_type, filepath)
			logger_project.info('SampleRef - '+fileid+' - '+filepath)
			self.data[fileid] = ref_obj
			self.last_obj = ref_obj
		self.last_id = fileid
		return self.data[fileid]

	def iter(self):
		for sampleref_id, sampleref_obj in self.data.items():
			yield sampleref_id, sampleref_obj

	def get(self, fileid):
		if fileid in self.data: return True, self.data[fileid]
		else: return False, None

	def remove_nonaudiopl(self):

		sflist = list(self.data)
		for trackid, track_obj in self.convproj_obj.tracks.iter():
			for audiopl_obj in track_obj.placements.pl_audio:
				if audiopl_obj.sample.sampleref in sflist: sflist.remove(audiopl_obj.sample.sampleref)

			for nestedpl_obj in track_obj.placements.pl_audio_nested:
				for audiopl_obj in nestedpl_obj.events:
					if audiopl_obj.sample.sampleref in sflist: sflist.remove(audiopl_obj.sample.sampleref)

			for laneid, lane_obj in track_obj.lanes.items():
				for audiopl_obj in lane_obj.placements.pl_audio:
					if audiopl_obj.sample.sampleref in sflist: sflist.remove(audiopl_obj.sample.sampleref)
					
		for s in sflist: del self.data[s]
