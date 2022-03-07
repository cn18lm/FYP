#replace root[n] with search for specific child?
import calendar
daysOfWeek = list(calendar.day_name)

from datetime import datetime

import xml.etree.ElementTree as ET
tree = ET.parse('data/instances/long/long/long01.xml')
root = tree.getroot()

SchedulingPeriod = root.attrib["ID"]
filename = SchedulingPeriod + ".dzn"

f = open(filename, "w")

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

def dayStrToInt(d):
    return daysOfWeek.index(d)

def writeCalendar(n,a):
    f.write(n + " = [|")
    for i in a:
        first = True
        for j in i:
            if first:
                f.write(j)
                first = False
            else:
                f.write(", " + j)
        f.write(" |")
    f.write("] \n")
            

for child in root:
  print(child.tag,child.attrib)

#SchedulingPeriod
writeComment(SchedulingPeriod)

#StartDate
StartDate = toDate(root.find('StartDate').text)
writeComment("StartDate: " + StartDate.strftime('%Y-%m-%d'))

#EndDate
EndDate = toDate(root.find('EndDate').text)
writeComment("EndDate: " + EndDate.strftime('%Y-%m-%d'))

#Starting day,  monday = 0 
firstDay = StartDate.weekday()
writeVar("firstDay",firstDay)

#numDays
delta = EndDate - StartDate
numDays = delta.days + 1
writeVar("numDays", numDays)

#Skills
Skills = []
for child in root.find('Skills'):
  Skills.append(child.text)
writeSet("Skills", Skills)

#ShiftTypes
ShiftTypes = []

for child in root.find('ShiftTypes'):
  name = child.attrib["ID"]
  ShiftTypes.append(name)
  arr = []
  for skill in child.find('Skills'):
      arr.append(skill.text)
  writeSet(name, arr)
writeSet("ShiftTypes", ShiftTypes)

#CoverRequirements
week = daysOfWeek.copy()
for x in root.find('CoverRequirements'):
    if x.tag == 'DayOfWeekCover':
        day = ShiftTypes.copy()
        for y in x.findall('Cover'):
            index = ShiftTypes.index(y[0].text)
            day[index] = y[1].text
        index = daysOfWeek.index(x[0].text)
        week[index] = day

big = []

for i in range(numDays):
    big.append(week[(firstDay + i)%7])

writeCalendar("CoverRequirements", big)

f.close()