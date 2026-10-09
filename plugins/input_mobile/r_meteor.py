# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import xtramath
from objects.convproj import fileref
from objects import globalstore
import os

def do_effect(convproj_obj, fxid, plugslots, m_fx):
	typeid = m_fx.typeid
	wetlvl = m_fx.mix/64
	fxparams = m_fx.params
	if typeid!=0:
		strtype = str(typeid)
		plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'meteor', strtype)
		plugin_obj.fxdata_add(True, wetlvl)
		for param_id, datapack_param in globalstore.datapack.get_params('native', 'plugin', strtype):
			paramval = m_fx.params[param_id] if param_id in m_fx.params else None
			plugin_obj.datapack_param__add(param_id, paramval, datapack_param)
		plugslots.slots_audio.append(fxid)

returnnames = {
	1: "Delay",
	2: "Chorus",
	3: "Reverb",
	4: "Phaser",
	5: "Tremolo",
	6: "EQ",
	7: "Pitch Shift",
	8: "Filter",
	9: "Overdrive",
	10: "Tone Boost",
	11: "Noise Gate"
}

class input_meteor(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'meteor'
	
	def get_name(self):
		return 'MeTeoR'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, conversion_state, dawvert_intent):
		from objects.file_proj_mobile import meteor
		project_obj = meteor.meteor_project()
		if dawvert_intent.input_mode == 'file':
			project_obj.load_from_file(dawvert_intent.input_file)
			conversion_state.project = project_obj
			return True

	def to_convproj(self, convproj_obj, dawvert_intent, conversion_state):
		project_obj = conversion_state.project
		from objects import colors

		globalstore.datapack.load('meteor', './data/datapack/app/meteor.xml')
		color_track = colors.colorset.from_datapack('meteor', 'track', 'main')

		# ---------- samples ----------
		data_path = None
		audiopool_path = project_obj.audiopool_path
		if audiopool_path:
			audiopool_path = audiopool_path.split('\\')
			if dawvert_intent.input_mode == 'file':
				while len(audiopool_path)>0:
					outfolder = os.path.join(dawvert_intent.input_folder, *audiopool_path)
					if os.path.exists(outfolder):
						data_path = outfolder
						break
					audiopool_path = audiopool_path[1:]

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks
		cvpj_automation = convproj_obj.automation
		cvpj_metadata = convproj_obj.metadata
		cvpj_master = convproj_obj.track_master
		
		# ---------- convproj init ----------
		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.type = 'r'
		convproj_obj.set_timings(480)
		convproj_obj.do_actions.append('do_addloop')

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav']
		traits_obj.audio_stretch = ['rate']

		# ---------- metadata ----------
		about = project_obj.about
		cvpj_metadata.name = about.title
		cvpj_metadata.author = about.author
		cvpj_metadata.comment_text = about.information
		
		# ---------- transport ----------
		tempo = project_obj.editinfo.tempo
		convproj_obj.params.add('bpm', tempo, 'float')

		# ---------- tracks ----------
		outsamples = {}

		for n, retu in enumerate(project_obj.aux_returns):
			return_obj = cvpj_master.fx__return__add(str(n))
			return_obj.params.add('vol', retu.volume/64, 'float')
			fxid = 'return%i_fx' % (n)
			do_effect(convproj_obj, fxid, return_obj.plugslots, retu.effect)
			fxtypeid = retu.effect.typeid
			if fxtypeid!=0: return_obj.visual.name = returnnames[fxtypeid]

		for n, track in enumerate(project_obj.tracks):
			trackid = 'track_'+str(n)
			color = track.color

			track_obj = cvpj_tracks.add(trackid, 'audio', 1, False)

			# params
			track_obj.params.add('vol', track.volume/64, 'float')
			track_obj.params.add('pan', (track.pan-32)/32, 'float')

			track_obj.visual.name = 'Track #%i' % (n+1)
			track_obj.visual.color.set_int(color_track.getcolornum(track.color))
			track_obj.visual.color.fx_allowed = ['saturate', 'brighter']

			# sends
			auxsendenable = track.auxsendenable
			for n, a in track.auxsend.items():
				if n in auxsendenable: 
					if bool(auxsendenable[n]): 
						track_obj.sends.add(str(n), None, a/64)

			# effects
			effects = track.effects
			for fn, effect in effects.items():
				fxid = 'track%i_fx%i' % (n, fn)
				do_effect(convproj_obj, fxid, track_obj.plugslots, effect)

			# clips
			for clip in track.clips:
				samplenum = clip.sampleid
				sampleid = str(samplenum)

				placement_obj = track_obj.placements.add_audio()
				placement_obj.visual.name = sampleid

				time_obj = placement_obj.time
				time_obj.set_posdur(clip.ticks, clip.ticklength+1)

				if data_path:
					if samplenum not in outsamples:
						sample_filename = 'S%s.WAV' % str(sampleid).zfill(5)
						sample_path = os.path.join(data_path, sample_filename)
						sampleref_obj = convproj_obj.sampleref__add(sampleid, sample_path, None)
						outsamples[samplenum] = sampleref_obj
					sp_obj = placement_obj.sample
					sp_obj.sampleref = sampleid
					sp_obj.stretch.timing.set__orgtempo(tempo)
					sp_obj.stretch.preserve_pitch = True