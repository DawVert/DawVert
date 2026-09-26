# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import numpy as np
from objects import globalstore

class input_cvpj_f(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'pixitracker'
	
	def get_name(self):
		return 'Pixitracker'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:sampler:single']
		in_dict['projtype'] = 'rs'

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.headers.append([0, b'PIXIMOD1'])

	def get_configdef(self, configdef):
		configdef.add_bool('tracker_mode', False, 'Tracker Mode')

	def parse(self, convproj_obj, dawvert_intent):
		from objects import audio_data
		from objects import colors
		from objects.file_proj_uncommon import piximod as proj_piximod

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav']

		project_obj = proj_piximod.piximod_song()

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks

		globalstore.datapack.load('pixitracker', './data/datapack/app/pixitracker.xml')
		colordata = colors.colorset.from_datapack('pixitracker', 'inst', 'main')

		swing = project_obj.shuffle/100
		samplefolder = dawvert_intent.path_samples['extracted']

		for instnum, pixi_sound in enumerate(project_obj.sounds):
			cvpj_instid = 'pixi_'+str(instnum)

			track_obj = cvpj_tracks.add(cvpj_instid, 'instrument', 1, False)
			track_obj.visual.name = 'Inst #'+str(instnum+1)
			track_obj.visual.color.set_int(colordata.getcolor())
			track_obj.params.add('pitch', (pixi_sound.fine/100)+(0.2 if pixi_sound.channels == 1 else 0.4), 'float')
			track_obj.params.add('vol', pixi_sound.volume/100, 'float')
			track_obj.datavals.add('middlenote', pixi_sound.transpose*-1)

			wave_path = samplefolder + str(instnum) + '.wav'

			audio_obj = audio_data.audio_obj()
			audio_obj.channels = pixi_sound.channels
			audio_obj.rate = pixi_sound.rate//pixi_sound.channels
			audio_obj.set_codec('int16')
			audio_obj.pcm_from_bytes(pixi_sound.data)
			audio_obj.to_file_wav(wave_path)

			plugin_obj, synthid, sampleref_obj, samplepart_obj = convproj_obj.plugin__addspec__sampler__genid(wave_path, None)
			sampleref_obj.set_fileformat('wav')
			audio_obj.to_sampleref_obj(sampleref_obj)
			track_obj.plugslots.set_synth(synthid)

			plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)
			samplepart_obj.point_value_type = "samples"
			if pixi_sound.end != 0:
				samplepart_obj.start = pixi_sound.start
				samplepart_obj.end = pixi_sound.end
				samplepart_obj.length = len(pixi_sound.data)//pixi_sound.channels


		if not dawvert_intent.input_get_param('tracker_mode', 0):
			convproj_obj.type = 'rs'
			convproj_obj.set_timings(1.0) 
			convproj_obj.params.add('bpm', project_obj.bpm, 'float')
			convproj_obj.track_master.params.add('vol', project_obj.vol/100, 'float')

			for pat_num, pat_data_r in project_obj.patterns.items():
				sceneid = str(pat_num)

				scene_obj = convproj_obj.scene__add(sceneid)
				scene_obj.visual.name = 'Pat #'+str(pat_num+1)

				pat_data = np.rot90(pat_data_r.data)
				numtracks = len(pat_data)

				instnotes = [[] for x in range(16)]

				for num in range(numtracks):
					c_track = (numtracks-1)-num
					s_data = pat_data[[c_track]][0]

					vol_where = np.where(s_data[:, 0]!=0)[0]

					track_data = np.zeros((len(vol_where), 6), dtype=np.uint8)

					for num, pos in enumerate(vol_where):
						track_data[num,:][0:4] = s_data[pos]
						track_data[num,:][4] = pos
						if num>0: track_data[num-1,:][5] = track_data[num,:][4]-track_data[num-1,:][4]
					if len(vol_where): track_data[-1,:][5] = len(s_data)-track_data[-1,:][4]

					for x in track_data: instnotes[x[1]].append(x)

				for instnum, instnote in enumerate(instnotes):
					if len(instnote):
						cvpj_instid = 'pixi_'+str(instnum)
						trscene_obj = cvpj_tracks.add_scene(cvpj_instid, sceneid, 'main')
						placement_obj = trscene_obj.add_notes()
						placement_obj.visual.name = 'Pat #'+str(pat_num+1)
						time_obj = placement_obj.time
						time_obj.set_posdur(0, pat_data_r.length)

						cvpj_notelist = placement_obj.notelist

						for nnn in instnote:
							pos = nnn[4]
							dur = nnn[5]
							if pos%2:
								pos += swing
								dur -= swing
							else:
								dur += swing

							if nnn[2]: cvpj_notelist.add_r(pos, dur, int(nnn[0])-78, int(nnn[2])/100, None)

			curpos = 0
			for pat_num in project_obj.order:
				size = project_obj.patterns[pat_num].length
				scenepl_obj = convproj_obj.scene__add_pl()
				scenepl_obj.position = curpos
				scenepl_obj.duration = size
				scenepl_obj.id = str(pat_num)
				curpos += size
		#else:
		#	convproj_obj.type = 'ts'
		#	numtracks = max([v.tracks for k, v in project_obj.patterns.items()])

		#	tracker_obj = convproj_obj.main__create_tracker_single()
		#	tracker_obj.set_num_chans(numtracks)
		#	tracker_obj.mainvisual.from_datapack('tracker_various', 'mod', 'main', True)
		#	tracker_obj.tempo = project_obj.bpm
		#	tracker_obj.speed = 6
		#	tracker_obj.orders = project_obj.order
		#	tracker_obj.use_starttempo = True

		#	for num_pat, pat_data in project_obj.patterns.items():
		#		pattern_obj = tracker_obj.pattern_add(num_pat, pat_data.length)
		#		for num_row, row_data in enumerate(pat_data.data):
		#			for num_ch, nnn in enumerate(row_data):
		#				if nnn[2]: 
		#					pattern_obj.cell_note(num_ch, num_row, int(nnn[0])-78, int(nnn[1]))

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_lanefit')
