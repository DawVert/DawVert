
		#if FL_OUTPUT_MODE == 25: 
		#	tlv_write_std(FLdt__ebrw_writestr, 199, '25.1.5.4976'.encode('utf8') + b'\x00')
		#	tlv_write_std(FLdt__ebrw_writestr, 159, 4976)
		#if FL_OUTPUT_MODE == 21: 
		#	tlv_write_std(FLdt__ebrw_writestr, 199, '21.0.3.3517'.encode('utf8') + b'\x00')
		#	tlv_write_std(FLdt__ebrw_writestr, 159, 3517)
		#if FL_OUTPUT_MODE == 20: 
		#	tlv_write_std(FLdt__ebrw_writestr, 199, '20.7.2.1852'.encode('utf8') + b'\x00')
		#	tlv_write_std(FLdt__ebrw_writestr, 159, 1852)
		#if FL_OUTPUT_MODE == 12: tlv_write_std(FLdt__ebrw_writestr, 199, '12.3.0.72'.encode('utf8') + b'\x00')
		#tlv_write_std(FLdt__ebrw_writestr, 28, 1)
		#if FL_OUTPUT_MODE >= 20: tlv_write_std(FLdt__ebrw_writestr, 37, 1)
		#tlv_write_std(FLdt__ebrw_writestr, 200, b'\x00\x00')
		#tlv_write_std(FLdt__ebrw_writestr, 156, int(self.tempo)*1000)
		#tlv_write_std(FLdt__ebrw_writestr, 67, self.nonsong_patnum)
		#tlv_write_std(FLdt__ebrw_writestr, 9, self.loop_active)
		#tlv_write_std(FLdt__ebrw_writestr, 11, self.shuffle)
		#tlv_write_std(FLdt__ebrw_writestr, 80, self.mainpitch)
		#tlv_write_std(FLdt__ebrw_writestr, 17, self.numerator)
		#tlv_write_std(FLdt__ebrw_writestr, 18, self.denominator)
		#if FL_OUTPUT_MODE >= 20: tlv_write_std(FLdt__ebrw_writestr, 35, 1)
		#tlv_write_std(FLdt__ebrw_writestr, 23, self.panning_law)
		#if FL_OUTPUT_MODE >= 21: tlv_write_std(FLdt__ebrw_writestr, 44, 0)
		#tlv_write_std(FLdt__ebrw_writestr, 30, self.truncate_clip_notes)
		#tlv_write_std(FLdt__ebrw_writestr, 10, self.showinfo)
		#tlv_write_std(FLdt__ebrw_writestr, 194, utf16encode(self.title))
		#tlv_write_std(FLdt__ebrw_writestr, 206, utf16encode(self.genre))
		#tlv_write_std(FLdt__ebrw_writestr, 207, utf16encode(self.author))
		#if FL_OUTPUT_MODE >= 25: tlv_write_std(FLdt__ebrw_writestr, 167, 0)
		#tlv_write_std(FLdt__ebrw_writestr, 202, utf16encode(self.projectdatapath))
		#tlv_write_std(FLdt__ebrw_writestr, 195, utf16encode(self.comment))
		#tlv_write_std(FLdt__ebrw_writestr, 237, b'\0'*16)
		#tlv_write_std(FLdt__ebrw_writestr, 231, utf16encode('Unsorted'))
		#if self.url: tlv_write_std(FLdt__ebrw_writestr, 197, utf16encode(self.url))
		#tlv_write_std(FLdt__ebrw_writestr, 146, 0)
		#if FL_OUTPUT_MODE >= 20: tlv_write_std(FLdt__ebrw_writestr, 216, self.startvals.write())
#
		#for patnum, patdat in self.patterns.items():
		#	if patdat.automation or patdat.notes or patdat.color or (patdat.name != None):
		#		tlv_write_std(FLdt__ebrw_writestr, 65, patnum)
		#		if patdat.automation:
		#			autobytes = b''
		#			#for pos, autov, val in patdat.automation: autobytes += struct.pack('III', pos, autov, val)
		#			#tlv_write_std(FLdt__ebrw_writestr, 223, autobytes)
		#		if patdat.notes:
		#			flnotes = b''
		#			for fln in patdat.notes: 
		#				if fln.pos >= 0 and fln.key>=0:
		#					flnotes += struct.pack('IHHIHHBBBBBBBB', fln.pos,fln.flags,fln.rack,fln.dur,fln.key,fln.group,fln.finep,fln.u1,fln.rel,fln.midich,fln.pan,fln.velocity,fln.mod_x,fln.mod_y)
		#			tlv_write_std(FLdt__ebrw_writestr, 224, flnotes)
		#		if patdat.color != None: tlv_write_std(FLdt__ebrw_writestr, 150, patdat.color)
		#		if patdat.name != None: tlv_write_std(FLdt__ebrw_writestr, 193, utf16encode(patdat.name))
#
		#		for timem_obj in patdat.timemarkers:
		#			tlv_write_std(FLdt__ebrw_writestr, 148, (timem_obj.type << 24)+timem_obj.pos)
		#			tlv_write_std(FLdt__ebrw_writestr, 33, timem_obj.numerator)
		#			tlv_write_std(FLdt__ebrw_writestr, 34, timem_obj.denominator)
		#			if timem_obj.name != None: tlv_write_std(FLdt__ebrw_writestr, 205, utf16encode(timem_obj.name))
		#			else: tlv_write_std(FLdt__ebrw_writestr, 205, b'\x20\x00\x00\x00')
#
		#tlv_write_std(FLdt__ebrw_writestr, 226, b'\x01\x00\x00\x00\x00\x00\x00\x00\x01\x90\xff\x0f\x04\x00\x00\x00\xd5\x01\x00\x00')
		#tlv_write_std(FLdt__ebrw_writestr, 226, b'\xfd\x00\x00\x00\x00\x00\x00\x00\x80\x90\xff\x0f\x04\x00\x00\x00\xd5\x01\x00\x00')
		#tlv_write_std(FLdt__ebrw_writestr, 226, b'\xff\x00\x00\x00\xff\x00\x00\x00\x04\x00\xff\x0f\x04\x00\x00\x00\x00\xfe\xff\xff')
#
		#for _, m in self.remote_assoc.items():
		#	for remotectrl in m:
		#		bytes_remote, isvalid = remotectrl.write()
		#		if isvalid: 
		#			tlv_write_std(FLdt__ebrw_writestr, 227, bytes_remote)
		#			if remotectrl.formula:
		#				tlv_write_std(FLdt__ebrw_writestr, 230, utf16encode(remotectrl.formula))
#
		#for chnum, chdat in self.channels.items():
		#	tlv_write_std(FLdt__ebrw_writestr, 64, chnum)
		#	tlv_write_std(FLdt__ebrw_writestr, 21, chdat.type)
		#	if FL_OUTPUT_MODE == 12: 
		#		if chdat.type in [0,4]:
		#			tlv_write_std(FLdt__ebrw_writestr, 201, utf16encode(''))
		#			tlv_write_std(FLdt__ebrw_writestr, 212, chdat.plugin.write())
#
		#	if chdat.type == 2:
		#		if chdat.plugin.plugname != None: tlv_write_std(FLdt__ebrw_writestr, 201, utf16encode(chdat.plugin.plugname))
		#		tlv_write_std(FLdt__ebrw_writestr, 212, chdat.plugin.write())
		#	if chdat.name != None: tlv_write_std(FLdt__ebrw_writestr, 203, utf16encode(chdat.name))
		#	if chdat.icon != None: tlv_write_std(FLdt__ebrw_writestr, 155, chdat.icon)
		#	if chdat.color != None: tlv_write_std(FLdt__ebrw_writestr, 128, chdat.color)
		#	tlv_write_std(FLdt__ebrw_writestr, 41, 0)
		#	if chdat.plugin.params != None: tlv_write_std(FLdt__ebrw_writestr, 213, chdat.plugin.params)
#
		#	tlv_write_std(FLdt__ebrw_writestr, 0, chdat.enabled)
		#	tlv_write_std(FLdt__ebrw_writestr, 209, chdat.delay.write())
		#	tlv_write_std(FLdt__ebrw_writestr, 138, chdat.delayreso)
		#	tlv_write_std(FLdt__ebrw_writestr, 139, chdat.reverb)
		#	tlv_write_std(FLdt__ebrw_writestr, 89, chdat.shiftdelay)
		#	tlv_write_std(FLdt__ebrw_writestr, 97, 128)
		#	tlv_write_std(FLdt__ebrw_writestr, 69, chdat.fx)
		#	tlv_write_std(FLdt__ebrw_writestr, 86, chdat.fx3)
		#	tlv_write_std(FLdt__ebrw_writestr, 71, chdat.cutoff)
		#	tlv_write_std(FLdt__ebrw_writestr, 83, chdat.resonance)
		#	tlv_write_std(FLdt__ebrw_writestr, 74, chdat.preamp)
		#	tlv_write_std(FLdt__ebrw_writestr, 75, chdat.decay)
		#	tlv_write_std(FLdt__ebrw_writestr, 76, chdat.attack)
		#	tlv_write_std(FLdt__ebrw_writestr, 85, chdat.stdel)
		#	tlv_write_std(FLdt__ebrw_writestr, 131, chdat.fxsine)
		#	tlv_write_std(FLdt__ebrw_writestr, 70, chdat.fxflags)
		#	tlv_write_std(FLdt__ebrw_writestr, 22, chdat.fxchannel)
		#	for layer_chan in chdat.layer_chans: tlv_write_std(FLdt__ebrw_writestr, 94, layer_chan)
		#	tlv_write_std(FLdt__ebrw_writestr, 219, chdat.basicparams.write())
		#	tlv_write_std(FLdt__ebrw_writestr, 229, chdat.ofslevels)
		#	tlv_write_std(FLdt__ebrw_writestr, 221, chdat.poly.write())
		#	tlv_write_std(FLdt__ebrw_writestr, 215, chdat.params.write(FL_OUTPUT_MODE))
		#	tlv_write_std(FLdt__ebrw_writestr, 132, chdat.cutcutby)
		#	tlv_write_std(FLdt__ebrw_writestr, 144, chdat.layerflags)
		#	tlv_write_std(FLdt__ebrw_writestr, 145, 0)
		#	tlv_write_std(FLdt__ebrw_writestr, 32, 0)
		#	for trking_obj in chdat.tracking: tlv_write_std(FLdt__ebrw_writestr, 228, trking_obj.write())
		#	for env_lfo_obj in chdat.env_lfo: tlv_write_std(FLdt__ebrw_writestr, 218, env_lfo_obj.write())
		#	tlv_write_std(FLdt__ebrw_writestr, 143, chdat.sampleflags)
		#	tlv_write_std(FLdt__ebrw_writestr, 20, chdat.looptype)
#
		#	if chdat.samplefilename: tlv_write_std(FLdt__ebrw_writestr, 196, utf16encode(chdat.samplefilename))
		#	if chdat.middlenote != 60: tlv_write_std(FLdt__ebrw_writestr, 135, chdat.middlenote)
#
		#for arrnum, arrdat in self.arrangements.items():
		#	if FL_OUTPUT_MODE >= 20:
		#		tlv_write_std(FLdt__ebrw_writestr, 99, arrnum)
		#		if arrdat.name != None: tlv_write_std(FLdt__ebrw_writestr, 241, utf16encode(arrdat.name))
		#	arr_bytes = b''
		#	for item in arrdat.items: arr_bytes += item.write(FL_OUTPUT_MODE, num_tracks)
#
		#	if FL_OUTPUT_MODE >= 20:
		#		tlv_write_std(FLdt__ebrw_writestr, 36, 0)
		#	tlv_write_std(FLdt__ebrw_writestr, 233, arr_bytes) #PlayListItems
		#	for track_num, track_obj in arrdat.tracks.items():
		#		if track_num<=num_tracks:
		#			tlv_write_std(FLdt__ebrw_writestr, 238, track_obj.write(FL_OUTPUT_MODE))
		#			if track_obj.name: tlv_write_std(FLdt__ebrw_writestr, 239, utf16encode(track_obj.name))
		#			if FL_OUTPUT_MODE >= 21: 
		#				tlv_write_std(FLdt__ebrw_writestr, 43, 0)
#
		#	for timem_obj in arrdat.timemarkers:
		#		tlv_write_std(FLdt__ebrw_writestr, 148, (timem_obj.type << 24)+int(timem_obj.pos))
		#		tlv_write_std(FLdt__ebrw_writestr, 33, timem_obj.numerator)
		#		tlv_write_std(FLdt__ebrw_writestr, 34, timem_obj.denominator)
		#		if timem_obj.name != None: tlv_write_std(FLdt__ebrw_writestr, 205, utf16encode(timem_obj.name))
		#		else: tlv_write_std(FLdt__ebrw_writestr, 205, b'\x20\x00\x00\x00')
		#	if FL_OUTPUT_MODE < 20: break
#
		#	#make_trackinfo(data_FLdt, arrangements[arrangement]['tracks'])
		#if FL_OUTPUT_MODE >= 20: tlv_write_std(FLdt__ebrw_writestr, 100, 0)
		#tlv_write_std(FLdt__ebrw_writestr, 29, 1)
		#if FL_OUTPUT_MODE >= 20: tlv_write_std(FLdt__ebrw_writestr, 39, 1)
		#if FL_OUTPUT_MODE >= 21: tlv_write_std(FLdt__ebrw_writestr, 40, 0)
		#tlv_write_std(FLdt__ebrw_writestr, 31, 0)
		#if FL_OUTPUT_MODE >= 20: tlv_write_std(FLdt__ebrw_writestr, 38, 1)
		#if FL_OUTPUT_MODE >= 21: tlv_write_std(FLdt__ebrw_writestr, 42, 0)
#
		#for mixernum, mixerdat in self.mixer.items():
		#	if mixernum<=num_fx:
		#		#print(mixernum, mixerdat)
		#		tlv_write_std(FLdt__ebrw_writestr, 236, mixerdat.write(FL_OUTPUT_MODE))
		#		if mixerdat.color != None: tlv_write_std(FLdt__ebrw_writestr, 149, mixerdat.color)
		#		if mixerdat.name != None: tlv_write_std(FLdt__ebrw_writestr, 204, utf16encode(mixerdat.name))
		#		if mixerdat.icon != None: tlv_write_std(FLdt__ebrw_writestr, 95, mixerdat.icon)
		#		for slotnum, slotdata in enumerate(mixerdat.slots):
		#			if slotdata:
		#				if slotdata.used:
		#					if slotdata.plugin.plugname != None: tlv_write_std(FLdt__ebrw_writestr, 201, utf16encode(slotdata.plugin.plugname))
		#					tlv_write_std(FLdt__ebrw_writestr, 212, slotdata.plugin.write())
		#					if slotdata.name != None: tlv_write_std(FLdt__ebrw_writestr, 203, utf16encode(slotdata.name))
		#					if slotdata.icon != None: tlv_write_std(FLdt__ebrw_writestr, 155, slotdata.icon)
		#					if slotdata.color != None: tlv_write_std(FLdt__ebrw_writestr, 128, slotdata.color)
		#					tlv_write_std(FLdt__ebrw_writestr, 41, 0)
		#					if slotdata.plugin.params != None: tlv_write_std(FLdt__ebrw_writestr, 213, slotdata.plugin.params)
		#			tlv_write_std(FLdt__ebrw_writestr, 98, slotnum)
		#		fxrouting_fl = [0 for _ in range(num_fx_routing)]
		#		for route in mixerdat.routing: 
		#			if route<len(fxrouting_fl):
		#				fxrouting_fl[route] = 1
		#		tlv_write_std(FLdt__ebrw_writestr, 235, bytearray(fxrouting_fl))
		#		if FL_OUTPUT_MODE >= 21: 
		#			tlv_write_std(FLdt__ebrw_writestr, 165, 3)
		#			tlv_write_std(FLdt__ebrw_writestr, 166, 1)
		#		tlv_write_std(FLdt__ebrw_writestr, 154, mixerdat.inchannum)
		#		tlv_write_std(FLdt__ebrw_writestr, 147, mixerdat.outchannum)
		#		if FL_OUTPUT_MODE >= 21: 
		#			tlv_write_std(FLdt__ebrw_writestr, 42, 0)
#
		#tlv_write_std(FLdt__ebrw_writestr, 225, self.initfxvals.write())
		#tlv_write_std(FLdt__ebrw_writestr, 133, 216)