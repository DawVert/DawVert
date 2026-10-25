# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects import globalstore
import plugins

FX_NAMES = ['delay','chorus','reverb','distortion','low_boost','compressor','high_pass']

vals_keyoffset = {
	363: 60,
	364: 48,
	365: 24,
}

def add_master_fx(convproj_obj, fx_type, fx_value):
	fx_id = 'master-effect'
	cvpj_plugins = convproj_obj.plugins

	if fx_type == 0: #delay
		from objects.inst_params import fx_delay
		delay_obj = fx_delay.fx_delay()
		delay_obj.feedback_first = True
		delay_obj.feedback[0] = 0.1
		timing_obj = delay_obj.timing_add(0)
		timing_obj.set_seconds(((300*fx_value)/100)/1000)
		plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, fx_id)
		plugin_obj.fxdata_add(1, 0.5)

	elif fx_type == 1: #chorus
		plugin_obj = cvpj_plugins.add_simple('chorus', None, fx_id)
		plugin_obj.params.add('amount', fx_value/100, 'float')

	elif fx_type == 2: #reverb
		plugin_obj = cvpj_plugins.add_simple('reverb', None, fx_id)
		plugin_obj.fxdata_add(1, (0.3)*(fx_value/100))

	elif fx_type == 3: #distortion
		plugin_obj = cvpj_plugins.add_simple('distortion', None, fx_id)
		plugin_obj.params.add('amount', fx_value/100, 'float')

	elif fx_type == 4: #low_boost
		plugin_obj = cvpj_plugins.add_simple('bassboost', None, fx_id)
		plugin_obj.fxdata_add(1, fx_value/100)

	elif fx_type == 5: #compressor
		plugin_obj = cvpj_plugins.add_uni('compressor', None, fx_id)
		params_obj = plugin_obj.params
		params_obj.add('attack', 0.1, 'float')
		params_obj.add('pregain', 0, 'float')
		params_obj.add('knee', 6, 'float')
		params_obj.add('postgain', 0, 'float')
		params_obj.add('ratio', 4, 'float')
		params_obj.add('release', 0.5, 'float')
		params_obj.add('threshold', -20, 'float')

	elif fx_type == 6: #high_pass
		plugin_obj = cvpj_plugins.add_uni('filter', None, fx_id)
		filter_obj = plugin_obj.filter
		filter_obj.on = True
		filter_obj.type.set('high_pass', None)
		filter_obj.freq = xtramath.midi_filter(fx_value/100)
		
	plugin_obj.role = 'fx'

	plugin_obj.visual.from_datapack('boscaceoil', 'fx', FX_NAMES[fx_type], True)
	convproj_obj.track_master.plugslots.slots_audio.append('master-effect')

def add_filter(cvpj_plugins, instnum, cutoff, resonance):
	cvpj_instid = 'ceol_'+str(instnum).zfill(2)
	fx_id = cvpj_instid+'_filter'
	plugin_obj = cvpj_plugins.add_uni('filter', None, fx_id)
	plugin_obj.role = 'fx'

	filter_obj = plugin_obj.filter
	filter_obj.on = True
	filter_obj.type.set('low_pass', None)
	filter_obj.freq = xtramath.midi_filter(cutoff/100)
	filter_obj.q = resonance+1
	
	return fx_id

class input_ceol(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'ceol'
	
	def get_name(self):
		return 'Bosca Ceoil'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['simple:chorus','simple:reverb','simple:distortion','simple:bassboost','universal:compressor','universal:filter','chip:fm:opm','universal:filter','universal:midi']
		in_dict['projtype'] = 'mi'

	def get_configdef(self, configdef):
		configdef.add_bool('no_swing', False, 'Disable Swing')

	def parse(self, conversion_state, dawvert_intent):
		from objects.file_proj_uncommon import boscaceoil as proj_boscaceoil
		project_obj = proj_boscaceoil.ceol_song()
		if dawvert_intent.input_mode == 'file':
			project_obj.load_from_file(dawvert_intent.input_file)
			conversion_state.project = project_obj
			return True

	def to_convproj(self, convproj_obj, dawvert_intent, conversion_state):
		project_obj = conversion_state.project
		from objects.inst_params import fm_opm
		from objects import colors
		global ceol_data
		
		globalstore.datapack.load('boscaceoil', './data/datapack/app/boscaceoil.xml')
		color_track = colors.colorset.from_datapack('boscaceoil', 'track', 'main')
		color_main = colors.colorset.from_datapack('boscaceoil', 'main', 'main')

		# ---------- convproj objects ----------
		cvpj_insts = convproj_obj.instruments
		cvpj_automation = convproj_obj.automation
		cvpj_transport = convproj_obj.transport
		cvpj_master = convproj_obj.track_master
		cvpj_plugins = convproj_obj.plugins
		
		# ---------- convproj params ----------
		no_swing = dawvert_intent.input_get_param('no_swing', False)

		# ---------- convproj init ----------
		convproj_obj.type = 'mi'
		convproj_obj.set_timings(4)
		convproj_obj.do_actions.append('do_addloop')

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['pl_points']

		# ---------- transport ----------
		convproj_obj.add_timesig_lengthbeat(project_obj.pattern_length, project_obj.bar_length)
		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
		cvpj_transport.loop_active = True
		cvpj_transport.loop_start = project_obj.pattern_length*project_obj.loopstart
		cvpj_transport.loop_end = project_obj.pattern_length*project_obj.loopend

		# ---------- fx master ----------
		cvpj_master.params.add('vol', 1, 'float')
		cvpj_master.visual.from_datapack('boscaceoil', 'main', 'masterfx', False)

		add_master_fx(convproj_obj, project_obj.effect_type, project_obj.effect_value)

		# ---------- insts ----------
		t_key_offset = []
		inst_filters = {}
		inst_objs = {}

		for instnum, ceol_inst_obj in enumerate(project_obj.instruments):
			cvpj_instid = 'ceol_'+str(instnum).zfill(2)
			inst_obj = cvpj_insts.add(cvpj_instid)
			inst_obj.params.add('vol', ceol_inst_obj.volume/256, 'float')

			voinst = ceol_inst_obj.inst

			# visual
			visual_obj = inst_obj.visual
			visual_obj.color.set_int(color_main.getcolornum(ceol_inst_obj.palette))
			visual_obj.color.fx_allowed = ['saturate', 'brighter']

			# instrument
			if voinst <= 127:
				inst_obj.midi.out_inst.patch = voinst
				inst_obj.to_midi(convproj_obj, cvpj_instid, True)
			elif voinst == 365: 
				visual_obj.name = 'MIDI Drums'
				inst_obj.midi.out_inst.drum = True
				inst_obj.to_midi(convproj_obj, cvpj_instid, True)
			else: 
				strinst = str(voinst)
				inst_obj.from_datapack("boscaceoil", 'inst', strinst, False)
				inst_ds_obj = globalstore.datapack.get_obj('boscaceoil', 'inst', strinst)
				if inst_ds_obj:
					if 'valsoundid' in inst_ds_obj.data: 
						valsoundid = inst_ds_obj.data['valsoundid']
						opm_obj = fm_opm.opm_inst()
						opm_obj.from_valsound(valsoundid)
						plugin_obj = opm_obj.to_cvpj(convproj_obj)
						inst_obj.plugslots.set_synth(cvpj_plugins.get_lastid())

			# key offset
			inst_objs[voinst] = inst_obj
			if voinst in vals_keyoffset: t_key_offset.append(vals_keyoffset[voinst])
			else: t_key_offset.append(0)

			# cutoff
			if ceol_inst_obj.cutoff < 110:
				inst_filters[instnum] = add_filter(cvpj_plugins, instnum, ceol_inst_obj.cutoff, ceol_inst_obj.resonance)
				inst_obj.plugslots.slots_audio.append(inst_filters[instnum])

		# ---------- patterns ----------
		for patnum, ceol_pat_obj in enumerate(project_obj.patterns):
			cvpj_pat_id = 'ceol_'+str(patnum).zfill(3)

			patinstid = 'ceol_'+str(ceol_pat_obj.inst).zfill(2)

			notevols = {}
			if ceol_pat_obj.recordfilter is not None:
				for n, x in enumerate(ceol_pat_obj.recordfilter[:,0]):
					notevols[n] = x/256

			cvpj_patcolor = color_main.getcolornum(ceol_pat_obj.palette)

			nle_obj = convproj_obj.notelistindex__add(cvpj_pat_id)

			# visual
			visual_obj = nle_obj.visual
			visual_obj.name = str(patnum+1)
			visual_obj.color.set_int(cvpj_patcolor)
			visual_obj.color.fx_allowed = ['saturate', 'brighter']

			# notelist
			cvpj_notelist = nle_obj.notelist
			for ceol_note_obj in ceol_pat_obj.notes: 
				oswing = 0
				if (not ceol_note_obj.pos%2) and (not no_swing): oswing = project_obj.swing/10
				notevol = notevols[ceol_note_obj.pos] if ceol_note_obj.pos in notevols else 1
				notekey = (ceol_note_obj.key-60)+t_key_offset[ceol_pat_obj.inst]
				cvpj_notelist.add_m(patinstid, ceol_note_obj.pos+oswing, ceol_note_obj.len, notekey, notevol, None)

			# scale
			if ceol_pat_obj.scale:
				scale_name, scale_keys = proj_boscaceoil.scale_data[ceol_pat_obj.scale-1]
				out_keys = []
				c = 0
				for x in scale_keys:
					out_keys.append(c)
					c += x
				visual_roll = nle_obj.visual_roll
				visual_roll.scale_root = ceol_pat_obj.key
				visual_roll.scale_keys = out_keys
				visual_roll.scale_name = scale_name
				visual_roll.scale_hide = True

		# ---------- playlist color ----------
		for num in range(8):
			playlist_obj = convproj_obj.playlist__add(num, 1, True)
			if color_track: 
				playlist_obj.visual.color.set_int(color_track.getcolornum(num))
				playlist_obj.visual.color.fx_allowed = ['saturate', 'brighter']

		# ---------- placements ----------
		prev_pl = None
		for plpos, row_data in enumerate(project_obj.spots):
			after_filter = [[-1, -1] for x in range(8)]
			for plnum, plpatnum in enumerate(row_data):

				if plpatnum != -1:
					cvpj_placement = convproj_obj.playlist[plnum].placements.add_notes_indexed()
					cvpj_placement.fromindex = 'ceol_'+str(plpatnum).zfill(3)
					time_obj = cvpj_placement.time
					time_obj.set_block_posdur(plpos, project_obj.pattern_length)

					# recordfilter
					ceol_pat_obj = project_obj.patterns[plpatnum]
					recordfilter = ceol_pat_obj.recordfilter
					if recordfilter is not None:
						after_filter[plnum][0] = plpos
						after_filter[plnum][1] = ceol_pat_obj.inst
						if ceol_pat_obj.inst not in inst_filters: 
							inst_filters[ceol_pat_obj.inst] = add_filter(cvpj_plugins, ceol_pat_obj.inst, ceol_inst_obj.cutoff, ceol_inst_obj.resonance)
							inst_objs[ceol_pat_obj.inst].plugslots.slots_audio.append(inst_filters[ceol_pat_obj.inst])

						patinstid = 'ceol_'+str(ceol_pat_obj.inst).zfill(2)

						autofilterfxid = patinstid+'_filter'
						recordfilter_freq = [xtramath.midi_filter(x/100) for x in recordfilter[:,1]]

						f_autopl_obj = cvpj_automation.add_pl_points(['filter', autofilterfxid, 'freq'], 'float')
						f_autopl_obj.time.set_block_posdur(plpos, project_obj.pattern_length)
						autopoints_obj = f_autopl_obj.data
						for n, x in enumerate(recordfilter_freq):
							autopoints_obj.points__add_normal(n, x, 0, None)

						recordfilter_reso = [x+1 for x in recordfilter[:,2]]
						q_autopl_obj = cvpj_automation.add_pl_points(['filter', autofilterfxid, 'q'], 'float')
						q_autopl_obj.time.set_block_posdur(plpos, project_obj.pattern_length)
						autopoints_obj = q_autopl_obj.data
						for n, x in enumerate(recordfilter_reso):
							autopoints_obj.points__add_normal(n, x, 0, None)

			if prev_pl != None:
				for n in range(8):
					if prev_pl[n][0] != -1 and after_filter[n][0] == -1:
						instnum = prev_pl[n][1]
						patinstid = 'ceol_'+str(instnum).zfill(2)
						autofilterfxid = patinstid+'_filter'

						ceol_inst_obj = project_obj.instruments[instnum]

						f_autopl_obj = cvpj_automation.get_opt(['filter', autofilterfxid, 'freq'])
						f_autopl_obj.defualt_val = xtramath.midi_filter(ceol_inst_obj.cutoff)

						q_autopl_obj = cvpj_automation.get_opt(['filter', autofilterfxid, 'q'])
						q_autopl_obj.defualt_val = ceol_inst_obj.resonance+1

			prev_pl = after_filter

		# ---------- automation ----------
		cvpj_automation.set_persist_all(False)