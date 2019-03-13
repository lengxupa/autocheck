def rdin(i):
	read_restart=''
	rsto=-1
	rstt=-1
	rsti=-1
	rstfile=''
	datafile=''
	thermo=-1
	every=1
	delay=0
	check='no'
	timestep=1
	Tstart=0
	Tend=0
	speciesfile=''
	bondfile=''
	deformscale=1
	src = file(i, "r+")
	for line in src.readlines():
		ln=rdln(line)
		if(ln):
			if(not(ln.find('read_restart'))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				read_restart=raw[0]
				raw2=raw[0].split('.')
				rsto=eval(raw2[raw2.index('rst')-1])
			if(not(ln.find('read_data'))):
				rsto=0
			if(not(ln.find('reset_timestep'))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				rsto=eval(raw[0])
			if(not(line.strip().lstrip().rstrip(',').find('write_data'))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				datafile=raw[0]
			if(not(ln.find('thermo '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				thermo=eval(raw[0])
			if(not(ln.find('neigh_modify'))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').find('every')
				if(not(raw==-1)):
					raw2=content[1].strip().lstrip().rstrip(',').split('every',1)
					raw3=raw2[1].strip().lstrip().rstrip(',').split(' ',1)
					every=eval(raw3[0])
				raw=content[1].strip().lstrip().rstrip(',').find('delay')
				if(not(raw==-1)):
					raw2=content[1].strip().lstrip().rstrip(',').split('delay',1)
					raw3=raw2[1].strip().lstrip().rstrip(',').split(' ',1)
					delay=eval(raw3[0])
				raw=content[1].strip().lstrip().rstrip(',').find('check')
				if(not(raw==-1)):
					raw2=content[1].strip().lstrip().rstrip(',').split('check',1)
					raw3=raw2[1].strip().lstrip().rstrip(',').split(' ',1)
					check=raw3[0]
			if(not(ln.find('timestep '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				timestep=eval(raw[0])
			if(not(ln.find('fix '))):
				if(not(ln.find('temp ')==-1)):
					content=ln.split('temp ',1)
					raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
					Tstart=eval(raw[0])
					raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
					Tend=eval(raw2[0])
				if(not(ln.find('reax/c/species ')==-1)):
					content=ln.split('reax/c/species ',1)
					raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
					raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
					every=eval(raw2[0])
					delay=0
					raw3=raw2[1].strip().lstrip().rstrip(',').split(' ',1)
					raw4=raw3[1].strip().lstrip().rstrip(',').split(' ',1)
					speciesfile=raw4[0]
				if(not(ln.find('reax/c/bonds ')==-1)):
					content=ln.split('reax/c/bonds ',1)
					raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
					raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
					bondfile=raw2[0]
				if(not(ln.find('deform ')==-1)):
					if(not(ln.find('scale ')==-1)):
						content=ln.split('scale ',1)
						raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
						deformscale=eval(raw[0])
			if(not(ln.find('restart '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				rsti=eval(raw[0])
				raw2=raw[1].strip().lstrip().rstrip(',').split('.',1)
				rstfile=raw2[0]
			if(not(ln.find('run '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				rstt=eval(raw[0])+rsto
	src.close()
	return read_restart,rsto,rstt,rsti,rstfile,datafile,thermo,every,delay,check,timestep,Tstart,Tend,speciesfile,bondfile,deformscale

