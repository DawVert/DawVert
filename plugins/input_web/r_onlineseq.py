# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
import plugins
import struct

def int2float(value): return struct.unpack("<f", struct.pack("<I", value))[0]

def get_autoloc(target, paramid):
	if target == 0:
		if   paramid ==  0: return ('main', 'bpm')
		elif paramid ==  8: return ('master', 'vol')
	else:
		trackid = 'os_'+str(target)
		if   paramid ==  1: return ('track', trackid, 'vol')
		elif paramid ==  2: return ('track', trackid, 'pan')
		elif paramid ==  3: return ('plugin', trackid+'_eq', 'eq_high')
		elif paramid ==  4: return ('plugin', trackid+'_eq', 'eq_mid')
		elif paramid ==  5: return ('plugin', trackid+'_eq', 'eq_low')
		elif paramid ==  6: return ('slot', trackid+'_delay', 'enabled')
		elif paramid ==  7: return ('plugin', trackid+'_reverb', 'reverb_type')
		elif paramid == 11: return ('track', trackid, 'pitch')
		elif paramid == 12: return ('slot', trackid+'_reverb', 'wet')
		elif paramid == 13: return ('plugin', trackid+'_distort', 'distort_type')
		elif paramid == 14: return ('slot', trackid+'_distort', 'wet')
		elif paramid == 26: return ('plugin', trackid+'_bitcrush', 'bits')

synth_filter_type = {
	0: 'low_pass',
	1: 'band_pass',
	2: 'high_pass',
}

class input_onlinesequencer(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'onlineseq'
	
	def get_name(self):
		return 'Online Sequencer'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi','native:onlineseq','universal:synth-osc']
		in_dict['projtype'] = 'r'

	def get_configdef(self, configdef):
		configdef.set_group('grouping', 'Grouping')
		cfgpart = configdef.add_enum('groupby', 'instset', 'Group By')
		cfgpart.add_choice('none', 'None')
		cfgpart.add_choice('inst', 'Instrument')
		cfgpart.add_choice('instset', 'Instrument Category')
		cfgpart = configdef.add_int('groupmin', 3, 'Group if more then')
		cfgpart.set_range(0, 10)

	def parse(self, conversion_state, dawvert_intent):
		from objects.file_proj import onlineseq as proj_onlineseq

		project_obj = proj_onlineseq.onlineseq_project()
		if dawvert_intent.input_mode == 'file':
			project_obj.load_from_file(dawvert_intent.input_file)
			conversion_state.project = project_obj
			return True

	def to_convproj(self, convproj_obj, dawvert_intent, conversion_state):
		project_obj = conversion_state.project
		
		from objects.inst_params import fx_delay

		globalstore.datapack.load('onlineseq', './data/datapack/app/onlineseq.xml')

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks
		cvpj_groups = convproj_obj.groups
		cvpj_automation = convproj_obj.automation
		cvpj_plugins = convproj_obj.plugins

		# ---------- convproj params ----------
		groupby = dawvert_intent.input_get_param('groupby', 'instset')
		groupmin = dawvert_intent.input_get_param('groupmin', 3)

		# ---------- convproj init ----------
		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.type = 'r'
		convproj_obj.set_timings(4.0)
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['nopl_points']
		traits_obj.track_nopl = True

		# ---------- transport ----------
		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
		convproj_obj.timesig = [project_obj.numerator, 4]

		# ---------- tracks ----------
		used_fx = {}
		synthdata = {}
		for instid, instparam in project_obj.params.items(): 
			used_fx[instid] = instparam.used_fx
		for instid, instparam in project_obj.params.items(): 
			synthdata[instid] = instparam.synth
		for target, params in project_obj.seperate_markers().items(): 
			if target != -1:
				if target in used_fx:
					if ((3 in params) or (4 in params) or (5 in params)) and 'eq' not in used_fx[target]: used_fx[instid].append('eq')
					if (6 in params) and 'delay' not in used_fx[target]: used_fx[instid].append('delay')
					if ((7 in params) or (12 in params)) and 'reverb' not in used_fx[target]: used_fx[instid].append('reverb')
					if ((13 in params) or (14 in params)) and 'distort' not in used_fx[target]: used_fx[instid].append('distort')
					if ((18 in params) or (19 in params) or (20 in params)) and 'bitcrush' not in used_fx[target]: used_fx[instid].append('bitcrush')

			for paramid, markers in params.items(): 
				autoloc = get_autoloc(target, paramid)
				div = 1
				if target != 0:
					if paramid == 11: div = 100

				if autoloc:
					auto_obj = cvpj_automation.create(autoloc, 'float', True)
					autopoints = auto_obj.make_nopl_points()
					for marker in markers: 
						pos = marker.pos
						val = marker.value/div
						ptype = 'normal' if marker.type else 'instant'
						autopoints.points__add_point(pos, val, ptype)

		# ---------- notes ----------
		multig = {}
		sep_notes = project_obj.seperate_notes(False)
		for instid, notes in sep_notes.items():
			s_used_fx = used_fx[instid] if instid in used_fx else []

			trackid = 'os_'+str(instid)
			trueinstid = instid%10000

			if trueinstid not in multig: multig[trueinstid] = []
			track_obj = cvpj_tracks.add(trackid, 'instrument', 0, False)
			track_obj.visual.from_datapack('onlineseq', 'inst', str(trueinstid), True)
			
			multig[trueinstid].append(track_obj)

			track_obj.visual_inst = track_obj.visual.copy()

			if trueinstid in [13,14,15,16]: 
				plugin_obj = cvpj_plugins.add_uni('synth-osc', None, trackid)
				plugin_obj.role = 'synth'
				track_obj.plugslots.set_synth(trackid)
				osc_data = plugin_obj.osc_add()
				if instid == 13:
					plugin_obj.midi_fallback__add_inst(11)
					osc_data.prop.shape = 'sine'
				elif instid == 14:
					plugin_obj.midi_fallback__add_inst(80)
					osc_data.prop.shape = 'square'
				elif instid == 15:
					plugin_obj.midi_fallback__add_inst(81)
					osc_data.prop.shape = 'saw'
				elif instid == 16:
					plugin_obj.midi_fallback__add_inst(95)
					osc_data.prop.shape = 'triangle'
			
			elif trueinstid == 55:
				s_synthdata = synthdata[instid]
				plugin_obj = cvpj_plugins.add_uni('synth-osc', None, trackid)
				plugin_obj.role = 'synth'
				track_obj.plugslots.set_synth(trackid)
				osc_data = plugin_obj.osc_add()
				osc_data.prop.shape = ['sine', 'square', 'saw', 'triangle'][s_synthdata.shape]
				plugin_obj.midi_fallback__add_inst([11, 80, 81, 95][s_synthdata.shape])

				if s_synthdata.env_vol:
					env_data = s_synthdata.env_vol
					if env_data.enabled: plugin_obj.env_asdr_add('vol', 0, env_data.attack, 0, env_data.decay, env_data.sustain, env_data.release, 1)

				if s_synthdata.env_filt:
					env_data = s_synthdata.env_filt
					if env_data.enabled: plugin_obj.env_asdr_add('cutoff', 0, env_data.attack, 0, env_data.decay, env_data.sustain, env_data.release, 6000)

				if s_synthdata.lfo_on:
					lfo_obj = plugin_obj.lfo_add(['vol','pitch','cutoff'][s_synthdata.lfo_dest])
					lfo_obj.amount = s_synthdata.lfo_amount if s_synthdata.lfo_dest != 1 else s_synthdata.lfo_amount/100
					if s_synthdata.lfo_freq_custom: lfo_obj.time.set_hz(s_synthdata.lfo_freq)
					else: lfo_obj.time.set_frac(1, int(s_synthdata.lfo_freq), '', convproj_obj)

				filter_obj = plugin_obj.filter
				filter_obj.on = True
				filter_obj.freq = s_synthdata.filter_freq
				filter_obj.q = ((s_synthdata.filter_reso+1)/11)**2.5
				filter_type = s_synthdata.filter_type
				if filter_type in synth_filter_type:
					filter_obj.type.set(synth_filter_type[filter_type], None)

			else:
				plugin_obj = cvpj_plugins.add_native('onlineseq', 'instrument', trackid)
				plugin_obj.datavals.add('instrument', trueinstid)
				plugin_obj.role = 'synth'
				plugin_obj.midi_fallback__add_from_datapack('onlineseq', 'inst', str(trueinstid))
				track_obj.plugslots.set_synth(trackid)

			if instid in project_obj.params:
				i_params = project_obj.params[instid]
				if i_params.name: track_obj.visual.name = i_params.name
				track_obj.params.add('vol', i_params.vol, 'float')
				track_obj.params.add('pan', i_params.pan, 'float')
	
				if 'bitcrush' in s_used_fx:
					pluginid = trackid+'_bitcrush'
					plugin_obj = cvpj_plugins.add_uni('bitcrush', None, pluginid)
					plugin_obj.role = 'fx'
					plugin_obj.params.add('bits', i_params.bitcrush_depth, 'float')
					plugin_obj.visual.from_datapack('onlineseq', 'fx', 'bitcrush', True)
					track_obj.plugslots.slots_audio.append(pluginid)

				if 'delay' in s_used_fx:
					pluginid = trackid+'_delay'
					delay_obj = fx_delay.fx_delay()
					delay_obj.feedback[0] = 0.25
					timing_obj = delay_obj.timing_add(0)
					timing_obj.set_steps(2, convproj_obj)
					plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, pluginid)
					plugin_obj.fxdata_add(bool(i_params.delay_on), 0.5)
					plugin_obj.visual.from_datapack('onlineseq', 'fx', 'delay', True)
					track_obj.plugslots.slots_audio.append(pluginid)
	
				if 'distort' in s_used_fx:
					pluginid = trackid+'_distort'
					plugin_obj = cvpj_plugins.add_native('onlineseq', 'distort', pluginid)
					plugin_obj.role = 'fx'
					plugin_obj.fxdata_add(True, i_params.distort_wet)
					plugin_obj.params.add('distort_type', i_params.distort_type, 'int')
					plugin_obj.visual.from_datapack('onlineseq', 'fx', 'distortion', True)
					track_obj.plugslots.slots_audio.append(pluginid)
	
				if 'reverb' in s_used_fx:
					pluginid = trackid+'_reverb'
					plugin_obj = cvpj_plugins.add_native('onlineseq', 'reverb', pluginid)
					plugin_obj.role = 'fx'
					plugin_obj.fxdata_add(bool(i_params.reverb_on), i_params.reverb_wet)
					plugin_obj.params.add('reverb_type', i_params.reverb_type, 'int')
					plugin_obj.visual.from_datapack('onlineseq', 'fx', 'reverb', True)
					track_obj.plugslots.slots_audio.append(pluginid)
	
				if 'eq' in s_used_fx:
					pluginid = trackid+'_eq'
					plugin_obj = cvpj_plugins.add_native('onlineseq', 'eq', pluginid)
					plugin_obj.role = 'fx'
					plugin_obj.fxdata_add(bool(i_params.enable_eq), 1)
					plugin_obj.params.add('eq_high', i_params.eq_high, 'float')
					plugin_obj.params.add('eq_mid', i_params.eq_mid, 'float')
					plugin_obj.params.add('eq_low', i_params.eq_low, 'float')
					plugin_obj.visual.from_datapack('onlineseq', 'fx', 'eq', True)
					track_obj.plugslots.slots_audio.append(pluginid)

			cvpj_notelist = track_obj.placements.notelist
			cvpj_notelist.clear_size(len(notes))
			for key, pos, dur, inst, vol in notes: 
				cvpj_notelist.add_r(pos, dur, key-60, vol, {})

		# ---------- grouping ----------
		if groupby=='inst':
			for k, v in multig.items():
				if len(v)>groupmin:
					group_obj = cvpj_groups.add(str(k))
					group_obj.visual.from_datapack('onlineseq', 'inst', str(k), True)
					for x in v: x.group = str(k)

		elif groupby=='instset':
			dset_cat_obj = globalstore.datapack.get_cat('onlineseq', 'inst')

			catgrp = {}
			for k, v in multig.items():
				dset_obj = dset_cat_obj.objects.get(str(k))
				if dset_obj is not None:
					if 'group' in dset_obj.data:
						catname = dset_obj.data['group']
						if catname not in catgrp: catgrp[catname] = []
						catgrp[catname] += v

			for k, v in catgrp.items():
				dset_obj = dset_cat_obj.objects.get(str(k))
				if len(v)>groupmin:
					group_obj = cvpj_groups.add(k)
					group_obj.visual.name = k
					group_obj.visual_track.group_expanded = True
					for x in v: x.group = str(k)
