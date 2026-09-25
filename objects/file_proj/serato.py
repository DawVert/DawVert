# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from objects.exceptions import ProjectFileParserException

DEBUG_IN_OUT = False

class serato_sample:
	def __init__(self, indict=None):
		self.file = None
		self.reverse = None
		self.start = 0
		self.end = 1
		self.color = None
		self.polyphonic = None
		self.attack = None
		self.release = None
		self.pitch_shift = 0
		self.playback_speed = 1
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'file' in indict: self.file = indict['file']
		if 'reverse' in indict: self.reverse = indict['reverse']
		if 'start' in indict: self.start = indict['start']
		if 'end' in indict: self.end = indict['end']
		if 'color' in indict: self.color = indict['color']
		if 'polyphonic' in indict: self.polyphonic = indict['polyphonic']
		if 'attack' in indict: self.attack = indict['attack']
		if 'release' in indict: self.release = indict['release']
		if 'pitch_shift' in indict: self.pitch_shift = indict['pitch_shift']
		if 'playback_speed' in indict: self.playback_speed = indict['playback_speed']

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
	def __init__(self, indict=None):
		self.used = False
		self.sample = None
		self.channel_strip = serato_channel_strip()
		if indict is not None: self.read(indict)

	def read(self, indict):
		self.used = True
		if 'sample' in indict: self.sample = serato_sample(indict['sample'])
		if 'channel_strip' in indict: self.channel_strip = serato_channel_strip(indict['channel_strip'])

	def dump(self):
		if self.used:
			out = {}
			out['sample'] = self.sample.dump()
			if self.channel_strip.used: out['channel_strip'] = self.channel_strip.dump()
			return out

class serato_channel_strip:
	def __init__(self, indict=None):
		self.used = False
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
		if indict is not None: self.read(indict)

	def read(self, indict):
		self.used = True
		if 'post_fader_effects' in indict: self.post_fader_effects = indict['post_fader_effects']
		if 'volume' in indict: self.volume = indict['volume']
		if 'high_eq' in indict: self.high_eq = indict['high_eq']
		if 'mid_eq' in indict: self.mid_eq = indict['mid_eq']
		if 'low_eq' in indict: self.low_eq = indict['low_eq']
		if 'pan' in indict: self.pan = indict['pan']
		if 'gain' in indict: self.gain = indict['gain']
		if 'filter' in indict: self.filter = indict['filter']
		if 'mute' in indict: self.mute = indict['mute']
		if 'post_fader_effects_beats' in indict: self.post_fader_effects_beats = indict['post_fader_effects_beats']

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
	def __init__(self, indict=None):
		self.type = ''
		self.name = ''
		self.content_name = ''
		self.groove_amount = 0.0
		self.channel_strip = serato_channel_strip()
		self.drums = None
		self.make_sequence_genre = None
		self.view = None
		self.deck_source_properties_changed = None
		self.zoom = None
		self.original_key = None
		self.tempo_map = None
		self.sample_file = None
		self.original_bpm = None
		self.sample_regions = None
		self.bpm = None
		self.cues = None
		self.momentary = True
		self.attack = None
		self.release = None
		self.instrument_file = None
		self.polyphony = None
		self.sequence_view = None
		self.bar_mode_enabled = True
		self.playback_speed = 1
		self.key_shift = 0
		self.plugin_description = None
		self.state = None
		self.parameters = None
		self.glide_mode = None
		self.glide_duration = None
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'type' in indict: self.type = indict['type']
		if 'name' in indict: self.name = indict['name']
		if 'content_name' in indict: self.content_name = indict['content_name']
		if 'groove_amount' in indict: self.groove_amount = indict['groove_amount']
		if 'channel_strip' in indict: self.channel_strip = serato_channel_strip(indict['channel_strip'])
		if 'drums' in indict: self.drums = [serato_drum(x) for x in indict['drums']]
		if 'make_sequence_genre' in indict: self.make_sequence_genre = indict['make_sequence_genre']
		if 'view' in indict: self.view = indict['view']
		if 'deck_source_properties_changed' in indict: self.deck_source_properties_changed = indict['deck_source_properties_changed']
		if 'zoom' in indict: self.zoom = indict['zoom']
		if 'original_key' in indict: self.original_key = indict['original_key']
		if 'tempo_map' in indict: self.tempo_map = indict['tempo_map']
		if 'sample_file' in indict: self.sample_file = indict['sample_file']
		if 'original_bpm' in indict: self.original_bpm = indict['original_bpm']
		if 'sample_regions' in indict: self.sample_regions = indict['sample_regions']
		if 'bpm' in indict: self.bpm = indict['bpm']
		if 'cues' in indict: self.cues = indict['cues']
		if 'momentary' in indict: self.momentary = indict['momentary']
		if 'attack' in indict: self.attack = indict['attack']
		if 'release' in indict: self.release = indict['release']
		if 'instrument_file' in indict: self.instrument_file = indict['instrument_file']
		if 'polyphony' in indict: self.polyphony = indict['polyphony']
		if 'sequence_view' in indict: self.sequence_view = indict['sequence_view']
		if 'bar_mode_enabled' in indict: self.bar_mode_enabled = indict['bar_mode_enabled']
		if 'playback_speed' in indict: self.playback_speed = indict['playback_speed']
		if 'key_shift' in indict: self.key_shift = indict['key_shift']
		if 'plugin_description' in indict: self.plugin_description = indict['plugin_description']
		if 'state' in indict: self.state = indict['state']
		if 'parameters' in indict: self.parameters = indict['parameters']
		if 'glide_mode' in indict: self.glide_mode = indict['glide_mode']
		if 'glide_duration' in indict: self.glide_duration = indict['glide_duration']

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
	def __init__(self, indict=None):
		self.start = 0
		self.duration = 0
		self.channel = 0
		self.number = 0
		self.velocity = None
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'start' in indict: self.start = indict['start']
		if 'duration' in indict: self.duration = indict['duration']
		if 'channel' in indict: self.channel = indict['channel']
		if 'number' in indict: self.number = indict['number']
		if 'velocity' in indict: self.velocity = indict['velocity']

	def dump(self):
		out = {}
		out['start'] = self.start
		out['duration'] = self.duration
		if self.channel: out['channel'] = self.channel
		out['number'] = self.number
		if self.velocity is not None: out['velocity'] = self.velocity
		return out

class serato_auto_keyframe:
	def __init__(self, indict=None):
		self.time = 0
		self.value = 0
		self.interpolation = None
		self.curvature = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'time' in indict: self.time = indict['time']
		if 'value' in indict: self.value = indict['value']
		if 'interpolation' in indict: self.interpolation = indict['interpolation']
		if 'curvature' in indict: self.curvature = indict['curvature']

	def dump(self):
		out = {}
		out['time'] = self.time
		out['value'] = self.value
		if self.interpolation: out['interpolation'] = self.interpolation
		if self.curvature: out['curvature'] = self.curvature
		return out

class serato_automation_curve:
	def __init__(self, indict=None):
		self.type = None
		self.parameter = None
		self.keyframes = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'type' in indict: self.type = indict['type']
		if 'parameter' in indict: self.parameter = indict['parameter']
		if 'keyframes' in indict: self.keyframes = [serato_auto_keyframe(x) for x in indict['keyframes']]

	def dump(self):
		out = {}
		out['type'] = self.type
		out['parameter'] = self.parameter
		out['keyframes'] = [x.dump() for x in self.keyframes]
		return out

class serato_deck_sequence:
	def __init__(self, indict=None):
		self.notes = []
		self.secondary_notes = []
		self.automation_curves = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'notes' in indict: self.notes = [serato_note(x) for x in indict['notes']]
		if 'secondary_notes' in indict: self.secondary_notes = [serato_note(x) for x in indict['secondary_notes']]
		if 'automation_curves' in indict: self.automation_curves = [serato_automation_curve(x) for x in indict['automation_curves']]

	def dump(self):
		out = {}
		if self.notes: out['notes'] = [x.dump() for x in self.notes]
		if self.secondary_notes: out['secondary_notes'] = [x.dump() for x in self.secondary_notes]
		if self.automation_curves: out['automation_curves'] = [x.dump() for x in self.automation_curves]
		return out

class serato_scene:
	def __init__(self, indict=None):
		self.name = None
		self.length = None
		self.deck_sequences = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'name' in indict: self.name = indict['name']
		if 'length' in indict: self.length = indict['length']
		if 'deck_sequences' in indict: self.deck_sequences = [serato_deck_sequence(x) for x in indict['deck_sequences']]

	def dump(self):
		out = {}
		out['name'] = self.name
		out['length'] = self.length
		out['deck_sequences'] = [x.dump() for x in self.deck_sequences]
		return out

class serato_arrangement_clip:
	def __init__(self, indict=None):
		self.start = 0
		self.length = None
		self.scene_slot_number = None
		self.audio_deck_index = None
		self.track_sample = None
		if indict is not None: self.read(indict)

	def read(self, indict):
		self.start = indict['start']
		if 'length' in indict: self.length = indict['length']
		if 'scene_slot_number' in indict: self.scene_slot_number = indict['scene_slot_number']
		if 'audio_deck_index' in indict: self.audio_deck_index = indict['audio_deck_index']
		if 'track_sample' in indict: self.track_sample = indict['track_sample']

	def dump(self):
		out = {}
		out['start'] = self.start
		out['length'] = self.length
		out['scene_slot_number'] = self.scene_slot_number
		if self.audio_deck_index is not None: out['audio_deck_index'] = self.audio_deck_index
		if self.track_sample is not None: out['track_sample'] = self.track_sample
		return out

class serato_arrangement_track:
	def __init__(self, indict=None):
		self.type = None
		self.name = None
		self.channel_strip = serato_channel_strip()
		self.view = None
		self.clips = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		self.type = indict['type']
		self.name = indict['name']
		if 'channel_strip' in indict: self.channel_strip = serato_channel_strip(indict['channel_strip'])
		if 'view' in indict: self.view = indict['view'] 
		if 'clips' in indict: self.clips = [serato_arrangement_clip(x) for x in indict['clips']]

	def dump(self):
		out = {}
		out['type'] = self.type
		out['name'] = self.name
		out['channel_strip'] = self.channel_strip.dump()
		if self.view: out['view'] = self.view
		if self.clips: out['clips'] = [x.dump() for x in self.clips]
		return out

class serato_arrangement:
	def __init__(self, indict=None):
		self.tracks = []
		self.loop_start = 0
		self.loop_end = 0
		self.loop_active = False
		if indict is not None: self.read(indict)

	def read(self, indict):
		 if 'tracks' in indict: self.tracks = [serato_arrangement_track(x) for x in indict['tracks']]
		 if 'loop_start' in indict: self.loop_start = indict['loop_start']
		 if 'loop_end' in indict: self.loop_end = indict['loop_end']
		 if 'loop_active' in indict: self.loop_active = indict['loop_active']

	def dump(self):
		out = {}
		out['tracks'] = [x.dump() for x in self.tracks]
		out['loop_start'] = self.loop_start
		out['loop_end'] = self.loop_end
		out['loop_active'] = self.loop_active
		return out

class serato_audio_deck:
	def __init__(self, indict=None):
		self.original_key = None
		self.tempo_map = None
		self.sample_file = None
		self.original_bpm = None
		self.key_shift = 0
		self.bpm = None
		self.cues = None
		self.slicer_cue_length = 0
		self.audio_deck_color = 0
		self.selected_cue_indices = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		 if 'original_key' in indict: self.original_key = indict['original_key']
		 if 'tempo_map' in indict: self.tempo_map = indict['tempo_map']
		 if 'sample_file' in indict: self.sample_file = indict['sample_file']
		 if 'original_bpm' in indict: self.original_bpm = indict['original_bpm']
		 if 'key_shift' in indict: self.key_shift = indict['key_shift']
		 if 'bpm' in indict: self.bpm = indict['bpm']
		 if 'cues' in indict: self.cues = indict['cues']
		 if 'slicer_cue_length' in indict: self.slicer_cue_length = indict['slicer_cue_length']
		 if 'audio_deck_color' in indict: self.audio_deck_color = indict['audio_deck_color']
		 if 'selected_cue_indices' in indict: self.selected_cue_indices = indict['selected_cue_indices']

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
