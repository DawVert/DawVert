# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import os

from objects.convproj import fileref

def calc_tick_val(bpmdiv, inpos):
	return (inpos/5512)/bpmdiv

class addauto_data():
	def __init__(self):
		self.autoloc = None
		self.mpetype = None
		self.plpos = None
		self.pldur = None
		self.startval = None
		self.endval = None
		self.envpoints = None
		self.defval = None
		self.iseff = None
		self.bpmdiv = None
		self.auto_method = None
		self.placement_obj = None
		self.ftr_clip = None

def make_auto(convproj_obj, addauto_obj):
	autoloc = addauto_obj.autoloc
	mpetype = addauto_obj.mpetype
	plpos = addauto_obj.plpos
	pldur = addauto_obj.pldur
	startval = addauto_obj.startval
	endval = addauto_obj.endval
	envpoints = addauto_obj.envpoints
	defval = addauto_obj.defval
	iseff = addauto_obj.iseff
	bpmdiv = addauto_obj.bpmdiv
	auto_method = addauto_obj.auto_method
	placement_obj = addauto_obj.placement_obj
	ftr_clip = addauto_obj.ftr_clip

	cvpj_automation = convproj_obj.automation

	if auto_method=='auto':
		autopl_obj = cvpj_automation.add_pl_points(autoloc, 'float')
		autopl_obj.visual.name = ftr_clip.name
		time_obj = autopl_obj.time
		time_obj.set_posdur(plpos, pldur)

		autopoints_obj = autopl_obj.data

		autopoints_obj.points__add_normal(1, startval if not iseff else startval*defval, 0, None)

		if envpoints:
			for pos, val in envpoints:
				pos = calc_tick_val(bpmdiv, pos)
				if pos<pldur:
					autopoints_obj.points__add_normal(pos, val if not iseff else val*defval, 0, None)

		autopoints_obj.points__add_normal(pldur-0.0001, endval if not iseff else endval*defval, 0, None)

	elif auto_method=='clip':
		autopoints_obj = placement_obj.add_autopoints(mpetype, 4.0)
		autopoints_obj.points__add_normal(0, startval if not iseff else startval*defval, 0, None)
		if envpoints:
			for pos, val in envpoints:
				pos = calc_tick_val(bpmdiv, pos)
				if pos<pldur:
					autopoints_obj.points__add_normal(pos, val if not iseff else val*defval, 0, None)
		autopoints_obj.points__add_normal(pldur, endval if not iseff else endval*defval, 0, None)

class input_fruitytracks(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'

	def get_shortname(self):
		return 'fruitytracks'

	def get_name(self):
		return 'FruityTracks'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def get_configdef(self, configdef):
		cfgpart = configdef.add_enum('pan_auto', 'auto', 'Pan Env')
		cfgpart.add_choice('none', 'None')
		cfgpart.add_choice('auto', 'Auto')
		cfgpart.add_choice('clip', 'Clip')
		cfgpart.add_choice('mixed', 'Mixed')

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import fruitytracks as proj_fruitytracks

		project_obj = proj_fruitytracks.ftr_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks
		cvpj_automation = convproj_obj.automation

		# ---------- convproj params ----------
		pan_auto = dawvert_intent.input_get_param('pan_auto', 'auto')

		# ---------- convproj init ----------
		convproj_obj.type = 'r'
		convproj_obj.set_timings(4.0)

		traits_obj = convproj_obj.traits
		traits_obj.placement_cut = True
		traits_obj.audio_filetypes = ['wav', 'mp3']
		traits_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
		traits_obj.audio_stretch = ['rate']
		traits_obj.auto_types = ['pl_points']

		# ---------- metadata ----------
		if project_obj.title: convproj_obj.metadata.name = project_obj.title
		if project_obj.url: convproj_obj.metadata.url = project_obj.url
		if project_obj.comment:
			convproj_obj.metadata.comment_text = project_obj.comment
			convproj_obj.metadata.comment_datatype = 'rtf'
		convproj_obj.metadata.show = project_obj.showinfo

		# ---------- transport ----------
		bpmdiv = 120/project_obj.bpm
		bpmticks = 5512

		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
		convproj_obj.track_master.params.add('vol', project_obj.vol/128, 'float')

		if project_obj.loopend:
			convproj_obj.transport.loop_active = True
			convproj_obj.transport.loop_start = calc_tick_val(bpmdiv, project_obj.loopstart)
			convproj_obj.transport.loop_end = calc_tick_val(bpmdiv, project_obj.loopstart+project_obj.loopend)

		# ---------- tracks ----------
		for tracknum, ftr_track in enumerate(project_obj.tracks):
			trackid = str(tracknum)
			track_obj = cvpj_tracks.add(trackid, 'audio', 1, False)
			track_obj.visual.name = ftr_track.name if ftr_track.name else 'Track '+str(tracknum)
			track_params = track_obj.params
			track_params.add('pan', (ftr_track.pan-64)/64, 'float')
			track_params.add('vol', ftr_track.vol/128, 'float')
			track_params.add('enabled', not bool(ftr_track.muted), 'bool')

			for pid in sorted(ftr_track.plugins):
				flplug = ftr_track.plugins[pid]

				fxid = trackid+'_'+str(pid)
				splitfile = flplug.name.split('.')

				plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'fruitytracks', splitfile[0].lower())
				plugin_obj.visual.name = splitfile[0]
				plugin_obj.datavals.add('file', flplug.name)
				plugin_obj.role = 'fx'
				plugin_obj.fxdata_add(bool(flplug.enabled), None)
				plugin_params = plugin_obj.params
				for n, v in enumerate(flplug.params): plugin_params.add(str(n), v, 'float')
				track_obj.plugslots.slots_audio.append(fxid)

			for ftr_clip in ftr_track.clips:
				placement_obj = track_obj.placements.add_audio()
				placement_obj.visual.name = ftr_clip.name
				placement_obj.muted = bool(ftr_clip.muted)
				time_obj = placement_obj.time

				# sampleref
				sampleref_obj = convproj_obj.sampleref__add(ftr_clip.file, ftr_clip.file, 'win')
				sampleref_obj.search_local(dawvert_intent.input_folder)

				sp_obj = placement_obj.sample
				sp_obj.sampleref = ftr_clip.file

				plpos = calc_tick_val(bpmdiv, ftr_clip.pos)
				if ftr_clip.stretch == 0:
					pldur = (ftr_clip.dur/bpmticks)
					time_obj.set_loop_data(0, 0, (ftr_clip.repeatlen/bpmticks))
				else:
					pldur = calc_tick_val(bpmdiv, ftr_clip.dur)
					repeatlen = calc_tick_val(bpmdiv, ftr_clip.repeatlen)
					offset = 0 if not ftr_clip.dontstart else calc_tick_val(bpmdiv, ftr_clip.pos%ftr_clip.repeatlen)
					time_obj.set_loop_data(offset, 0, calc_tick_val(bpmdiv, ftr_clip.repeatlen))
					stretch_obj = sp_obj.stretch
					stretch_obj.preserve_pitch = True
					stretch_obj.timing.set__beats(ftr_clip.stretch/4)
				time_obj.set_posdur(plpos, pldur)

				# auto
				envpoints = ftr_clip.vol_env

				# auto: vol
				addauto_obj = addauto_data()
				addauto_obj.autoloc = ['track', trackid, 'vol']
				addauto_obj.mpetype = 'vol'
				addauto_obj.plpos = plpos
				addauto_obj.pldur = pldur
				addauto_obj.bpmdiv = bpmdiv
				addauto_obj.placement_obj = placement_obj
				addauto_obj.ftr_clip = ftr_clip

				addauto_obj.startval = ftr_clip.vol_start/128
				addauto_obj.endval = ftr_clip.vol_end/128
				addauto_obj.envpoints = envpoints
				addauto_obj.defval = ftr_track.vol/128
				addauto_obj.iseff = True
				addauto_obj.auto_method = 'auto'

				if (ftr_clip.vol_start == ftr_clip.vol_end) and not envpoints:
					sp_obj.vol = ftr_clip.vol_start/128
				else:
					make_auto(convproj_obj, addauto_obj)
					
				# auto: pan
				addauto_obj.autoloc = ['track', trackid, 'pan']
				addauto_obj.mpetype = 'pan'
				addauto_obj.startval = (ftr_clip.pan_start-64)/64
				addauto_obj.endval = (ftr_clip.pan_end-64)/64
				addauto_obj.envpoints = None
				addauto_obj.defval = (ftr_track.pan-64)/64
				addauto_obj.iseff = False
				addauto_obj.auto_method = pan_auto

				if (ftr_clip.pan_start == ftr_clip.pan_end):
					sp_obj.pan = (ftr_clip.pan_start-64)/64
				else:
					make_auto(convproj_obj, addauto_obj)

		# ---------- automation ----------
		cvpj_automation.set_persist_all(False)