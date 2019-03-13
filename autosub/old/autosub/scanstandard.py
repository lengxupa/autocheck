def scanstandard(outp2):
	ln=rdln(outp2)
	content=ln.split('Loop time of ',1)
	raw=content[1].strip().lstrip().rstrip(',').split(' on ',1)
	raw2=raw[1].strip().lstrip().rstrip(',').split(' procs for ',1)
	raw3=raw2[1].strip().lstrip().rstrip(',').split(' steps with ',1)
	return eval(raw[0]),eval(raw2[0]),eval(raw3[0])

