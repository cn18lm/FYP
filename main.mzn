int: num_days;
int: num_employees;
int: num_shifts;

enum shift_types;


array[1..num_shifts] of shift_types: shift_types_array; 

array[1..num_employees] of set of shift_types: acceptable_shifts;

array[1..num_days, 1..(num_shifts-1)] of int: cover_requirements;

array[1..num_employees, 1..num_days] of var shift_types: roster;

function int: shift_type_to_int(shift_types: s) =  
  sum(  [ if s = shift_types_array[i] 
              then i
           else 0 endif  
          | i in index_set(shift_types_array) ]
   );

% Nusrses can only be assigned shifts for which they have the appropriate skill 
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

 
 