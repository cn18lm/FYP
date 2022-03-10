import calendar

from datetime import datetime

import xml.etree.ElementTree as ET

week_days = list(calendar.day_name)

tree = ET.parse('data/instances/long/long/long01.xml')
root = tree.getroot()


""" USEFUL FUNCTIONS """


def to_date(d):
    return datetime.strptime(d, '%Y-%m-%d').date()


def write_comment(c):
    f.write("% " + c + "\n")


def write_var(v1, v2):
    f.write(v1 + " = " + str(v2) + "\n")


def write_set(n, a):
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
    return week_days.index(d)


def writeCalendar(n, a):
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


""" PARSING XML DATA """

SchedulingPeriod = root.attrib["ID"]
filename = SchedulingPeriod + ".dzn"

f = open(filename, "w")


for child in root:
    print(child.tag, child.attrib)

# SchedulingPeriod
write_comment(SchedulingPeriod)

# StartDate
StartDate = to_date(root.find('StartDate').text)
write_comment("StartDate: " + StartDate.strftime('%Y-%m-%d'))

# EndDate
EndDate = to_date(root.find('EndDate').text)
write_comment("EndDate: " + EndDate.strftime('%Y-%m-%d'))

# Starting day,  monday = 0
firstDay = StartDate.weekday()
write_var("firstDay", firstDay)

# numDays
delta = EndDate - StartDate
numDays = delta.days + 1
write_var("numDays", numDays)

# Skills
Skills = []
for child in root.find('Skills'):
    Skills.append(child.text)
write_set("Skills", Skills)

# ShiftTypes
ShiftTypes = []

for child in root.find('ShiftTypes'):
    name = child.attrib["ID"]
    ShiftTypes.append(name)
    arr = []
    for skill in child.find('Skills'):
        arr.append(skill.text)
    write_set(name, arr)
write_set("ShiftTypes", ShiftTypes)

# CoverRequirements
week = week_days.copy()
for x in root.find('CoverRequirements'):
    if x.tag == 'DayOfWeekCover':
        day = ShiftTypes.copy()
        for y in x.findall('Cover'):
            index = ShiftTypes.index(y[0].text)
            day[index] = y[1].text
        index = week_days.index(x[0].text)
        week[index] = day

big = []

for i in range(numDays):
    big.append(week[(firstDay + i) % 7])

writeCalendar("CoverRequirements", big)

f.close()
