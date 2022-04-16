int: num_days;
int: num_employees;
int: num_shifts;

enum shift_types;

array[1..num_employees] of set of shift_types: acceptable_shifts;

array[1..num_days, 1..(num_shifts-1)] of int: cover_requirements;

array[1..num_employees, 1..num_days] of var shift_types: roster;


% Nurses can only be assigned shifts for which they have the appropriate skill 
constraint forall(i in 1..num_employees)(
  forall(j in 1..num_days)(
  roster[i,j] in acceptable_shifts[i]
  ));
 
% Cover requirements
constraint forall(j in 1..num_days)(
    forall(s in shift_types)(
        if s < num_shifts then
        sum(i in 1..num_employees)(roster[i,j] == s) == cover_requirements[j , s] endif
));
 
 solve satisfy;
 
 output [ show(roster[i,j]) ++ if j==num_days then "\n" else " " endif
       | i in 1..num_employees, j in 1..num_days ]; 

 
 