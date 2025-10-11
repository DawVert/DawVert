# https://github.com/juce-framework/JUCE/blob/master/modules/juce_audio_processors/format_types/juce_VST3PluginFormat.cpp

import uuid
import numpy
import struct

def getHashForRange(xinput):
    value = 0
    for item in xinput:
        value = (value * 31) + int(item)
    return value&0xffffffff

def vst3_make_uniqueid(vstid):
	value2_u = uuid.UUID(bytes=bytes.fromhex(vstid))
	value2_a = numpy.frombuffer(value2_u.bytes, '>I')
	o = getHashForRange(value2_a)
	o = struct.pack('<I', o)
	return struct.unpack('<i', o)[0]