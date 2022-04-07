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


def write_var(name, value):
    f.write(name + " = " + str(value) + "\n")


def write_set(name, list_):
    f.write(name + " = {")
    first = True
    for item in list_:
        if first:
            first = False
            f.write(str(item))
        else:
            f.write(", " + str(item))

    f.write("}\n")


def day_string_to_int(d):
    return week_days.index(d)


def write_2D_array(name, list_):
    f.write(name + " = [|")
    for i in list_:
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

SCHEDULING_PERIOD = root.attrib["ID"]
filename = SCHEDULING_PERIOD + ".dzn"
f = open(filename, "w")



for child in root:
    print(child.tag, child.attrib)


""" ------------------ GLOBAL VARIABLES ------------------ """
START_DATE = None
END_DATE = None
NUM_DAYS = None

SKILLS = []
SHIFT_TYPES = []


def scheduling_period():
    write_comment(SCHEDULING_PERIOD)



def dates():
    global START_DATE
    global END_DATE
    global NUM_DAYS
    
    START_DATE = to_date(root.find('StartDate').text)
    END_DATE = to_date(root.find('EndDate').text)
    delta = END_DATE - START_DATE
    NUM_DAYS = delta.days + 1

    
    write_comment("START_DATE: " + START_DATE.strftime('%Y-%m-%d'))
    
    write_comment("END_DATE: " + END_DATE.strftime('%Y-%m-%d'))
      
    write_var("NUM_DAYS", NUM_DAYS)


def skills():
    global SKILLS
    for child in root.find('Skills'):
        SKILLS.append(child.text)
    write_set("SKILLS", SKILLS)



def shift_types():
    global SHIFT_TYPES
    for child in root.find('ShiftTypes'):
        name = child.attrib["ID"]
        SHIFT_TYPES.append(name)
        arr = []
        for skill in child.find('Skills'):
            arr.append(skill.text)
        write_set(name, arr)
    write_set("SHIFT_TYPES", SHIFT_TYPES)



def cover_requirements():
    week = week_days.copy()
    for x in root.find('CoverRequirements'):
        if x.tag == 'DayOfWeekCover':
            day = SHIFT_TYPES.copy()
            for y in x.findall('Cover'):
                index = SHIFT_TYPES.index(y[0].text)
                day[index] = y[1].text
            index = week_days.index(x[0].text)
            week[index] = day

    big = []

    firstDay = START_DATE.weekday()
    for i in range(NUM_DAYS):
        big.append(week[(firstDay + i) % 7])

    write_2D_array("CoverRequirements", big)



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
            
            # Shift types
            shift = q.find('ShiftType').text
            
            
            # if any shift type is any, set array to all shifts
            if shift == 'Any':
                shift_array = [*range(len(SHIFT_TYPES))]
            
            # if shift type is none, set array to be off shift 
            elif shift == 'None':
                shift_array = [len(SHIFT_TYPES)]
            
            else:
                shift_array = [SHIFT_TYPES.index(shift)]
            

            # Days
            day = q.find('Day').text
            day_array = []
            
            # if day is any, set array to be integers 0-6
            if day == 'Any':
                day_array = [*range(7)]
                
            # otherwise set array to be integer of day
            else:
                day_array = [day_string_to_int(day)]

            
            delta_part = []
            for i in range(7):
                row = []
                for j in range(len(SHIFT_TYPES) + 1):
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
