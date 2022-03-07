#replace root[n] with search for specific child?


from datetime import datetime

import xml.etree.ElementTree as ET
tree = ET.parse('data/instances/long/long/long01.xml')
root = tree.getroot()

SchedulingPeriod = root.attrib["ID"]
filename = SchedulingPeriod + ".dzn"

f = open(filename, "w",)

# Useful functions

def toDate(d):
  return datetime.strptime(d, '%Y-%m-%d').date()

def writeComment(c):
    f.write("% " + c + "\n")
    
def writeVar(v1, v2):
    f.write(v1 + " = " + str(v2) + "\n")
    
def writeSet(n, a):
    f.write(n + " = {")
    first = True
    for item in a:
        if first:
            first = False
            f.write(str(item))
        else:
            f.write(", " + str(item))
    
    f.write("}\n")
        

for child in root:
  print(child.tag,child.attrib)

#SchedulingPeriod
writeComment(SchedulingPeriod)

#StartDate
StartDate = toDate(root[0].text)
writeComment("StartDate: " + StartDate.strftime('%Y-%m-%d'))

#Starting day,  monday = 0 
print(StartDate.weekday())

#EndDate
EndDate = toDate(root[1].text)
writeComment("EndDate: " + EndDate.strftime('%Y-%m-%d'))

#numDays
delta = EndDate - StartDate
numDays = delta.days + 1
writeVar("numDays", numDays)

#Skills
Skills = []
for child in root[2]:
  Skills.append(child.text)
writeSet("Skills", Skills)

#ShiftTypes
ShiftTypes = []

for child in root[3]:
  name = child.attrib["ID"]
  ShiftTypes.append(name)
  skills = []
  for skill in child[3]:
      skills.append(skill.text)
  writeSet(name, skills)
writeSet("ShiftTypes", ShiftTypes)

#CoverRequirements
CoverRequirements = []



f.close()