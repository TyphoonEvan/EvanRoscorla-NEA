import os

def GetLastModified():
    items = os.scandir("teams")
    def get_modified(entry):
        return entry.stat().st_mtime
    sorted = []
    for item in items:
        sorted.append(item)
    sorted.sort(key=get_modified, reverse=False)     
    return sorted.pop()    

print(str(GetLastModified().name))