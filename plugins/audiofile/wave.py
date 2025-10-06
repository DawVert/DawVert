# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_soundfile(plugins.base):
	def is_dawvert_plugin(self):
		return 'audiofile'
	
	def get_shortname(self):
		return 'wave'
	
	def get_name(self):
		return 'Wave'
	
	def get_priority(self):
		return -100
	
	def get_prop(self, in_dict):
		in_dict['file_formats'] = ['wav']
	
	def getinfo(self, input_file, sampleref_obj, fileextlow):
		import soundfile
		import io
		from external.easybinrw import easybinrw
		from external.easybinrw import riff_chunks

		if fileextlow == 'wav':
			ebrw_readstr = easybinrw.binread()
			ebrw_readstr.load_file(input_file)
			riffchunks = riff_chunks.riff_chunk()
			riffchunks.read(ebrw_readstr, 0)

			data_pos = 0
			data_size = 0

			fmt_format = 0
			fmt_channels = 0
			fmt_rate = 0
			fmt_bytessec = 0
			fmt_datablocksize = 0
			fmt_bits = 0

			data_size = 0

			for riff_part in riffchunks.iter_reader(ebrw_readstr):
				if riff_part.name == b'fmt ': 
					fmt_format = ebrw_readstr.int_u16()
					fmt_channels = ebrw_readstr.int_u16()
					fmt_rate = ebrw_readstr.int_u32()
					fmt_bytessec = ebrw_readstr.int_u32()
					fmt_datablocksize = ebrw_readstr.int_u16()
					fmt_bits = ebrw_readstr.int_u16()
				elif riff_part.name == b'data': 
					data_pos = riff_part.start
					data_end = riff_part.end
					data_size = data_end-data_pos

			if fmt_format == 1: # PCM
				ebrw_readstr.seek(data_pos)
				audiodata = ebrw_readstr.raw(data_end-data_pos)
				if fmt_channels and fmt_bits and data_size:
					numsamples = data_size
					numsamples //= fmt_channels
					numsamples //= fmt_bits//8
					sampleref_obj.set_dur_samples(numsamples)
				sampleref_obj.set_hz(fmt_rate)
				sampleref_obj.set_channels(fmt_channels)
				sampleref_obj.set_fileformat('wav')
				return True

			elif fmt_format == 3: # IEEE float
				ebrw_readstr.seek(data_pos)
				audiodata = ebrw_readstr.raw(data_end-data_pos)
				if fmt_channels and fmt_bits and data_size:
					numsamples = data_size
					numsamples //= fmt_channels
					numsamples //= fmt_bits//8
					sampleref_obj.set_dur_samples(numsamples)
				sampleref_obj.set_hz(fmt_rate)
				sampleref_obj.set_channels(fmt_channels)
				sampleref_obj.set_fileformat('wav')
				return True
			return False
		return False