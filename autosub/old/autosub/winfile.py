def winfile(infile,read_restart,rsto,rstt,rsti,rstfile,datafile,thermo,every,delay,check,timestep,Tstart,Tend,deformscale):
	os.system("cp %s temp2.txt" %infile)
	src = file('temp2.txt', "r+")
	for line in src.readlines():
		ln=rdln(line)
		if(line.strip().lstrip().rstrip(',').find('write_data')!=-1):
			if(line.strip().lstrip().rstrip(',').find(datafile)!=-1):
				if(not(line.strip().lstrip().rstrip(',').find('write_data'))):
					if(rstt!=rsteo):
						rplcfl(infile,line,'#%s' %line)
				else:
					if(rstt==rsteo):
						rplcfl(infile,line,'write_data %s \n' %datafile)
			else:
				rplcfl(infile,line,'#%s' %line)
		if(line.strip().lstrip().rstrip(',').find('read_restart')!=-1):
			if(read_restart):
						rplcfl(infile,line,'read_restart %s \n' %read_restart)
		if(ln):			
			if(not(ln.find('read_data'))):
				if(read_restart):
					rplcfl(infile,line,'#%s' %line)
			if(not(ln.find('reset_timestep'))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				if(rstr!=eval(raw[0])):
					rplcfl(infile,line,'reset_timestep %d \n' %rstr)
			if(not(ln.find('thermo '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				if(thermo!=eval(raw[0])):
					rplcfl(infile,line,'thermo %d \n' %thermo)
			if(not(ln.find('neigh_modify'))):
				rplcfl(infile,line,'neigh_modify every %d delay %d check %s \n' %(every,delay,check))
			if(not(ln.find('fix '))):
				if(not(ln.find('temp ')==-1)):
					content=ln.split('temp ',1)
					raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
					raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
					if(Tstart!=eval(raw[0]) or Tend!=eval(raw2[0])):
						rplcfl(infile,line,'%stemp %f %f %s \n' %(content[0],Tstart,Tend,raw2[1]))
				if(not(ln.find('reax/c/species ')==-1)):
					content=ln.split('reax/c/species ',1)
					raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
					raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
					if(every!=eval(raw2[0])):
						rplcfl(infile,line,'%sreax/c/species %s %d %s \n' %(content[0],raw[0],every,raw2[1]))
				if(not(ln.find('deform ')==-1)):
					if(not(ln.find('scale ')==-1)):
						content=ln.split('scale ',1)
						raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
						if(deformscale!=eval(raw[0])):
							rplcfl(infile,line,'%sscale %d %s \n' %(content[0],deformscale,raw[1]))
			if(not(ln.find('restart '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				raw2=raw[1].strip().lstrip().rstrip(',').split('.',1)
				if(rsti!=eval(raw[0]) and rstfile==raw2[0]):
					rplcfl(infile,line,'restart %d %s.*.rst \n' %(rsti,rstfile))
			if(not(ln.find('run '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				if(rstt!=(eval(raw[0])+rsto)):
					rplcfl(infile,line,'run %d \n' %(rstt-rsto))
	src.close()
	os.system("rm temp2.txt")
	
