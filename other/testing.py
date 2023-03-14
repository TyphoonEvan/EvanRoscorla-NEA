searchList = [True, False, True, True, False, True, False, False]

idsList1 = [i for i in range(len(searchList)) if searchList[i] == True]
idsList2 = []
for j in range(len(searchList)):
    if searchList[j] == True:
        idsList2.append(j)

print(idsList1)
print(idsList2)