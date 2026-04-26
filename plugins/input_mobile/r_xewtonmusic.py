# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import xtramath
from objects.convproj import fileref
from objects import globalstore
import os

INST_ENABLED = 1

class input_xewton(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'xewton_music'
	
	def get_name(self):
		return 'Xewton Music Studio'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['']
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_mobile import xewtonmusic
		from objects import audio_data

		project_obj = xewtonmusic.xewtonmusic_song_file()

		convproj_obj.type = 'r'

		traits_obj = convproj_obj.traits
		traits_obj.track_nopl = True

		convproj_obj.set_timings(48)

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', project_obj.header.tempo, 'float')
		convproj_obj.timesig = [project_obj.header.timesig1, project_obj.header.timesig2]
		
		globalstore.datapack.load('xewton', './data/datapack/app/xewton.xml')

		extpath_path = os.path.join(dawvert_intent.path_external_data, 'xewton')
		samplefolder = dawvert_intent.path_samples['extracted']

		instplugs = {}

		for tracknim, xe_tr in project_obj.tracks.items():
			idval = 'track'+str(tracknim)
			track_obj = convproj_obj.track__add(idval, 'instrument', 0, False)

			track_obj.params.add('vol', xe_tr.volume, 'float')
			track_obj.params.add('pan', xe_tr.pan, 'float')

			visual_obj = track_obj.visual
			visual_obj.from_datapack('xewton', 'inst', str(xe_tr.instnum), True)

			if xe_tr.color is not None: 
				cr = xe_tr.color[2]
				cg = xe_tr.color[1]
				cb = xe_tr.color[0]
				visual_obj.color.set_int([cr, cg, cb])

			if INST_ENABLED:
				if xe_tr.instnum not in instplugs:
					instplug = 'inst'+str(xe_tr.instnum)
					plugin_obj = convproj_obj.plugin__add(instplug, 'universal', 'sampler', 'multi')
					instplugs[xe_tr.instnum] = [plugin_obj, [track_obj]]
				else:
					instplugs[xe_tr.instnum][1].append(track_obj)
				track_obj.plugslots.set_synth(instplug)

			cvpj_notelist = track_obj.placements.notelist
			tracknotes = xe_tr.notes.notes

			for n in tracknotes:
				cvpj_notelist.add_r(int(n.pos), int(n.dur), n.key-60, n.vol/127, None)

				noteauto = n.auto
				if noteauto:
					pp = noteauto[0][0]
					for p, v in noteauto:
						val = ((v-8192)/8192)*24
						if (p-pp)>5:
							cvpj_notelist.last_add_auto_instant('pitch', p, val)
						else:
							cvpj_notelist.last_add_auto('pitch', p, val)
						pp = p
						if n.dur<p: break

		if INST_ENABLED:
			for instnum, instdata in instplugs.items():
				plugin_obj, tracks = instdata
				dp_obj = globalstore.datapack.get_obj('xewton', 'inst', str(instnum))
				if dp_obj is not None:
					dpdata = dp_obj.data
					filename = dpdata['filename'] if 'filename' in dpdata else None
					if filename:
						instfilename = os.path.join(extpath_path, filename)
						if os.path.exists(instfilename):
							inst_obj = xewtonmusic.xewtonmusic_inst_file()
							inst_obj.load_from_file(instfilename)
	
							plugin_obj.env_asdr_add('vol', 0, inst_obj.header.attack, 0, 0, 1, inst_obj.header.release, 1)
	
							isdrums = max([s.key_hi-s.key_lo for s in inst_obj.samples])==0
	
							if isdrums:
								for t in tracks:
									t.is_drum = True
	
							for n, s in enumerate(inst_obj.samples):
								wavfilename = os.path.join(samplefolder, s.filename)
								org_filename =  s.filename
	 
								sampleref_obj = convproj_obj.sampleref__add(s.filename, wavfilename, None)
								audio_obj = audio_data.audio_obj()
								audio_obj.rate = 22050 
								audio_obj.channels = 2
								audio_obj.set_codec('int16')
								audio_obj.pcm_from_bytes(s.data)
								audio_obj.to_file_wav(wavfilename)
								sampleref_obj.set_fileformat('wav')
								audio_obj.to_sampleref_obj(sampleref_obj)
	
								#print(sampleref_obj.get_dur_samples(), s.loop_on, s.loop_1//2, s.loop_2//2, s.loop_3//2, s.filename)
	
								sp_obj = plugin_obj.sampleregion_add(s.key_lo-60, s.key_hi-60, s.key_root-60, None)
								sp_obj.point_value_type = "samples"
								sp_obj.sampleref = s.filename
								sp_obj.start = 0
								sp_obj.vol = s.vol
								sp_obj.end = sampleref_obj.get_dur_samples()
								#sp_obj.loop_start = s.loop_1
								sp_obj.loop_end = sp_obj.end
								sp_obj.loop_active = bool(s.loop_on)
								sp_obj.trigger = 'oneshot' if isdrums else 'normal'
	
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')