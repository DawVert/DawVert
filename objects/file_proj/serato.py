# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from objects.exceptions import ProjectFileParserException

DEBUG_IN_OUT = False

class serato_sample:
	def __init__(self, json_data):
		self.file = json_data['file'] if 'file' in json_data else None
		self.reverse = json_data['reverse'] if 'reverse' in json_data else None
		self.start = json_data['start'] if 'start' in json_data else 0
		self.end = json_data['end'] if 'end' in json_data else 1
		self.color = json_data['color'] if 'color' in json_data else None
		self.polyphonic = json_data['polyphonic'] if 'polyphonic' in json_data else None
		self.attack = json_data['attack'] if 'attack' in json_data else None
		self.release = json_data['release'] if 'release' in json_data else None
		self.pitch_shift = json_data['pitch_shift'] if 'pitch_shift' in json_data else 0
		self.playback_speed = json_data['playback_speed'] if 'playback_speed' in json_data else 1
	def dump(self):
		out = {}
		if self.file is not None: out['file'] = self.file
		if self.reverse is not None: out['reverse'] = self.reverse
		if self.start: out['start'] = self.start
		out['end'] = self.end
		if self.color is not None: out['color'] = self.color
		if self.polyphonic is not None: out['polyphonic'] = self.polyphonic
		if self.attack is not None: out['attack'] = self.attack
		if self.release is not None: out['release'] = self.release
		if self.pitch_shift != 0: out['pitch_shift'] = self.pitch_shift
		if self.playback_speed != 1: out['playback_speed'] = self.playback_speed
		return out

class serato_drum:
	def __init__(self, json_data):
		self.used = json_data != None
		if self.used:
			self.sample = serato_sample(json_data['sample']) if 'sample' in json_data else None
			self.channel_strip = serato_channel_strip(json_data['channel_strip'] if 'channel_strip' in json_data else None)
	def dump(self):
		if self.used:
			out = {}
			out['sample'] = self.sample.dump()
			if self.channel_strip.used: out['channel_strip'] = self.channel_strip.dump()
			return out

class serato_channel_strip:
	def __init__(self, json_data):
		self.used = json_data != None
		if self.used:
			self.post_fader_effects = json_data['post_fader_effects'] if 'post_fader_effects' in json_data else None
			self.volume = json_data['volume'] if 'volume' in json_data else None
			self.high_eq = json_data['high_eq'] if 'high_eq' in json_data else None
			self.mid_eq = json_data['mid_eq'] if 'mid_eq' in json_data else None
			self.low_eq = json_data['low_eq'] if 'low_eq' in json_data else None
			self.pan = json_data['pan'] if 'pan' in json_data else None
			self.gain = json_data['gain'] if 'gain' in json_data else None
			self.filter = json_data['filter'] if 'filter' in json_data else None
			self.mute = json_data['mute'] if 'mute' in json_data else None
			self.post_fader_effects_beats = json_data['post_fader_effects_beats'] if 'post_fader_effects_beats' in json_data else None
		else:
			self.post_fader_effects = None
			self.volume = None
			self.high_eq = None
			self.mid_eq = None
			self.low_eq = None
			self.pan = None
			self.gain = None
			self.filter = None
			self.mute = None
			self.post_fader_effects_beats = None
	def dump(self):
		out = {}
		if self.high_eq is not None: out['high_eq'] = self.high_eq
		if self.mid_eq is not None: out['mid_eq'] = self.mid_eq
		if self.low_eq is not None: out['low_eq'] = self.low_eq
		if self.volume is not None: out['volume'] = self.volume
		if self.pan is not None: out['pan'] = self.pan
		if self.gain is not None: out['gain'] = self.gain
		if self.filter is not None: out['filter'] = self.filter
		if self.mute is not None: out['mute'] = self.mute
		if self.post_fader_effects is not None: out['post_fader_effects'] = self.post_fader_effects
		if self.post_fader_effects_beats is not None: out['post_fader_effects_beats'] = self.post_fader_effects_beats
		return out

class serato_scene_deck:
	def __init__(self, json_data):
		self.type = json_data['type'] if 'type' in json_data else ''
		self.name = json_data['name'] if 'name' in json_data else ''
		self.content_name = json_data['content_name'] if 'content_name' in json_data else ''
		self.groove_amount = json_data['groove_amount'] if 'groove_amount' in json_data else 0.0
		self.channel_strip = serato_channel_strip(json_data['channel_strip'] if 'channel_strip' in json_data else None)
		self.drums = [serato_drum(x) for x in json_data['drums']] if 'drums' in json_data else None
		self.make_sequence_genre = json_data['make_sequence_genre'] if 'make_sequence_genre' in json_data else None
		self.view = json_data['view'] if 'view' in json_data else None
		self.deck_source_properties_changed = json_data['deck_source_properties_changed'] if 'deck_source_properties_changed' in json_data else None
		self.zoom = json_data['zoom'] if 'zoom' in json_data else None
		self.original_key = json_data['original_key'] if 'original_key' in json_data else None
		self.tempo_map = json_data['tempo_map'] if 'tempo_map' in json_data else None
		self.sample_file = json_data['sample_file'] if 'sample_file' in json_data else None
		self.original_bpm = json_data['original_bpm'] if 'original_bpm' in json_data else None
		self.sample_regions = json_data['sample_regions'] if 'sample_regions' in json_data else None
		self.bpm = json_data['bpm'] if 'bpm' in json_data else None
		self.cues = json_data['cues'] if 'cues' in json_data else None
		self.momentary = json_data['momentary'] if 'momentary' in json_data else True
		self.attack = json_data['attack'] if 'attack' in json_data else None
		self.release = json_data['release'] if 'release' in json_data else None
		self.instrument_file = json_data['instrument_file'] if 'instrument_file' in json_data else None
		self.polyphony = json_data['polyphony'] if 'polyphony' in json_data else None
		self.sequence_view = json_data['sequence_view'] if 'sequence_view' in json_data else None
		self.bar_mode_enabled = json_data['bar_mode_enabled'] if 'bar_mode_enabled' in json_data else True
		self.playback_speed = json_data['playback_speed'] if 'playback_speed' in json_data else 1
		self.key_shift = json_data['key_shift'] if 'key_shift' in json_data else 0
		self.plugin_description = json_data['plugin_description'] if 'plugin_description' in json_data else None
		self.state = json_data['state'] if 'state' in json_data else None
		self.parameters = json_data['parameters'] if 'parameters' in json_data else None
		self.glide_mode = json_data['glide_mode'] if 'glide_mode' in json_data else None
		self.glide_duration = json_data['glide_duration'] if 'glide_duration' in json_data else None
	def dump(self):
		out = {}
		out['type'] = self.type
		out['name'] = self.name
		if self.content_name: out['content_name'] = self.content_name
		if self.groove_amount != 0: out['groove_amount'] = self.groove_amount
		out['channel_strip'] = self.channel_strip.dump()
		if self.drums: out['drums'] = [x.dump() for x in self.drums]
		if self.make_sequence_genre is not None: out['make_sequence_genre'] = self.make_sequence_genre
		if self.deck_source_properties_changed is not None: out['deck_source_properties_changed'] = self.deck_source_properties_changed
		if self.original_key is not None: out['original_key'] = self.original_key
		if self.tempo_map is not None: out['tempo_map'] = self.tempo_map
		if self.sample_file is not None: out['sample_file'] = self.sample_file
		if self.original_bpm is not None: out['original_bpm'] = self.original_bpm
		if self.sample_regions is not None: out['sample_regions'] = self.sample_regions
		if self.polyphony is not None: out['polyphony'] = self.polyphony
		if self.momentary != True: out['momentary'] = self.momentary
		if self.key_shift != 0: out['key_shift'] = self.key_shift
		if self.bpm is not None: out['bpm'] = self.bpm
		if self.zoom is not None: out['zoom'] = self.zoom
		if self.cues is not None: out['cues'] = self.cues
		if self.attack is not None: out['attack'] = self.attack
		if self.release is not None: out['release'] = self.release
		if self.instrument_file is not None: out['instrument_file'] = self.instrument_file
		if self.sequence_view is not None: out['sequence_view'] = self.sequence_view
		if self.bar_mode_enabled is not True: out['bar_mode_enabled'] = self.bar_mode_enabled
		if self.playback_speed != 1: out['playback_speed'] = self.playback_speed
		if self.plugin_description is not None: out['plugin_description'] = self.plugin_description
		if self.state is not None: out['state'] = self.state
		if self.parameters is not None: out['parameters'] = self.parameters
		if self.view != None: out['view'] = self.view
		if self.glide_mode != None: out['glide_mode'] = self.glide_mode
		if self.glide_duration != None: out['glide_duration'] = self.glide_duration
		return out

class serato_note:
	def __init__(self, json_data):
		self.start = json_data['start']
		self.duration = json_data['duration']
		self.channel = json_data['channel'] if 'channel' in json_data else 0
		self.number = json_data['number']
		self.velocity = json_data['velocity'] if 'velocity' in json_data else None
	def dump(self):
		out = {}
		out['start'] = self.start
		out['duration'] = self.duration
		if self.channel: out['channel'] = self.channel
		out['number'] = self.number
		if self.velocity is not None: out['velocity'] = self.velocity
		return out

class serato_auto_keyframe:
	def __init__(self, json_data):
		self.time = json_data['time'] if 'time' in json_data else 0
		self.value = json_data['value'] if 'value' in json_data else 0
		self.interpolation = json_data['interpolation'] if 'interpolation' in json_data else None
		self.curvature = json_data['curvature'] if 'curvature' in json_data else 0
	def dump(self):
		out = {}
		out['time'] = self.time
		out['value'] = self.value
		if self.interpolation: out['interpolation'] = self.interpolation
		if self.curvature: out['curvature'] = self.curvature
		return out

class serato_automation_curve:
	def __init__(self, json_data):
		self.type = json_data['type'] if 'type' in json_data else None
		self.parameter = json_data['parameter'] if 'parameter' in json_data else None
		self.keyframes = [serato_auto_keyframe(x) for x in json_data['keyframes']] if 'keyframes' in json_data else []
	def dump(self):
		out = {}
		out['type'] = self.type
		out['parameter'] = self.parameter
		out['keyframes'] = [x.dump() for x in self.keyframes]
		return out

class serato_deck_sequence:
	def __init__(self, json_data):
		self.notes = [serato_note(x) for x in json_data['notes']] if 'notes' in json_data else []
		self.secondary_notes = [serato_note(x) for x in json_data['secondary_notes']] if 'secondary_notes' in json_data else []
		self.automation_curves = [serato_automation_curve(x) for x in json_data['automation_curves']] if 'automation_curves' in json_data else []
	def dump(self):
		out = {}
		if self.notes: out['notes'] = [x.dump() for x in self.notes]
		if self.secondary_notes: out['secondary_notes'] = [x.dump() for x in self.secondary_notes]
		if self.automation_curves: out['automation_curves'] = [x.dump() for x in self.automation_curves]
		return out

class serato_scene:
	def __init__(self, json_data):
		self.name = json_data['name'] if 'name' in json_data else None
		self.length = json_data['length'] if 'length' in json_data else None
		self.deck_sequences = [serato_deck_sequence(x) for x in json_data['deck_sequences']] if 'deck_sequences' in json_data else []
	def dump(self):
		out = {}
		out['name'] = self.name
		out['length'] = self.length
		out['deck_sequences'] = [x.dump() for x in self.deck_sequences]
		return out

class serato_arrangement_clip:
	def __init__(self, json_data):
		self.start = json_data['start']
		self.length = json_data['length']
		self.scene_slot_number = json_data['scene_slot_number'] if 'scene_slot_number' in json_data else None
		self.audio_deck_index = json_data['audio_deck_index'] if 'audio_deck_index' in json_data else None
		self.track_sample = json_data['track_sample'] if 'track_sample' in json_data else None
	def dump(self):
		out = {}
		out['start'] = self.start
		out['length'] = self.length
		out['scene_slot_number'] = self.scene_slot_number
		if self.audio_deck_index is not None: out['audio_deck_index'] = self.audio_deck_index
		if self.track_sample is not None: out['track_sample'] = self.track_sample
		return out

class serato_arrangement_track:
	def __init__(self, json_data):
		self.type = json_data['type']
		self.name = json_data['name']
		self.channel_strip = serato_channel_strip(json_data['channel_strip'] if 'channel_strip' in json_data else None)
		self.view = json_data['view'] if 'view' in json_data else {}
		self.clips = [serato_arrangement_clip(x) for x in json_data['clips']] if 'clips' in json_data else []
	def dump(self):
		out = {}
		out['type'] = self.type
		out['name'] = self.name
		out['channel_strip'] = self.channel_strip.dump()
		if self.view: out['view'] = self.view
		if self.clips: out['clips'] = [x.dump() for x in self.clips]
		return out

class serato_arrangement:
	def __init__(self, json_data):
		self.tracks = [serato_arrangement_track(x) for x in json_data['tracks']] if 'tracks' in json_data else []
		self.loop_start = json_data['loop_start'] if 'loop_start' in json_data else 0
		self.loop_end = json_data['loop_end'] if 'loop_end' in json_data else 0
		self.loop_active = json_data['loop_active'] if 'loop_active' in json_data else False
	def dump(self):
		out = {}
		out['tracks'] = [x.dump() for x in self.tracks]
		out['loop_start'] = self.loop_start
		out['loop_end'] = self.loop_end
		out['loop_active'] = self.loop_active
		return out

class serato_audio_deck:
	def __init__(self, json_data):
		self.original_key = json_data['original_key'] if 'original_key' in json_data else None
		self.tempo_map = json_data['tempo_map'] if 'tempo_map' in json_data else None
		self.sample_file = json_data['sample_file'] if 'sample_file' in json_data else None
		self.original_bpm = json_data['original_bpm'] if 'original_bpm' in json_data else None
		self.key_shift = json_data['key_shift'] if 'key_shift' in json_data else 0
		self.bpm = json_data['bpm'] if 'bpm' in json_data else None
		self.cues = json_data['cues'] if 'cues' in json_data else None
		self.slicer_cue_length = json_data['slicer_cue_length'] if 'slicer_cue_length' in json_data else 0
		self.audio_deck_color = json_data['audio_deck_color'] if 'audio_deck_color' in json_data else 0
		self.selected_cue_indices = json_data['selected_cue_indices'] if 'selected_cue_indices' in json_data else 0
	def dump(self):
		out = {}
		if self.original_key is not None: out['original_key'] = self.original_key
		if self.tempo_map is not None: out['tempo_map'] = self.tempo_map
		if self.sample_file is not None: out['sample_file'] = self.sample_file
		if self.original_bpm is not None: out['original_bpm'] = self.original_bpm
		if self.key_shift != 0: out['key_shift'] = self.key_shift
		if self.bpm is not None: out['bpm'] = self.bpm
		if self.slicer_cue_length != 0: out['slicer_cue_length'] = self.slicer_cue_length
		if self.cues is not None: out['cues'] = self.cues
		if self.audio_deck_color is not None: out['audio_deck_color'] = self.audio_deck_color
		if self.selected_cue_indices is not None: out['selected_cue_indices'] = self.selected_cue_indices
		return out

class serato_song:
	def __init__(self):
		self.version = 81
		self.metadata = {}
		self.bpm = 120.0
		self.key_root_note = 'C'
		self.key_type = 'major'
		self.transpose = 0
		self.play_focus_area = 'arrangement'
		self.audio_deck_color_collection = []
		self.scene_tab_colors = []
		self.scene_decks = []
		self.audio_decks = []

	def load_from_file(self, input_file):
		f = open(input_file, 'r')
		try: serato_json = json.load(f)
		except: raise ProjectFileParserException('serato: JSON Decoding Error')

		if 'version' in serato_json: self.version = serato_json['version']
		if 'metadata' in serato_json: self.metadata = serato_json['metadata']
		if 'transpose' in serato_json: self.transpose = serato_json['transpose']
		if 'bpm' in serato_json: self.bpm = serato_json['bpm']
		if 'key_root_note' in serato_json: self.key_root_note = serato_json['key_root_note']
		if 'key_type' in serato_json: self.key_type = serato_json['key_type']
		if 'play_focus_area' in serato_json: self.play_focus_area = serato_json['play_focus_area']
		if 'audio_deck_color_collection' in serato_json: self.audio_deck_color_collection = serato_json['audio_deck_color_collection']
		if 'scene_tab_colors' in serato_json: self.scene_tab_colors = serato_json['scene_tab_colors']
		if 'scene_decks' in serato_json: self.scene_decks = [serato_scene_deck(x) for x in serato_json['scene_decks']]
		if 'scenes' in serato_json: self.scenes = [serato_scene(x) for x in serato_json['scenes']]
		if 'arrangement' in serato_json: self.arrangement = serato_arrangement(serato_json['arrangement'])
		if 'audio_decks' in serato_json: self.audio_decks = [serato_audio_deck(x) for x in serato_json['audio_decks']]

		if DEBUG_IN_OUT:
			f = open('debug_in.json', 'w')
			f.write(json.dumps(serato_json, indent = 2))
	
			f = open('debug_out.json', 'w')
			f.write(json.dumps(self.dump(), indent = 2))
		return True

	def dump(self):
		out = {}
		out['version'] = self.version
		out['metadata'] = self.metadata
		if self.transpose: out['transpose'] = self.transpose
		out['bpm'] = self.bpm
		out['key_root_note'] = self.key_root_note
		out['key_type'] = self.key_type
		out['play_focus_area'] = self.play_focus_area
		if self.scene_tab_colors: out['scene_tab_colors'] = self.scene_tab_colors
		if self.audio_deck_color_collection: out['audio_deck_color_collection'] = self.audio_deck_color_collection
		out['scene_decks'] = [x.dump() for x in self.scene_decks]
		out['audio_decks'] = [x.dump() for x in self.audio_decks]
		out['scenes'] = [x.dump() for x in self.scenes]
		if self.arrangement: out['arrangement'] = self.arrangement.dump()
		return out
