import os
import time

path = "c:/Users/USER/Desktop/System Administator/Private-Cloud/README.md"
mtime = os.path.getmtime(path)
print(f"Last modified: {time.ctime(mtime)}")
