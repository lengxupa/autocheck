def tmpchk(i):
	a=fdindx('Temp')
	if(a):
		cmd=("sed '1,%dd' log.lammps" %fdln('Temp'))
		tst=Popen(cmd,shell=True,stdout=PIPE)
		outp,err=tst.communicate()
		print outp
		src = open("temp.txt", "w+")
		src.writelines(outp)
		src.close()
		cmd2=("find -maxdepth 1 -name temp.txt | xargs grep %d" %i)
		tst2=Popen(cmd2,shell=True,stdout=PIPE)
		outp2,err2=tst2.communicate()
		print outp2
		if(outp2):
			src = open("temp2.txt", "w+")
			src.writelines(outp2)
			src.close()
			b = np.loadtxt('temp2.txt')
			return b[a]<4000
		else:
			return False
		os.system("rm temp.txt")
		os.system("rm temp2.txt")
	else:
		return False

