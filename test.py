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
        f.write("\n | ")
    f.write("] \n")


""" ------------------ PARSING XML DATA ------------------ """

SchedulingPeriod = root.attrib["ID"]
filename = SchedulingPeriod + ".dzn"
f = open(filename, "w")



for child in root:
    print(child.tag, child.attrib)


""" ------------------ GLOBAL VARIABLES ------------------ """
StartDate = None
EndDate = None
num_days = None

Skills = []
ShiftTypes = []


def scheduling_period():
    write_comment(SchedulingPeriod)



def dates():
    global StartDate
    global EndDate
    global num_days
    
    StartDate = to_date(root.find('StartDate').text)
    EndDate = to_date(root.find('EndDate').text)
    delta = EndDate - StartDate
    num_days = delta.days + 1

    
    write_comment("StartDate: " + StartDate.strftime('%Y-%m-%d'))
    
    write_comment("EndDate: " + EndDate.strftime('%Y-%m-%d'))
      
    write_var("num_days", num_days)


def skills():
    global Skills
    for child in root.find('Skills'):
        Skills.append(child.text)
    write_set("Skills", Skills)



def shift_types():
    global ShiftTypes
    for child in root.find('ShiftTypes'):
        name = child.attrib["ID"]
        ShiftTypes.append(name)
        arr = []
        for skill in child.find('Skills'):
            arr.append(skill.text)
        write_set(name, arr)
    write_set("ShiftTypes", ShiftTypes)



def cover_requirements():
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

    firstDay = StartDate.weekday()
    for i in range(num_days):
        big.append(week[(firstDay + i) % 7])

    writeCalendar("CoverRequirements", big)



def unwanted_patterns():
    
    for p in root.find('Patterns'):
        print('Pattern ID = ' + p.attrib['ID'])
        
        indices = []
        
        for q in p.find('PatternEntries'):
            
            index = int(q.attrib['index'])
            indices.append(index)
            
        delta = []
        
        
        for q in p.find('PatternEntries'):
            
            index = int(q.attrib['index'])
            
            print('Pattern index = ' + str(index))
            
            # Shift types
            shift = q.find('ShiftType').text
            
            
            # if any shift type is any, set array to all shifts
            if shift == 'Any':
                shift_array = [*range(len(ShiftTypes))]
            
            # if shift type is none, set array to be off shift 
            elif shift == 'None':
                shift_array = [len(ShiftTypes)]
            
            else:
                shift_array = [ShiftTypes.index(shift)]
            
            print ('   Shift type = ' + shift)
            print(shift_array)
            
            # Days
            day = q.find('Day').text
            day_array = []
            
            # if day is any, set array to be integers 0-6
            if day == 'Any':
                day_array = [*range(7)]
                
            # otherwise set array to be integer of day
            else:
                day_array = [dayStrToInt(day)]

            print ('   Day = ' + day)
            print(day_array)
            
            delta_part = []
            for i in range(7):
                row = []
                for j in range(len(ShiftTypes) + 1):
                    row.append((i+1) % 7 + 1)
                delta_part.append(row)
            
            # if we are on last index, send any matches to the fail state
            if index == indices[-1]:
                for i in day_array:
                    for j in shift_array:
                        delta_part[i][j] = 0 
            
            else:
                for i in day_array:
                    for j in shift_array:
                        delta_part[i][j] = (i+1) % 7 + 1 + (7 * (index+1))
            
            #print(delta_part)
            delta = delta + delta_part
 
        print(delta)
        print('.....')

    
    
    
def main():
    scheduling_period()
    dates()
    skills()
    shift_types()
    cover_requirements()
    unwanted_patterns() 

main()

    
    
    
    
f.close()
