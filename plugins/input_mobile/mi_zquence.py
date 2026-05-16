# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import struct

def color_to_int(c):
	Color = struct.unpack('BBBB', struct.pack('<i', c))
	return [Color[0], Color[1], Color[2]]

def text_float(c):
	return float(c.replace(',', '.'))

def do_mixer(convproj_obj, num, mixerchan):
	fxchannel_obj = convproj_obj.fx__chan__add(num)
	mixerattrib = mixerchan.attrib
	if 'Volyme' in mixerattrib: 
		fxchannel_obj.params.add('vol', text_float(mixerattrib['Volyme']), 'float')
	if 'Pan' in mixerattrib:
		fxchannel_obj.params.add('pan', text_float(mixerattrib['Pan']), 'float')
	if 'FXEnable' in mixerattrib:
		fxchannel_obj.plugslots.slots_audio_enabled = mixerattrib['FXEnable']=='True'
	if 'Active' in mixerattrib:
		fxchannel_obj.params.add('enabled', mixerattrib['Active']=='True', 'bool')
	if 'UniqueName' in mixerattrib: 
		fxchannel_obj.visual.name = mixerattrib['UniqueName']
	for group in mixerchan.groups:
		if group.name == 'Effects':
			for fxgroup in group:
				fxattrib = fxgroup.attrib
				dspid = fxattrib['DspID']
				fxid = 'fx_'+dspid
				fxname = fxattrib['DspName'].replace(' ', '_').lower()
				plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'zquence', fxname)
				plugin_obj.role = 'fx'
				for fxd in fxgroup.groups:
					if fxd.name=='Parameters':
						for n, v in fxd.attrib.items():
							plugin_obj.params.add(n, text_float(v), 'float')
				fxchannel_obj.plugslots.slots_audio.append(fxid)

class input_zquence(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'zquence'
	
	def get_name(self):
		return 'Zquence Studio 2016'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		pass

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_mobile import zquence

		project_obj = zquence.zquence_song()

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'mi'

		traits_obj = convproj_obj.traits

		convproj_obj.set_timings(96)

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		mixercount = 0
		mixerassoc = {}
		if project_obj.mixers:
			for mixer in project_obj.mixers:
				if mixer.name == 'MainMixer':
					for mixerchan in mixer.groups:
						mixerattrib = mixerchan.attrib
						mixerassoc[mixerattrib['ID']] = mixercount
						do_mixer(convproj_obj, mixercount, mixerchan)
						mixercount += 1
				if mixer.name == 'AdditionalMixers':
					for mixerchan in mixer.groups:
						mixerattrib = mixerchan.attrib
						mixerassoc[mixerattrib['ID']] = mixercount
						do_mixer(convproj_obj, mixercount, mixerchan)
						mixercount += 1

		synthgrpassoc = {}
		if project_obj.tracks:
			for track in project_obj.tracks:
				trackattrib = track.attrib
				trackid = trackattrib['TrackID']
				inst_obj = convproj_obj.instrument__add(trackid)
				if 'MixerChannelID' in trackattrib:
					MixerChannelID = trackattrib['MixerChannelID']
					if MixerChannelID in mixerassoc:
						inst_obj.fxrack_channel = mixerassoc[MixerChannelID]
				trkgrps = track.groups
				for group in trkgrps:
					if group.name == 'Synthesizer':
						synthattrib = group.attrib
						visual_obj = inst_obj.visual

						if 'TrackName' in synthattrib: 
							visual_obj.name = synthattrib['TrackName']
							synthgrpassoc[synthattrib['TrackName']] = trackid

						if 'Color' in synthattrib:
							Color = int(synthattrib['Color'])
							visual_obj.color.set_int(color_to_int(Color))

						if 'DspName' in synthattrib:
							dspname = synthattrib['DspName']
							if dspname=='SamplerSynth':
								plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'drums')
								plugin_obj.role = 'synth'
								inst_obj.plugslots.plugin_autoplace(plugin_obj, pluginid)
								for x in group:
									if x.name=='EData':
										for instpart in x.groups:
											attrib = instpart.attrib
											if instpart.name == 'ContentFiles':
												if 'File' in attrib:
													files = attrib['File']
													if isinstance(files, list):
														for f in files:
															sampleref_obj = convproj_obj.sampleref__add(f, f, None)
															if sampleref_obj: 
																sampleref_obj.search_local(dawvert_intent.input_folder)
													else:
														sampleref_obj = convproj_obj.sampleref__add(files, files, None)
														if sampleref_obj: 
															sampleref_obj.search_local(dawvert_intent.input_folder)

											if instpart.name == 'Node':
												for i in instpart:
													if i.name=='Notes':
														for p in i:
															drump = p.attrib
															key = int(drump['K']) if 'K' in drump else 0
															file = drump['F'] if 'F' in drump else ''

															drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
															drumpad_obj.key = key-60
															drumpad_obj.visual.name = file
															layer_obj.samplepartid = 'drum_%i' % key
															sp_obj = plugin_obj.samplepart_add(layer_obj.samplepartid)
															sp_obj.sampleref = file



		if project_obj.patterns:
			for pattern in project_obj.patterns:
				patternattrib = pattern.attrib

				if 'PatternName' in patternattrib:
					notelistname = patternattrib['PatternName']
					nle_obj = convproj_obj.notelistindex__add(notelistname)
					visual_obj = nle_obj.visual
					visual_obj.name = notelistname
					cvpj_notelist = nle_obj.notelist

					if 'Color' in patternattrib:
						Color = int(patternattrib['Color'])
						visual_obj.color.set_int(color_to_int(Color))

					patterngrps = pattern.groups
					for patterngrp in patterngrps:
						if patterngrp.name == 'Sequences':
							for seqsgrp in patterngrp.groups:
								seqsgrpattrib = seqsgrp.attrib

								if seqsgrp.name == 'Sequence':
									instid = None
									if 'ReferencedToTrack.TrackName' in seqsgrpattrib:
										instid = seqsgrpattrib['ReferencedToTrack.TrackName']
										if instid in synthgrpassoc: instid = synthgrpassoc[instid]

									if instid:
										for inseqgrp in seqsgrp.groups:
											if inseqgrp.name == 'Notes':
												for notesgrp in inseqgrp.groups:
													noteattrib = notesgrp.attrib

													note_NoteKey = int(noteattrib['NoteKey']) if 'NoteKey' in noteattrib else 60
													note_TickLength = int(noteattrib['TickLength']) if 'TickLength' in noteattrib else 48
													note_TickStart = int(noteattrib['TickStart']) if 'TickStart' in noteattrib else 0
													note_Velocity = int(noteattrib['Velocity']) if 'Velocity' in noteattrib else 127
													note_Pan = int(noteattrib['Pan'])/127 if 'Pan' in noteattrib else 0

													cvpj_notelist.add_m(instid, note_TickStart, note_TickLength, note_NoteKey-60, note_Velocity/127, None if not note_Pan else {'pan': note_Pan})

		if project_obj.references:
			playlist_stor = {}

			for reference in project_obj.references:
				referenceattrib = reference.attrib

				ref_Start = int(referenceattrib['Start'])
				ref_Stop = int(referenceattrib['Stop'])
				ref_Length = int(referenceattrib['Length'])
				ref_GraphicLength = int(referenceattrib['GraphicLength'])
				ref_TrackStationIndex = int(referenceattrib['TrackStationIndex'])
				ref_ReferencedToPattern_PatternName = referenceattrib['ReferencedToPattern.PatternName']

				if ref_TrackStationIndex not in playlist_stor:
					playlist_stor[ref_TrackStationIndex] = convproj_obj.playlist__add(ref_TrackStationIndex, 1, True)

				playlist_obj = playlist_stor[ref_TrackStationIndex]
				placement_obj = playlist_obj.placements.add_notes_indexed()
				placement_obj.fromindex = ref_ReferencedToPattern_PatternName
				time_obj = placement_obj.time
				time_obj.set_posdur(ref_Start, ref_GraphicLength)

		if project_obj.globals:
			zglobals = project_obj.globals.attrib

			if 'BPM' in zglobals:
				convproj_obj.params.add('bpm', int(zglobals['BPM']), 'float')
			if 'CycleStartPosition' in zglobals:
				convproj_obj.transport.loop_start = int(zglobals['CycleStartPosition'])
			if 'CycleEndPosition' in zglobals:
				convproj_obj.transport.loop_end = int(zglobals['CycleEndPosition'])
			if 'TimeSignatureDenominator' in zglobals:
				convproj_obj.timesig[0] = int(zglobals['TimeSignatureDenominator'])
			if 'TimeSignatureNumerator' in zglobals:
				convproj_obj.timesig[1] = int(zglobals['TimeSignatureNumerator'])

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')