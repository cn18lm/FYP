from datetime import datetime

import xml.etree.ElementTree as ET
tree = ET.parse('data/instances/long/long/long01.xml')
root = tree.getroot()

def toDate(d):
  return datetime.strptime(d, '%Y-%m-%d').date()

for child in root:
  print(child.tag,child.attrib)
  print(child.tag)

#SchedulingPeriod
SchedulingPeriod = root.attrib["ID"]
print(SchedulingPeriod)

#StartDate
StartDate = toDate(root[0].text)
print(StartDate)

#EndDate
EndDate = toDate(root[1].text)
print(EndDate)

#numDays
delta = EndDate - StartDate
numDays = delta.days + 1
print(numDays)

#Skills
Skills = []
for child in root[2]:
  print(child.tag,child.attrib)
  Skills.append(child.text)
print(Skills)

#ShiftTypes
ShiftTypes = []
for child in root[3]:
  foo = []
  foo.append(child.attrib["ID"])
  print(foo)

#numShiftTypes
numShiftTypes = len(ShiftTypes)
print(numShiftTypes)
