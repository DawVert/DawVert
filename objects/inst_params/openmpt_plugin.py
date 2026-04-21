
#datadef = dv_datadef.datadef('./data_main/datadef/openmpt.ddef')
#dataset = dv_dataset.dataset('./data/datapack/app/openmpt.xml')
#from functions_plugin_ext import plugin_vst2

class openmpt_plugin:
	def __init__(self):
		self.type = None
		self.id = None
		self.route = None
		self.mix = None
		self.gain = None
		self.output_routing = None
		self.name = None
		self.libname = None
		self.data = None
		self.params = None

	def read(self, ebrw_readstr):
		self.type = ebrw_readstr.raw(4)
		self.id = ebrw_readstr.int_u32()
		self.route = ebrw_readstr.int_u8()
		self.mix = ebrw_readstr.int_u8()
		self.gain = ebrw_readstr.int_u8()
		ebrw_readstr.skip(1)
		self.output_routing = ebrw_readstr.int_u32()
		ebrw_readstr.skip(16)
		self.name = ebrw_readstr.string(32, encoding="windows-1252")
		self.libname = ebrw_readstr.string(64, encoding="windows-1252")

		datalen = ebrw_readstr.int_u32()
		if self.type == b'DBM0':
			ebrw_readstr.skip(4)
			self.params = ebrw_readstr.list_int_u8(datalen-4)
		elif self.type == b'SymM':
			ebrw_readstr.skip(4)
			self.params = ebrw_readstr.list_int_u8(datalen-4)
		else:
			self.data = ebrw_readstr.raw(datalen)

	def to_cvpj(self, fxnum, convproj_obj):
		pluginid = 'FX'+str(fxnum)
		if self.type == b'OMXD':
			plugin_obj = convproj_obj.plugin__add(pluginid, 'external', 'directx', self.libname)
			plugin_obj.from_bytes(self.data, 'directx', 'directx', 'plugin', self.libname.lower(), None)
		#elif self.type == b'PtsV':
		#	plugin_obj = convproj_obj.plugin__add(pluginid, 'external', 'vst2', None)
		#	plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', self.id, 'chunk', self.data, 0)
		elif self.type == b'DBM0':
			plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'digibooster', 'pro_echo')
			plugin_obj.params.add('delay', self.params[0], 'int')
			plugin_obj.params.add('fb', self.params[1], 'int')
			plugin_obj.params.add('wet', self.params[2], 'int')
			plugin_obj.params.add('cross_echo', self.params[3], 'int')
		elif self.type == b'SymM':
			plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'symmod', 'echo')
			plugin_obj.params.add('type', self.params[0], 'int')
			plugin_obj.params.add('delay', self.params[1], 'int')
			plugin_obj.params.add('fb', self.params[2], 'int')
		if plugin_obj and self.name:
			if self.name: plugin_obj.visual.name = self.name
