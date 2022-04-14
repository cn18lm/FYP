import calendar

from datetime import datetime

import xml.etree.ElementTree as ET

import re

week_days = list(calendar.day_name)

tree = ET.parse('data/instances/long/long/long01.xml')
root = tree.getroot()


""" USEFUL FUNCTIONS """


def to_date(d):
    return datetime.strptime(d, '%Y-%m-%d').date()


def day_index_to_weekday(i):
    """
    takes the index of a day and returns what day of the week it is, as an int
    
    """
    firstDay = START_DATE.weekday()
    
    return((firstDay + i) % 7)


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

def write_array(name, list_):
    f.write(name + " = [")
    first = True
    for item in list_:
        if first:
            first = False
            f.write(str(item))
        else:
            f.write(", " + str(item))

    f.write("]\n")
    

def day_string_to_int(d):
    return week_days.index(d)


def write_2D_array(name, list_):
    f.write(name + " = [\n|")
    for i in list_:
        first = True
        for j in i:
            if first:
                f.write(" " + str(j))
                first = False
            else:
                f.write(", " + str(j))
        f.write("\n|")
    f.write("] \n")


def write_array_of_sets(name, list_):
    f.write(name + " = [")
    firstfirst = True
    for i in list_:
        if firstfirst:
            f.write("{")
            firstfirst = False
        else:
            f.write(",{")
        first = True
        for j in i:
            if first:
                f.write(str(j))
                first = False
            else:
                f.write(", " + str(j))
        f.write("}")
    f.write("]\n")


""" ------------------ PARSING XML DATA ------------------ """

SCHEDULING_PERIOD = root.attrib["ID"]
filename = SCHEDULING_PERIOD + ".dzn"
f = open(filename, "w")


""" ------------------ GLOBAL VARIABLES ------------------ """
START_DATE = None
END_DATE = None
NUM_DAYS = None

SKILLS = []
SHIFT_TYPES = []
OFF_SHIFT = 'ZZ'
SHIFT_SKILLS = []
NUM_SHIFTS = []

EMPLOYEE_CONTRACTS = []
EMPLOYEE_SKILLS = []


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

    write_var("num_days", NUM_DAYS)


def skills():
    global SKILLS
    for child in root.find('Skills'):
        SKILLS.append(child.text)
    write_set("skills", SKILLS)



def shift_types():
    global SHIFT_TYPES
    global SHIFT_SKILLS
    global NUM_SHIFTS
    
    for child in root.find('ShiftTypes'):
        name = child.attrib["ID"]
        SHIFT_TYPES.append(name)
        s = []
        for skill in child.find('Skills'):
            s.append(skill.text)
        SHIFT_SKILLS.append(s)
    
    
    
    # ZZ represents no shift (which accepts any skill)
    SHIFT_TYPES.append(OFF_SHIFT)
    SHIFT_SKILLS.append(SKILLS)
    NUM_SHIFTS = len(SHIFT_TYPES)
    
    write_var('num_shifts', NUM_SHIFTS)
    write_set("shift_types", SHIFT_TYPES)
    write_array_of_sets("shift_skills", SHIFT_SKILLS)
    



def employee_contracts():
    
    global EMPLOYEE_CONTRACTS
    
    for e in root.find('Employees'):
        contract = e.find('ContractID').text
        EMPLOYEE_CONTRACTS.append(int(contract)+1) # Adding 1 to make indices work
        
    write_var('num_employees', len(EMPLOYEE_CONTRACTS))
    
    write_array('employee_contracts', EMPLOYEE_CONTRACTS)
    

def employee_skills():
    
    global EMPLOYEE_SKILLS
    
    for e in root.find('Employees'): 
        theirskills = []
        for s in e.find('Skills'):
            theirskills.append(s.text)
        EMPLOYEE_SKILLS.append(theirskills)
    
    write_array_of_sets('employee_skills', EMPLOYEE_SKILLS)
    
    

def cover_requirements():
    # NEED TO REDO AND ADD SPECIFIC DAYS/SHIFTS
    week = week_days.copy()
    for x in root.find('CoverRequirements'):
        if x.tag == 'DayOfWeekCover':
            day = SHIFT_TYPES[0:-1]
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
    all_delta = []
    adindices = []
    first = True

    for p in root.find('Patterns'):
        ID = p.attrib['ID']
        indices = []

        for q in p.find('PatternEntries'):

            index = int(q.attrib['index'])
            indices.append(index)

        delta = []

        for q in p.find('PatternEntries'):

            index = int(q.attrib['index'])

            #----- Shift types -----
            shift = q.find('ShiftType').text
            
            # 'None' means off shift, represented by 'ZZ'
            if shift == 'None':
                shift = OFF_SHIFT

            # if any shift type is any, set array to all shifts other than off
            if shift == 'Any':
                shift_array = [*range(len(SHIFT_TYPES)-1)]

            else:
                shift_array = [SHIFT_TYPES.index(shift)]

            #----- Days ------
            day = q.find('Day').text
            day_array = []

            # if day is any, set array to be integers 0-6
            if day == 'Any':
                day_array = [*range(7)]

            # otherwise set array to be integer of day
            else:
                day_array = [day_string_to_int(day)]

            # ----- creating transition function table -----
            delta_part = []
            for i in range(7):
                row = []
                for j in range(len(SHIFT_TYPES)):
                    row.append((i+1) % 7 + 1)
                delta_part.append(row)

            # if we are on last index, send any matches to the fail state
            if index == indices[-1]:
                for i in day_array:
                    for j in shift_array:
                        delta_part[i][j] = 0
            
            # otherwise send matches to next 'level' of DFA
            else:
                for i in day_array:
                    for j in shift_array:
                        delta_part[i][j] = (i+1) % 7 + 1 + (7 * (index+1))

            delta = delta + delta_part

        #write_2D_array('delta'+ID , delta)
        indexrow = []
        if first:
            indexrow.append(1)
            first = False
        else:
            indexrow.append(adindices[-1][-1] + 1)
        
        indexrow.append(indexrow[-1] - 1 + len(delta))
        
        adindices.append(indexrow)
        
        all_delta = all_delta + delta
        print(len(delta))
    
    print(len(all_delta))
    print(adindices)
    write_2D_array('unwanted_patterns' , adindices)
    write_2D_array('unwanted_patterns_delta' , all_delta)


def define_contracts():
    max_num_assignments = []
    min_num_assignments = []
    for contract in root.find('Contracts'):
        ID = int(contract.attrib['ID'])+1
               
        # MaxNumAssignments
        m = contract.find('MaxNumAssignments').text
        max_num_assignments.append(m)
        
        m = contract.find('MinNumAssignments').text
        min_num_assignments.append(m)
        
        # Weekend is defined in contract by a string of days
        wknd = contract.find('WeekendDefinition')
        
        # using regex to split up string into individual days 
        # each new day starts with uppercase character
        # regex inserts space before every uppercase character
        # then string is split with space as delimiter        
        weekend_list = re.sub( r"([A-Z])", r" \1", wknd.text).split()
        
        #converting days to their index in the week
        weekend_list_int = [day_string_to_int(i) for i in weekend_list]
        print(weekend_list)
        print(weekend_list_int)
        
        weekend_indices = []
        for i in range(NUM_DAYS):
            if day_index_to_weekday(i) in weekend_list_int:
                weekend_indices.append(i)
        
        print(weekend_indices)
        
        weekend_indices_mz = [x+1 for x in weekend_indices]
        name = "weekend_c" + str(ID)
        write_array(name, weekend_indices_mz)
    
    write_array('max_num_assignments', max_num_assignments)
    write_array('min_num_assignments', min_num_assignments)
        
def max_working_consecutive_delta(m_):
    delta = []
    for i in range(NUM_DAYS):
        row = []
        if i + 1 == m_ + 1 :
            for j in range(NUM_SHIFTS-1):
                row.append(0)
            row.append(1)
        else:
            for j in range(NUM_SHIFTS-1):
                row.append(i+2)
            row.append(1)        
        delta.append(row)
    
    print(delta)

def min_working_consecutive_delta(m_):
    delta = []
    for i in range(NUM_DAYS):
        row = []
        if i + 1 == 1:
            for j in range(NUM_SHIFTS-1):
                row.append(i+2)
            row.append(i+1)
        elif i == m_ :
            for j in range(NUM_SHIFTS-1):
                row.append(i+1)
            row.append(1)
        else:
            for j in range(NUM_SHIFTS-1):
                row.append(i+2)
            row.append(0)        
        delta.append(row)
    
    print(delta)
    
def max_free_consecutive_delta(m_):
    delta = []
    for i in range(NUM_DAYS):
        row = []
        if i + 1 == m_ + 1 :
            for j in range(NUM_SHIFTS-1):
                row.append(1)
            row.append(0)
        else:
            for j in range(NUM_SHIFTS-1):
                row.append(1)
            row.append(i+2)        
        delta.append(row)
    
    print(delta)

def min_free_consecutive_delta(m_):
    delta = []
    for i in range(NUM_DAYS):
        row = []
        if i + 1 == 1:
            for j in range(NUM_SHIFTS-1):
                row.append(i+1)
            row.append(i+2)
        elif i == m_ :
            for j in range(NUM_SHIFTS-1):
                row.append(1)
            row.append(i+1)
        else:
            for j in range(NUM_SHIFTS-1):
                row.append(0)
            row.append(i+2)        
        delta.append(row)
    
    print(delta)
    
def max_weekends_consecutive_delta(m_):
    None

def min_weekends_consecutive_delta(m_):
    None

def main():
    scheduling_period()
    dates()
    skills()
    shift_types()
    employee_contracts()
    employee_skills()
    define_contracts()
    unwanted_patterns()
    cover_requirements()

main()


f.close()
