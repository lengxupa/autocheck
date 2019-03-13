def writelogini(cnt):
	s=open('logini.m','w')
	s.writelines("global i;\n")
	if(cnt==1):
		s.writelines("smooth=1;\n")
	else:
		s.writelines("smooth=0;\n")
	s.writelines("i=%d;\n" %cnt)
	s.writelines("run logresults.m;\n")
	s.close()

