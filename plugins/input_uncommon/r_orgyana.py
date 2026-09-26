# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
import plugins
import os

class input_orgyana(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'orgyana'
	
	def get_name(self):
		return 'Orgyana'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:synth-osc']
		in_dict['projtype'] = 'r'

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.headers.append([0, b'Org-02'])
		detectdef_obj.headers.append([0, b'Org-03'])

	def get_configdef(self, configdef):
		configdef.add_bool('use_groups', True, 'Enable Groups')
		cfgpart = configdef.add_float('panlvl', 1.0, 'Pan Amount')
		cfgpart.set_range(-1, 1)
		configdef.set_group('pan_auto', 'Pan Auto')
		cfgpart = configdef.add_enum('pan_auto', 'track', 'Auto Type')
		cfgpart.add_choice('none', 'None')
		cfgpart.add_choice('track', 'Track')
		cfgpart.add_choice('note', 'Notes')
		cfgpart = configdef.add_float('pan_smooth', 0.75, 'Smooth')
		cfgpart.set_range(0, 1)

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_uncommon import orgyana as proj_orgyana
		from objects import colors
		from objects import audio_data

		# ---------- load file: project ----------
		project_obj = proj_orgyana.orgyana_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		# ---------- load file: orgsamp ----------
		orgsamp_filename = os.path.join(dawvert_intent.path_external_data, 'orgyana', 'orgsamp.dat')
		orgsamp_obj = proj_orgyana.orgyana_orgsamp()
		if os.path.exists(orgsamp_filename): orgsamp_obj.load_from_file(orgsamp_filename)

		orgdrum_sob = {}

		# ---------- datapack ----------
		globalstore.datapack.load('orgyana', './data/datapack/app/orgyana.xml')
		colordata = colors.colorset.from_datapack('orgyana', 'track', 'orgmaker_2')

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks
		cvpj_groups = convproj_obj.groups
		cvpj_automation = convproj_obj.automation

		# ---------- convproj params ----------
		use_groups = dawvert_intent.input_get_param('use_groups', True)
		pan_auto = dawvert_intent.input_get_param('pan_auto', 'none')
		panlvl = dawvert_intent.input_get_param('panlvl', 1)
		pan_smooth = dawvert_intent.input_get_param('pan_smooth', 0.25)

		# ---------- convproj init ----------
		convproj_obj.type = 'r'
		convproj_obj.set_timings(4)
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['nopl_points']
		traits_obj.track_nopl = True

		# ---------- transport ----------
		convproj_obj.params.add('bpm', (1/(project_obj.wait/122))*122, 'float')
		convproj_obj.timesig = [project_obj.stepsperbar, project_obj.beatsperstep]

		if project_obj.loop_beginning != 0: 
			convproj_obj.transport.loop_active = True
			convproj_obj.transport.loop_start = project_obj.loop_beginning
			convproj_obj.transport.loop_end = project_obj.loop_end

		# ---------- tracks ----------
		drum_tracks = []
		for tracknum, orgtrack_obj in enumerate(project_obj.tracks):
			if len(orgtrack_obj.notes) != 0:
				idval = 'org_'+str(tracknum)
				track_obj = cvpj_tracks.add(idval, 'instrument', 0, False)
				if tracknum > 7: # drums
					drum_tracks.append(track_obj)
					track_obj.is_drum = True

					# visual
					track_obj.visual.from_datapack('orgyana', 'drums', str(orgtrack_obj.instrument), False)

					# plugin
					if orgsamp_obj.loaded:
						# drum sample
						drum_filename = os.path.join(dawvert_intent.path_samples['extracted']+'orgmaker_drum_'+str(orgtrack_obj.instrument)+'.wav')
						if orgtrack_obj.instrument not in orgdrum_sob:
							audio_obj = audio_data.audio_obj()
							audio_obj.set_codec('int8')
							audio_obj.rate = orgsamp_obj.drum_rate
							audio_obj.pcm_from_list(orgsamp_obj.drum_data[orgtrack_obj.instrument])
							audio_obj.to_file_wav(drum_filename)
							sampleref_obj = convproj_obj.sampleref__add(drum_filename, drum_filename, None)
							sampleref_obj.set_fileformat('wav')
							audio_obj.to_sampleref_obj(sampleref_obj)
							orgdrum_sob[orgtrack_obj.instrument] = sampleref_obj

						plugin_obj, pluginid, sp_obj = convproj_obj.plugin__addspec__sampler__genid__s_obj(orgdrum_sob[orgtrack_obj.instrument], drum_filename)
						sp_obj.trigger = 'oneshot'
						track_obj.plugslots.set_synth(pluginid)
				else: # melody
					# visual
					track_obj.visual.name = "Melody "+str(tracknum+1)

					# plugin
					if orgsamp_obj.loaded:
						plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
						track_obj.plugslots.set_synth(pluginid)
						osc_data = plugin_obj.osc_add()
						osc_data.prop.type = 'wave'
						osc_data.prop.nameid = 'main'
						wave_obj = plugin_obj.wave_add('main')
						wave_obj.set_all_range(list(orgsamp_obj.sample_data[orgtrack_obj.instrument]), -128, 128)
						track_obj.plugslots.set_synth(pluginid)

				track_obj.visual.color.set_int(colordata.getcolornum(tracknum))
				track_obj.params.add('pitch', (orgtrack_obj.pitch-1000)/1800, 'float')

				posnotes = {}
				for org_note in orgtrack_obj.notes: posnotes[org_note[0]] = org_note[1:5]
				posnotes = dict(sorted(posnotes.items(), key=lambda item: item[0]))
				endnote = None
				notedur = 0
				org_notelist = []

				cvpj_notelist = track_obj.placements.notelist

				pan_autoid = ['track', idval, 'pan']

				last_pan_pos = 0
				last_pan_val = 0

				if pan_auto=='track': pan_auto_obj = cvpj_automation.create(['track', idval, 'pan'], 'float', False).make_nopl_points()

				for pos, orgnote in posnotes.items():
					note, dur, vol, pan = orgnote
					pan = (pan-6)/6

					if endnote != None: 
						if pos >= endnote: endnote = None
					if orgnote[1] != 1:
						notedur = orgnote[1]
						endnote = pos+notedur
					if endnote != None: isinsidenote = False if endnote-pos == notedur else True
					else: isinsidenote = False
					if not isinsidenote: 
						extradata = None
						if pan_auto=='note': extradata = {'pan': pan}
						cvpj_notelist.add_r(pos, dur, note-24 if tracknum > 7 else note-36, vol/254, extradata)
						if pan_auto=='track':
							if pan or last_pan_val:
								pan_auto_obj.points__add_point(pos, pan*panlvl, 'instant')
						elif pan_auto=='note':
							notepos = pos
					else:
						if pan!=last_pan_val:
							if last_pan_pos>1:
								if pan_auto=='track':
									pan_auto_obj.points__add_point(pos-pan_smooth, last_pan_val*panlvl, 'normal')
									pan_auto_obj.points__add_point(pos+pan_smooth, pan*panlvl, 'normal')
								elif pan_auto=='note':
									insidepos = pos-notepos
									cvpj_notelist.last_add_auto('pan', insidepos-pan_smooth, last_pan_val*panlvl)
									cvpj_notelist.last_add_auto('pan', insidepos+pan_smooth, pan*panlvl)
					last_pan_pos = pos
					last_pan_val = pan

		# ---------- grouping ----------
		if use_groups:
			convproj_obj.fxtype = 'groupreturn'

			track_obj = cvpj_groups.add('drums')
			track_obj.visual.name = 'Drums/SFX'
			
			for track_obj in drum_tracks:
				track_obj.group = 'drums'
