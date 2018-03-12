import subprocess
import time

start=0
while start<45000:
	subprocess.call(" python3 get_urls.py "+str(start), shell=True  )
	start+=1000
	time.sleep(5)
