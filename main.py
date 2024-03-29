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

def date_to_index(d):
    """
    takes a date object and returns the index of that day
    """
    delta = d - START_DATE
    return delta.days

def write_comment(c):
    f.write("% " + c + ";\n")


def write_var(name, value):
    f.write(name + " = " + str(value) + ";\n")


def write_set(name, list_):
    f.write(name + " = {")
    first = True
    for item in list_:
        if first:
            first = False
            f.write(str(item))
        else:
            f.write(", " + str(item))

    f.write("};\n")

def write_array(name, list_):
    f.write(name + " = [")
    first = True
    for item in list_:
        if first:
            first = False
            f.write(str(item))
        else:
            f.write(", " + str(item))

    f.write("];\n")
    

def day_string_to_int(d):
    return week_days.index(d)


def write_2D_array(name, list_):
    f.write(name + " = [|")
    for i in list_:
        first = True
        for j in i:
            if first:
                f.write(" " + str(j))
                first = False
            else:
                f.write(", " + str(j))
        f.write("\n|")
    f.write("]; \n")


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
    f.write("];\n")
    

def combine_lists(list_):
    """
    Takes a list containing 2d lists of same row length, and joins them into 
    one list which is returned along with the indices (for minizinc) to access
    each list
    """
    combined = []
    indices = []
    
    first = True
    
    for l in list_:
        combined = combined + l
        indexrow = []
        if first:
            indexrow.append(1)
            first = False
        else:
            indexrow.append(indices[-1][-1] + 1)
        
        indexrow.append(indexrow[-1] - 1 + len(l))
        
        indices.append(indexrow)
        
    return combined, indices
            


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
NUM_EMPLOYEES = None

NUM_CONTRACTS = []


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
    #write_set("skills", SKILLS)



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



def employee_contracts():
    
    global EMPLOYEE_CONTRACTS
    global NUM_EMPLOYEES
    
    for e in root.find('Employees'):
        contract = e.find('ContractID').text
        EMPLOYEE_CONTRACTS.append(int(contract)+1) # Adding 1 to make indices work
        
    NUM_EMPLOYEES = len(EMPLOYEE_CONTRACTS)
    
    write_var('num_employees', NUM_EMPLOYEES)
    write_array('employee_contracts', EMPLOYEE_CONTRACTS)
    

def employee_skills():
    
    global EMPLOYEE_SKILLS
    
    total = []
    
    for e in root.find('Employees'): 
        theirskills = []
        for s in e.find('Skills'):
            theirskills.append(s.text)
        EMPLOYEE_SKILLS.append(theirskills)
        
        acceptable_shifts = []
        for i in range(len(SHIFT_TYPES)):
            for j in SHIFT_SKILLS[i]:
                if j in theirskills:
                    acceptable_shifts.append(SHIFT_TYPES[i])
                    break
                
        total.append(acceptable_shifts)
    
    write_array_of_sets('acceptable_shifts', total)
    

def cover_requirements():
    # NEED TO REDO AND ADD SPECIFIC DAYS/SHIFTS
    
    total = [[0] * (NUM_SHIFTS - 1) for _ in range(NUM_DAYS)]
    
    
    for x in root.find('CoverRequirements'):
        
        if x.tag == 'DayOfWeekCover':
            
            d = x.find('Day').text
            day = day_string_to_int(d)
            shifts = SHIFT_TYPES[0:-1]
            
            for c in x.findall('Cover'):
                shift = c.find('Shift').text
                preferred = c.find('Preferred').text
                index = shifts.index(shift)
                shifts[index] = int(preferred)
            
            for i in range(NUM_DAYS):
                if day_index_to_weekday(i) == day:
                    total[i] = shifts.copy()
                    

    for x in root.find('CoverRequirements'):
        
        if x.tag == 'DateSpecificCover':
            
            d = x.find('Date').text
            date = to_date(d)
            day_index = date_to_index(date)
            
            shifts = SHIFT_TYPES[0:-1]
            
            for c in x.findall('Cover'):

                shift = c.find('Shift').text
                shift_index = shifts.index(shift)
                preferred = c.find('Preferred').text
                total[day_index][shift_index] = int(preferred)
    

    write_2D_array("cover_requirements", total)


def unwanted_patterns():
    all_delta = []


    for p in root.find('Patterns'):
        #ID = p.attrib['ID']
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
        
        all_delta.append(delta)
    
    combined, adindices = combine_lists(all_delta)
    write_var('num_unwanted_patterns', len(adindices))
    write_2D_array('unwanted_patterns' , adindices)
    write_2D_array('unwanted_patterns_delta' , combined)






"""---------- Contracts ----------"""

def define_contracts():
    
    global NUM_CONTRACTS
    
    max_num_assignments = []
    min_num_assignments = []
    
    max_consecutive_working_parts = []
    max_consecutive_working_weights = []
    min_consecutive_working_parts = []
    min_consecutive_working_weights = []

    max_consecutive_free_parts = []
    max_consecutive_free_weights = []
    min_consecutive_free_parts = []
    min_consecutive_free_weights = []

    max_consecutive_weekends_parts = []
    max_consecutive_weekends_weights = []
    min_consecutive_weekends_parts = []
    min_consecutive_weekends_weights = []
    
    max_total_weekends_parts = []
    max_total_weekends_weights = []
    
    # used for CompleteWeekends and IdenticalShiftTypesDuringWeekend
    weekends_per_contract = []
    
    complete_weekends = []

    identical_shift_weekend = []
    
    for contract in root.find('Contracts'):
        # Need to ignore if weight = 0
        ID = int(contract.attrib['ID'])+1
        
        # Weekend is defined in contract by a string of days
        wknd = contract.find('WeekendDefinition')
        
        # using regex to split up string into individual days 
        # each new day starts with uppercase character
        # regex inserts space before every uppercase character
        # then string is split with space as delimiter        
        weekend_list = re.sub( r"([A-Z])", r" \1", wknd.text).split()
        
        #converting days to their index in the week
        weekend_list_int = [day_string_to_int(i) for i in weekend_list]
        
        weekend0 = []
        weekend1 = []
        for i in range(NUM_DAYS):
            if day_index_to_weekday(i) == weekend_list_int[0]:
                weekend0.append(i+1)
            if day_index_to_weekday(i) == weekend_list_int[1]:
                weekend1.append(i+1)
        weekends_per_contract.append(weekend0)
        weekends_per_contract.append(weekend1)
        
        
        m = int(contract.find('MaxNumAssignments').text)
        max_num_assignments.append(m)
        
        m = int(contract.find('MinNumAssignments').text)
        min_num_assignments.append(m)
        
        
        m = contract.find('MaxConsecutiveWorkingDays')
        w = int(m.attrib["on"])
        max_consecutive_working_weights.append(w)
        m = int(contract.find('MaxConsecutiveWorkingDays').text)
        max_consecutive_working_parts.append(max_working_consecutive_delta(m))
        
        m = contract.find('MinConsecutiveWorkingDays')
        w = int(m.attrib["on"])
        min_consecutive_working_weights.append(w)
        m = int(contract.find('MinConsecutiveWorkingDays').text)
        min_consecutive_working_parts.append(min_working_consecutive_delta(m))
        
        m = contract.find('MaxConsecutiveFreeDays')
        w = int(m.attrib["on"])
        max_consecutive_free_weights.append(w)
        m = int(contract.find('MaxConsecutiveFreeDays').text)
        max_consecutive_free_parts.append(max_free_consecutive_delta(m))
        
        m = contract.find('MinConsecutiveFreeDays')
        w = int(m.attrib["on"])
        min_consecutive_free_weights.append(w)
        m = int(contract.find('MinConsecutiveFreeDays').text)
        min_consecutive_free_parts.append(min_free_consecutive_delta(m))
        
        m = contract.find('MaxWorkingWeekendsInFourWeeks')
        w = int(m.attrib["on"])
        max_total_weekends_weights.append(w)
        m = int(contract.find('MaxWorkingWeekendsInFourWeeks').text)
        max_total_weekends_parts.append(max_total_weekends(m, weekend_list_int))
        
        m = contract.find('MaxConsecutiveWorkingWeekends')
        w = int(m.attrib["on"])
        max_consecutive_weekends_weights.append(w)
        m = int(contract.find('MaxConsecutiveWorkingWeekends').text)
        max_consecutive_weekends_parts.append(max_weekends_consecutive_delta(m, weekend_list_int))
        
        m = contract.find('MinConsecutiveWorkingWeekends')
        w = int(m.attrib["on"])
        min_consecutive_weekends_weights.append(w)
        m = int(contract.find('MinConsecutiveWorkingWeekends').text)
        min_consecutive_weekends_parts.append(min_weekends_consecutive_delta(m, weekend_list_int))
        
        
        w = contract.find('CompleteWeekends').text
        complete_weekends.append(w)
        
        w = contract.find('IdenticalShiftTypesDuringWeekend').text
        identical_shift_weekend.append(w)
        
    NUM_CONTRACTS = len(max_num_assignments)
    write_var('num_contracts', NUM_CONTRACTS)
    
    write_array('max_num_assignments', max_num_assignments)
    write_array('min_num_assignments', min_num_assignments)
    write_array_of_sets('weekends_per_contract', weekends_per_contract)
    

    write_array('complete_weekends', complete_weekends)
    write_array('identical_shift_weekend', identical_shift_weekend)
    
    a,b = combine_lists(max_consecutive_working_parts)
    write_2D_array('max_consecutive_working', b)
    write_2D_array('max_consecutive_working_delta', a)
    write_array('max_consecutive_working_weights', max_consecutive_working_weights)
    
    a,b = combine_lists(min_consecutive_working_parts)
    write_2D_array('min_consecutive_working', b)
    write_2D_array('min_consecutive_working_delta', a)
    write_array('min_consecutive_working_weights', min_consecutive_working_weights)
    
    a,b = combine_lists(max_consecutive_free_parts)
    write_2D_array('max_consecutive_free', b)
    write_2D_array('max_consecutive_free_delta', a)
    write_array('max_consecutive_free_weights', max_consecutive_free_weights)
    
    a,b = combine_lists(min_consecutive_free_parts)
    write_2D_array('min_consecutive_free', b)
    write_2D_array('min_consecutive_free_delta', a)
    write_array('min_consecutive_free_weights',min_consecutive_free_weights)
    
    a,b = combine_lists(max_total_weekends_parts)
    write_2D_array('max_total_weekends', b)
    write_2D_array('max_total_weekends_delta', a)
    write_array('max_total_weekends_weights',max_total_weekends_weights)
    
    a,b = combine_lists(max_consecutive_weekends_parts)
    write_2D_array('max_consecutive_weekends', b)
    write_2D_array('max_consecutive_weekends_delta', a)
    write_array('max_consecutive_weekends_weights',max_consecutive_weekends_weights)
    
    a,b = combine_lists(min_consecutive_weekends_parts)
    write_2D_array('min_consecutive_weekends', b)
    write_2D_array('min_consecutive_weekends_delta', a)
    write_array('min_consecutive_weekends_weights',min_consecutive_weekends_weights)


    
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
    
    return(delta)

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
    
    return(delta)
    
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
    
    return(delta)

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
    
    return(delta)
    
def max_total_weekends(m_, weekend):
    delta = []
    
    if m_ == 0:
        for j in range(7):
            row = []
            if j in weekend:
                for k in range(len(SHIFT_TYPES) - 1):
                    row.append(0)
                row.append((j + 1 )%7 + 1)
            else:
                for k in range(len(SHIFT_TYPES)):
                    row.append((j + 1 )%7 + 1)
            delta.append(row)
        return(delta)
    
    indices = [*range(m_)]
    
    for i in indices:
        for j in range(7):
            row = []
            if j == weekend[0]:
                for k in range(len(SHIFT_TYPES) - 1):
                    if i == indices[-1]:
                        row.append(0)
                    else:
                        row.append(7*m_ + i + 1)
                row.append((j + 1 )%7 + 1 + 7 * i)
            
            elif j == weekend[1]:
                for k in range(len(SHIFT_TYPES) - 1):
                    if i == indices[-1]:
                        row.append(0)
                    else:
                        row.append((j + 1 )%7 + 1 + 7 * (i+1))
                row.append((j + 1 )%7 + 1 + 7 * i)
            
            else:
                for k in range(len(SHIFT_TYPES)):
                    row.append((j + 1 )%7 + 1 + 7 * i)
                    
            delta.append(row)
    
    for i in indices[0:-1]:
        row = []
        for k in range(len(SHIFT_TYPES)):
            row.append((weekend[1] + 1 )%7 + 1 + 7 * (i+1))
        delta.append(row)
    
    return(delta)
    
def max_weekends_consecutive_delta(m_, weekend):
    delta = []
    
    indices = [*range(m_)]
    
    for i in indices:
        for j in range(7):
            row = []
            if j == weekend[0]:
                for k in range(len(SHIFT_TYPES) - 1):
                    if i == indices[-1]:
                        row.append(0)
                    else:
                        row.append(7*m_ + i + 1)
                row.append((j + 1 )%7 + 1 + 7 * i)
            
            elif j == weekend[1]:
                for k in range(len(SHIFT_TYPES) - 1):
                    if i == indices[-1]:
                        row.append(0)
                    else:
                        row.append((j + 1 )%7 + 1 + 7 * (i+1))
                        
                row.append((j + 1 )%7 + 1)
            
            else:
                for k in range(len(SHIFT_TYPES)):
                    row.append((j + 1 )%7 + 1 + 7 * i)
                    
            delta.append(row)
    
    for i in indices[0:-1]:
        row = []
        for k in range(len(SHIFT_TYPES)):
            row.append((weekend[1] + 1 )%7 + 1 + 7 * (i+1))
        delta.append(row)
    
    return(delta)

def min_weekends_consecutive_delta(m_, weekend):
    #not done yet
    delta = []
    
    indices = [*range(m_+1)]
    
    for i in indices:
        for j in range(7):
            row = []
            if j == weekend[0]:
                for k in range(len(SHIFT_TYPES) - 1):
                    row.append(7*m_ + i + 1)
                row.append((j + 1 )%7 + 1 + 7 * i)
            
            elif j == weekend[1]:
                for k in range(len(SHIFT_TYPES) - 1):
                    if i == indices[-1]:
                        row.append((j + 1 )%7 + 1 + 7 * i)
                    else:
                        row.append((j + 1 )%7 + 1 + 7 * (i+1))
                
                if i == indices[0]:
                    row.append((j + 1 )%7 + 1)
                
                elif i == indices[-1]:
                    row.append((j + 1 )%7 + 1)
                else:
                    row.append(0)
                    
                
            
            else:
                for k in range(len(SHIFT_TYPES)):
                    row.append((j + 1 )%7 + 1 + 7 * i)
                    
            delta.append(row)
    
    for i in indices:
        row = []
        for k in range(len(SHIFT_TYPES)):
            if i == indices[-1]:
                row.append((weekend[1] + 1 )%7 + 1 + 7 * i)
            else:
                row.append((weekend[1] + 1 )%7 + 1 + 7 * (i+1))
        delta.append(row)
    
    return(delta)
    
    
    
"""----- day/shift on/off requests -----"""

def day_on_requests():
    
    total = [[0] * (NUM_DAYS) for _ in range(NUM_EMPLOYEES)]
    
    if root.find('DayOnRequests') == None:
        write_2D_array('day_on_requests', total)
        return
    
    for d in root.find('DayOnRequests'):
        ID = int(d.find('EmployeeID').text)
        date = to_date(d.find('Date').text)
        date_index = date_to_index(date)
        total[ID][date_index] = 1
    
    write_2D_array('day_on_requests', total)
    
def day_off_requests():
    total = [[0] * (NUM_DAYS) for _ in range(NUM_EMPLOYEES)]
    
    if root.find('DayOffRequests') == None:
        write_2D_array('day_off_requests', total)
        return
    
    for d in root.find('DayOffRequests'):
        ID = int(d.find('EmployeeID').text)
        date = to_date(d.find('Date').text)
        date_index = date_to_index(date)
        total[ID][date_index] = 1
    
    write_2D_array('day_off_requests', total)
    
    
def shift_on_requests():
    total_ = []
    for s in SHIFT_TYPES[0:-1]:
        
        total = [[0] * (NUM_DAYS) for _ in range(NUM_EMPLOYEES)]
        
        if root.find('ShiftOnRequests') == None:
            total_.append(total)
        else:
            for d in root.find('ShiftOnRequests'):
                ID = int(d.find('EmployeeID').text)
                date = to_date(d.find('Date').text)
                date_index = date_to_index(date)
                shift = d.find('ShiftTypeID').text
                
                if shift == s:
                    total[ID][date_index] = 1
            total_.append(total)
     
    combined, indices = combine_lists(total_)
    write_2D_array('shift_on_request_indices' , indices)
    write_2D_array('shift_on_requests' , combined)

def shift_off_requests():
    total_ = []
    for s in SHIFT_TYPES[0:-1]:
        
        total = [[0] * (NUM_DAYS) for _ in range(NUM_EMPLOYEES)]
        
        if root.find('ShiftOffRequests') == None:
            total_.append(total)
        else:
            for d in root.find('ShiftOffRequests'):
                ID = int(d.find('EmployeeID').text)
                date = to_date(d.find('Date').text)
                date_index = date_to_index(date)
                shift = d.find('ShiftTypeID').text
                
                if shift == s:
                    total[ID][date_index] = 1
            total_.append(total)
     
    combined, indices = combine_lists(total_)
    write_2D_array('shift_off_request_indices' , indices)
    write_2D_array('shift_off_requests' , combined)




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
    
    day_on_requests()
    day_off_requests()
    shift_on_requests()
    shift_off_requests()
    

main()


f.close()
