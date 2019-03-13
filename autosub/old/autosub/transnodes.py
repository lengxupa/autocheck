def transnodes(ppno):
	if(not(ppno%16)):
		nodes=ppno/16
		ppn=16
	else:
		nodes=ppno/16+1
		if(nodes>1):
			ppn=16
		else:
			ppn=ppno
	return ("nodes=%d:ppn=%d" %(nodes,ppn))

