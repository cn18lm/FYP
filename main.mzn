int: num_days;
int: num_employees;
int: num_shifts;

enum shift_types;

array[1..num_employees] of set of shift_types: acceptable_shifts;

array[1..num_employees, 1..num_days] of var shift_types: roster;


constraint forall(i in 1..num_employees)(
  forall(j in 1..num_days)(
  roster[i,j] in acceptable_shifts[i]
  ));
  
 solve satisfy;

 
 