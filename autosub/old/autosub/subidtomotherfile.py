def subidtomotherfile(jbID,jbN,pwd):
	os.system("cp /home/shen276/motherjob/motherjob.txt motherjob.txt")
	src=open('motherjob.txt',"r")
	des=open('mothertemp.txt',"w")
	des.writelines(src.read())
	src.close()
	des.write("%s %s %s\n" %(jbID,jbN,pwd))
	des.close()
	os.system("mv mothertemp.txt /home/shen276/motherjob/motherjob.txt")
	os.system("rm mother*.txt")

