def subjob(i):
	cmd=("qsub %s" %i)
	tst=Popen(cmd,shell=True, stdout=PIPE)
	outp,err=tst.communicate()
	print outp
	outp=outp.split('\n')
	for line in outp:
		if(line):
			if ord(line[0])>=48 and ord(line[0])<=57:
				content=line.split('.')
				jbID=content[0]
	walltimeo,jbN,infile,ppno=rdsb(i)
	cmd1=("pwd")
	tst1=Popen(cmd1,shell=True, stdout=PIPE)
	outp1,err1=tst1.communicate()
	print outp1
	pwd=outp1.split('\n')
	if(jbN[0]=='b' and jbN[1]=='d'):
		pwd[0]+='/bond'
	subidtomotherfile(jbID,jbN[0:15],pwd[0])

