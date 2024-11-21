string = "@@ -93,6 +93,7 @@"
start,context = string[string.find('+') + 1 : -2].split(',')
print(int(start),int(start) + int(context) - 1)