# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math
import base64
from functions import data_bytes
from functions import data_values
from external.easybinrw import easybinrw
from objects.dawspecific import flp_plugins
from objects.dawspecific import flp_plugins_directwave

import logging
logger_output = logging.getLogger('output')

def wrapper_addchunk(wrapper_data, chunkid, chunkdata):
	wrapper_data.uint32(chunkid)
	wrapper_data.uint32(len(chunkdata))
	wrapper_data.uint32(0)
	wrapper_data.raw(chunkdata)

def wrapper_addchunk_plugtype(wrapper_data, chunkid, plugtype, chunkdata):
	wrapper_data.uint32(chunkid)
	wrapper_data.uint32(len(chunkdata)+4)
	wrapper_data.uint32(0)
	wrapper_data.uint32(plugtype)
	wrapper_data.raw(chunkdata)

	#print('O< ', chunkid, chunkdata[0:100])

def setparams(convproj_obj, plugin_obj):
	fl_plugin = None
	fl_pluginparams = None
	plug_type = plugin_obj.type_get()

	ebrw_writestr = easybinrw.binwrite()

	if plugin_obj.check_wildmatch('universal', 'sampler', 'single'):
		sp_obj = plugin_obj.samplepart_get('sample')
		sampleref_found, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
		if sp_obj.loop_active and sampleref_found:
			sp_obj.convpoints_samples(sampleref_obj)

			fl_plugin = 'directwave'
			fpc_plugin = flp_plugins_directwave.directwave_plugin()
			firstprogram = fpc_plugin.programs[0]
			firstprogram.name = 'DawVert Converted'.encode()
			firstprogram.main.used = 1
			dw_region = firstprogram.add_region()
			dw_reg_main = dw_region.main
			dw_reg_main.key_min = 0
			dw_reg_main.key_max = 127
			dw_reg_main.key_root = 60
			dw_reg_main.unk_4 = 2

			dw_reg_sample = dw_region.sample
			dw_reg_sample.bits = 128
			dw_reg_sample.channels = sampleref_obj.channels
			dw_reg_sample.hz = sampleref_obj.hz
			dw_reg_sample.loop_end = sp_obj.loop_end
			dw_reg_sample.loop_start = sp_obj.loop_start
			if sp_obj.loop_active:
				dw_reg_sample.loop_type = 2
			else:
				dw_reg_sample.loop_type = 0 if sp_obj.trigger != 'oneshot' else 1

			dw_reg_sample.num_samples = sampleref_obj.dur_samples
			dw_reg_sample.start = sp_obj.start

			filepath = sp_obj.get_filepath(convproj_obj, False)
			filepath = filepath.replace('/', '\\')
			dw_region.path = filepath.encode()

			fl_pluginparams = fpc_plugin.dump()

	if plugin_obj.check_wildmatch('universal', 'sampler', 'multi'):
		fl_plugin = 'directwave'
		fpc_plugin = flp_plugins_directwave.directwave_plugin()

		firstprogram = fpc_plugin.programs[0]
		firstprogram.name = 'DawVert Converted'.encode()

		for sampleregion in plugin_obj.sampleregion_getall():
			key_l, key_h, key_r, samplerefid, extradata = sampleregion

			dw_region = firstprogram.add_region()

			sp_obj = plugin_obj.samplepart_get(samplerefid)
			sampleref_found, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
			if sampleref_found: 
				firstprogram.main.used += 1
				sp_obj.convpoints_samples(sampleref_obj)

				dw_reg_pitch = dw_region.pitch
	
				dw_reg_main = dw_region.main
				dw_reg_main.key_min = int(key_l+60)
				dw_reg_main.key_max = int(key_h+60)
				dw_reg_main.key_root = int(key_r+60)
				dw_reg_main.vel_min = int(sp_obj.vel_min*127)
				dw_reg_main.vel_max = int(sp_obj.vel_max*127)
				dw_reg_main.unk_4 = 2
	
				dw_reg_main.gain = sp_obj.vol
				dw_reg_main.pan = (sp_obj.pan/2)+0.5
				dw_reg_main.tune = (sp_obj.pitch/24)+0.5
	
				dw_reg_pitch.k_trk = int(sp_obj.scale*100) if not sp_obj.no_pitch else 0
	
				dw_reg_sample = dw_region.sample
				dw_reg_sample.bits = 128
				dw_reg_sample.channels = sampleref_obj.channels
				dw_reg_sample.hz = sampleref_obj.hz
				dw_reg_sample.loop_end = sp_obj.loop_end
				dw_reg_sample.loop_start = sp_obj.loop_start
				if sp_obj.loop_active:
					dw_reg_sample.loop_type = 2
				else:
					dw_reg_sample.loop_type = 0 if sp_obj.trigger != 'oneshot' else 1
	
				dw_reg_sample.num_samples = sampleref_obj.dur_samples
				dw_reg_sample.start = sp_obj.start
	
				if sp_obj.visual.name:
					dw_region.name = sp_obj.visual.name.encode()
				if not dw_region.name:
					if sampleref_obj.fileref.file.filename:
						dw_region.name = sampleref_obj.fileref.file.filename.encode()
	
				filepath = sp_obj.get_filepath(convproj_obj, False)
				filepath = filepath.replace('/', '\\')
				dw_region.path = filepath.encode()

		fl_pluginparams = fpc_plugin.dump()

	if plugin_obj.check_wildmatch('universal', 'sampler', 'drums'):
		fl_plugin = 'fpc'
		fpc_plugin = flp_plugins.fpc_plugin()

		drumpads = plugin_obj.drumpad_getall()
		drumpads = drumpads[0:32]

		for num, drumpad_obj in enumerate(drumpads):
			fpc_pad = fpc_plugin.pads[num]
			fpc_pad.key = drumpad_obj.key+60
			fpc_pad.vol = min(127, int(drumpad_obj.vol*127))
			fpc_pad.pan = int(drumpad_obj.pan*127)
			fpc_pad.tune = int((drumpad_obj.pitch/12)*128)

			if drumpad_obj.visual.name: fpc_pad.name = drumpad_obj.visual.name.encode()
			drum_color = drumpad_obj.visual.color.get_int()
			if drum_color: fpc_pad.color = int.from_bytes(bytes(drum_color), "little")

			if drumpad_obj.layers: fpc_pad.layers_clear()
			for layer_obj in drumpad_obj.layers:
				fpc_layer = fpc_pad.layer_add()
				fpc_layer.vel_min = int(layer_obj.vel_min*127)
				fpc_layer.vel_max = int(layer_obj.vel_max*127)
				sre_obj = plugin_obj.samplepart_get(layer_obj.samplepartid)
				if sre_obj:
					fpc_layer.vol = int(sre_obj.vol*127)
					fpc_layer.pan = int(sre_obj.pan*127)
					fpc_layer.tune = int((sre_obj.pitch/12)*128)
					ref_found, sampleref_obj = convproj_obj.sampleref__get(sre_obj.sampleref)
					if ref_found:
						filepath = sampleref_obj.fileref.get_path('win', False)
						fpc_layer.filename = filepath.encode()

		fl_pluginparams = fpc_plugin.dump()

	if plugin_obj.check_wildmatch('universal', 'sampler', 'slicer'):
		fl_plugin = 'fruity slicer'

		sre_obj = plugin_obj.samplepart_get('sample')
		ref_found, sampleref_obj = convproj_obj.sampleref__get(sre_obj.sampleref)

		stretch_obj = sre_obj.stretch

		slicer_beats = plugin_obj.datavals.get('beats', 4)
		slicer_bpm = plugin_obj.datavals.get('bpm', 4)
		slicer_pitch = int(sre_obj.pitch*100)
		slicer_fitlen = int(math.log2(1/stretch_obj.timing.get__speed(sampleref_obj))*10000)
		slicer_att = int(plugin_obj.datavals.get('fade_in', 4))
		slicer_dec = int(plugin_obj.datavals.get('fade_out', 4))
		
		stretch_algo = stretch_obj.algorithm

		if stretch_algo.type == 'elastique_pro': 
			if stretch_algo.subtype == 'transient': slicer_stretchtype = 3
			else: slicer_stretchtype = 2
		elif stretch_algo.type == 'elastique_v2': 
			if stretch_algo.subtype == 'tonal': slicer_stretchtype = 5
			elif stretch_algo.subtype == 'mono': slicer_stretchtype = 6
			elif stretch_algo.subtype == 'speech': slicer_stretchtype = 7
			else: slicer_stretchtype = 4
		else:
			slicer_stretchtype = 0

		ebrw_writestr.int_s32(15)
		ebrw_writestr.float(slicer_beats)
		ebrw_writestr.float(slicer_bpm)
		ebrw_writestr.int_s32(slicer_pitch)
		ebrw_writestr.int_s32(slicer_fitlen)
		ebrw_writestr.int_s32(slicer_stretchtype)
		ebrw_writestr.int_s32(slicer_att)
		ebrw_writestr.int_s32(slicer_dec)
		ebrw_writestr.string_i8(sre_obj.get_filepath(convproj_obj, 'win'))

		ebrw_writestr.int_u32(len(sre_obj.slicer_slices))
		for slice_obj in sre_obj.slicer_slices:
			ebrw_writestr.string_i8(slice_obj.name)
			ebrw_writestr.int_u32(int(slice_obj.start))
			ebrw_writestr.int_s32(slice_obj.custom_key+60 if slice_obj.is_custom_key else -1)
			ebrw_writestr.int_u16(0)
			ebrw_writestr.int_u8(128)
			ebrw_writestr.int_u8(191)
			ebrw_writestr.int_u8(slice_obj.reverse)

		slicer_animate = plugin_obj.viscustom_get('animate', False)
		slicer_starting_key = sre_obj.slicer_start_key+60
		slicer_play_to_end = plugin_obj.datavals.get('play_to_end', 0)
		slicer_bitrate = 44100
		slicer_auto_dump = plugin_obj.datavals.get('auto_dump', 0)
		slicer_declick = plugin_obj.datavals.get('declick', 0)
		slicer_auto_fit = plugin_obj.datavals.get('auto_fit', 0)
		slicer_view_spectrum = plugin_obj.viscustom_get('spectrum', False)

		ebrw_writestr.int_u8(slicer_animate)
		ebrw_writestr.int_u32(slicer_starting_key)
		ebrw_writestr.int_u8(slicer_play_to_end)
		ebrw_writestr.int_u32(slicer_bitrate)
		ebrw_writestr.int_u8(slicer_auto_dump)
		ebrw_writestr.int_u8(slicer_declick)
		ebrw_writestr.int_u8(slicer_auto_fit)
		ebrw_writestr.int_u32(slicer_view_spectrum)

		fl_pluginparams = ebrw_writestr.getvalue()

	if plugin_obj.check_wildmatch('native', 'flstudio', 'fruity html notebook'):
		fl_plugin = 'fruity html notebook'
		ebrw_writestr.int_u32(1)
		ebrw_writestr.string_i8(plugin_obj.datavals.get('url', ''))
		fl_pluginparams = ebrw_writestr.getvalue()

	if plugin_obj.check_wildmatch('native', 'flstudio', 'fruity notebook'):
		fl_plugin = 'fruity notebook'
		ebrw_writestr.int_u32(1000)
		ebrw_writestr.int_u32(plugin_obj.datavals.get('currentpage', 0))
		pagedata = plugin_obj.datavals.get('pages', {})
		for pagenum, pagebin in pagedata.items():
			ebrw_writestr.int_s32(pagenum)
			ebrw_writestr.string_i32(pagebin)
		ebrw_writestr.int_s32(-1)
		ebrw_writestr.int_s8(plugin_obj.datavals.get('editing_enabled', 0))
		fl_pluginparams = ebrw_writestr.getvalue()

	if plugin_obj.check_wildmatch('native', 'flstudio', 'fruity notebook 2'):
		fl_plugin = 'fruity notebook 2'
		ebrw_writestr.int_u32(0)
		ebrw_writestr.int_u32(plugin_obj.datavals.get('currentpage', 0))
		pagedata = plugin_obj.datavals.get('pages', {})
		for pagenum, pagebin in pagedata.items():
			ebrw_writestr.int_s32(pagenum)
			ebrw_writestr.varint(len(pagebin*2))
			ebrw_writestr.string_varint(pagebin, encoding='utf-16le')
		ebrw_writestr.int_s32(-1)
		ebrw_writestr.int_s8(plugin_obj.datavals.get('editing_enabled', 0))
		fl_pluginparams = ebrw_writestr.getvalue()

	if plugin_obj.check_wildmatch('native', 'flstudio', 'fruity vocoder'):
		fl_plugin = 'fruity vocoder'
		p_bands = plugin_obj.array_get('bands', 4)
		p_filter = plugin_obj.datavals.get('filter', 2)
		p_left_right = plugin_obj.datavals.get('left_right', 0)

		p_freq_min = plugin_obj.params.get('freq_min', 0).value
		p_freq_max = plugin_obj.params.get('freq_max', 65536).value
		p_freq_scale = plugin_obj.params.get('freq_scale', 64).value
		p_freq_invert = int(plugin_obj.params.get('freq_invert', 0).value)
		p_freq_formant = plugin_obj.params.get('freq_formant', 0).value
		p_freq_bandwidth = plugin_obj.params.get('freq_bandwidth', 50).value
		p_env_att = plugin_obj.params.get('env_att', 1000).value
		p_env_rel = plugin_obj.params.get('env_rel', 100).value
		p_mix_mod = plugin_obj.params.get('mix_mod', 0).value
		p_mix_car = plugin_obj.params.get('mix_car', 0).value
		p_mix_wet = plugin_obj.params.get('mix_wet', 128).value

		ebrw_writestr.int_u32(2)
		ebrw_writestr.int_u32(len(p_bands))
		ebrw_writestr.int_u32(p_filter)
		ebrw_writestr.int_u32(2)
		ebrw_writestr.int_u8(p_left_right)

		ebrw_writestr.list_float(p_bands, len(p_bands))
		
		ebrw_writestr.int_u32(p_freq_min)
		ebrw_writestr.int_u32(p_freq_max)
		ebrw_writestr.int_u32(p_freq_scale)
		ebrw_writestr.int_u32(p_freq_invert)
		ebrw_writestr.int_u32(p_freq_formant)
		ebrw_writestr.int_u32(p_freq_bandwidth)

		ebrw_writestr.int_u32(p_env_att)
		ebrw_writestr.int_u32(p_env_rel)
		ebrw_writestr.int_u32(0)
		ebrw_writestr.int_u32(p_mix_mod)
		ebrw_writestr.int_u32(p_mix_car)
		ebrw_writestr.int_u32(p_mix_wet)

		fl_pluginparams = ebrw_writestr.getvalue()

	if plugin_obj.check_wildmatch('native', 'flstudio', None):
		outbytes = plugin_obj.to_bytes('fl_studio', 'plugin', plug_type[2], 'main')

		if outbytes:
			fl_plugin = plug_type[2]
			fl_pluginparams = outbytes
		else:
			fl_pluginparams = plugin_obj.rawdata_get('fl')

	if plugin_obj.check_wildmatch('universal', 'soundfont2', None):
		fl_plugin = 'fruity soundfont player'

		asdr_vol = plugin_obj.env_asdr_get('vol')
		lfo_pitch = plugin_obj.lfo_get('pitch')

		ref_found, fileref_obj = plugin_obj.fileref__get('file', convproj_obj)
		sf2_file = fileref_obj.get_path('win', False) if ref_found else ''
		sf2_bank, sf2_patch = plugin_obj.midi.to_sf2()

		flsf_lfo_predelay = int(lfo_pitch.predelay*256) if lfo_pitch.predelay != 0 else -1
		flsf_lfo_amount = int(lfo_pitch.amount*128) if lfo_pitch.amount != 0 else -1
		flsf_lfo_speed = int(6/lfo_pitch.time.speed_seconds)

		if asdr_vol.amount == 0: flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = -1, -1, -1, -1
		else: flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = int(asdr_vol.attack/1024), int(asdr_vol.decay/1024), int(asdr_vol.sustain/127), int(asdr_vol.release/1024)

		fl_pluginparams = b''
		fl_pluginparams += struct.pack('iiiiii', *(2, sf2_patch+1, sf2_bank, 128, 128, 0) )
		fl_pluginparams += struct.pack('iiii', *(flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R) )
		fl_pluginparams += struct.pack('iiii', *(flsf_lfo_predelay, flsf_lfo_amount, flsf_lfo_speed, -1) )
		fl_pluginparams += len(sf2_file).to_bytes(1, "little")
		fl_pluginparams += sf2_file.encode('utf-8')
		fl_pluginparams += b'\xff\xff\xff\xff\x00\xff\xff\xff\xff\x00\x00'

	if plugin_obj.check_wildmatch('external', 'vst2', None):
		vst_numparams = plugin_obj.external_info.numparams
		vst_current_program = plugin_obj.current_program
		vst_datatype = plugin_obj.external_info.datatype
		vst_fourid = plugin_obj.external_info.fourid
		vst_name = plugin_obj.external_info.name

		ref_found, fileref_obj = plugin_obj.fileref__get_global('plugin', convproj_obj)
		vst_path = fileref_obj.get_path('win', False) if ref_found else None

		isvalid = True
		if vst_fourid:
			if vst_name or vst_path:
				if vst_datatype in ['chunk', 'param']:
					isvalid = True
				else:
					logger_output.warning('VST2 plugin not placed: unknown datatype:', str(vst_datatype))
			else:
				logger_output.warning('VST2 plugin not placed: name or file path not found.')
		else:
			logger_output.warning('VST2 plugin not placed: no ID '+('for "'+vst_name+'" found.' if vst_name else "found."))

		if isvalid:
			vstdata_bytes = plugin_obj.rawdata_get('chunk')

			wrapper_state = easybinrw.binwrite()

			if vst_datatype == 'chunk':
				if vst_current_program != -1:
					wrapper_state.raw(b'\xf7\xff\xff\xff\r\xfe\xff\xff\xff')
					wrapper_state.int_u32(len(vstdata_bytes))
					wrapper_state.raw(b'\x00\x00\x00\x00')
					wrapper_state.int_u32(vst_current_program)
					wrapper_state.raw(vstdata_bytes)
				else:
					wrapper_state.raw(b'\xf7\xff\xff\xff\x0c\xfe\xff\xff\xff')
					wrapper_state.int_u32(len(vstdata_bytes))
					wrapper_state.raw(b'\x00\x00\x00\x00\x00\x00\x00\x00')
					wrapper_state.raw(vstdata_bytes)

			if vst_datatype == 'param':
				prognums = list(plugin_obj.programs)
				prognum = prognums.index(plugin_obj.current_program) if plugin_obj.current_program in prognums else 0
	
				wrapper_state.raw(b'\xf7\xff\xff\xff\x05\xfe\xff\xff\xff')
				wrapper_state.raw(b'\x00\x00\x00\x00')
				wrapper_state.raw(b'\x00\x00\x00\x00')
				wrapper_state.int_u32(prognum)
	
				vst_total_params = 0
				vst_num_names = len(plugin_obj.programs)
				vst_params_data = easybinrw.binwrite()
				vst_names = easybinrw.binwrite()

				for _, progstate in plugin_obj.programs.items():
					vst_total_params += vst_numparams

					for num in range(vst_numparams):
						paramval = progstate.params.get('ext_param_'+str(num), 0).value
						vst_params_data.float(paramval)
					vst_names.string(progstate.preset.name, 25)
	
				wrapper_state.int_u32(vst_total_params)
				wrapper_state.raw(vst_params_data.getvalue())
				wrapper_state.int_u32(vst_num_names)
				wrapper_state.raw(vst_names.getvalue())
	
			wrapper_plugin = flp_plugins.fruity_wrapper()
			wrapper_plugin.plugin_type = 4 if plugin_obj.role == 'synth' else 0
			wrapper_plugin.plugin_other = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
			if vst_fourid != None: wrapper_plugin.fourid = vst_fourid
			wrapper_plugin.unk_57 = b'`\t\x00\x00'
			if vst_name != None: wrapper_plugin.name = vst_name
			if vst_path != None: wrapper_plugin.file = vst_path
			wrapper_plugin.state = wrapper_state.getvalue()

			fl_plugin = 'fruity wrapper'
			fl_pluginparams = wrapper_plugin.dump()

	#if plug_type[0] == 'vst3':
	#	vst_chunk = plugin_obj.rawdata_get('chunk')
	#	vst_id = plugin_obj.datavals.get('id', None)
	#	vst_name = plugin_obj.datavals.get('name', None)
	#	vst_path = plugin_obj.datavals.get('path', None)
	#	vst_numparams = plugin_obj.datavals.get('numparams', None)

	#	if vst_numparams != None:
	#		wrapper_state = b'\x01\x00\x00\x00\x01\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	#		wrapper_state += wrapper_addchunk(3, vst_chunk)

	#		fourchunkdata = vst_numparams.to_bytes(4, "little")
	#		for paramnum in range(vst_numparams):
	#			fourchunkdata += paramnum.to_bytes(4, "little")

	#		wrapper_state += wrapper_addchunk(4, fourchunkdata)
	#		wrapper_data = b'\n\x00\x00\x00'

	##		print(54, vst_name.encode())
	##		print(55, vst_path.encode())

	#		if vst_name != None: wrapper_data += wrapper_addchunk(54, vst_name.encode() )
	#		if vst_path != None: wrapper_data += wrapper_addchunk(55, vst_path.encode() )

	#		wrapper_data += wrapper_addchunk(53, wrapper_state )
	#		#print(wrapper_state.hex())
	#		fl_plugin = 'fruity wrapper'
	#		fl_pluginparams = wrapper_data

	#print(fl_pluginparams)

	return fl_plugin, fl_pluginparams