def rplcfl(infl,s1,s2):
	open('temp.txt', 'w').write(re.sub(r'%s' %s1, s2, open(infl).read()))
	src = file("temp.txt", "r+")
	des = file(infl, "w+")
	des.writelines(src.read())
	src.close()
	des.close()
	os.system("rm temp.txt")

