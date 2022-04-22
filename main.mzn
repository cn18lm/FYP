% Initializing all the variables from datafile ====================
include "long01.dzn";
include "soft_constraints/minibrass.mzn";
include "main_o.mzn";
int: num_days;
int: num_employees;
int: num_shifts;
int: num_contracts;

set of int: shift_types;

array[1..num_employees] of set of shift_types: acceptable_shifts;

array[1..num_days, 1..(num_shifts-1)] of int: cover_requirements;

array[1..num_employees] of int: employee_contracts;

array[1..num_contracts] of int: max_num_assignments;
array[1..num_contracts] of int: min_num_assignments;

array[1..(2*num_contracts)] of set of int: weekends_per_contract;
array[1..num_contracts] of bool: complete_weekends;
array[1..num_contracts] of bool: identical_shift_weekend;

array[1..num_contracts, 1..2] of int: max_consecutive_working;
array[1..max_consecutive_working[num_contracts,2], 1..num_shifts] of int: max_consecutive_working_delta;
array[1..num_contracts] of int: max_consecutive_working_weights;

array[1..num_contracts, 1..2] of int: min_consecutive_working;
array[1..min_consecutive_working[num_contracts,2], 1..num_shifts] of int: min_consecutive_working_delta;
array[1..num_contracts] of int: min_consecutive_working_weights;

array[1..num_contracts, 1..2] of int: max_consecutive_free;
array[1..max_consecutive_free[num_contracts,2], 1..num_shifts] of int: max_consecutive_free_delta;
array[1..num_contracts] of int: max_consecutive_free_weights;

array[1..num_contracts, 1..2] of int: min_consecutive_free;
array[1..min_consecutive_free[num_contracts,2], 1..num_shifts] of int: min_consecutive_free_delta;
array[1..num_contracts] of int: min_consecutive_free_weights;

array[1..num_contracts, 1..2] of int: max_total_weekends;
array[1..max_total_weekends[num_contracts,2], 1..num_shifts] of int: max_total_weekends_delta;
array[1..num_contracts] of int: max_total_weekends_weights;

array[1..num_contracts, 1..2] of int: max_consecutive_weekends;
array[1..max_consecutive_weekends[num_contracts,2], 1..num_shifts] of int: max_consecutive_weekends_delta;
array[1..num_contracts] of int: max_consecutive_weekends_weights;

array[1..num_contracts, 1..2] of int: min_consecutive_weekends;
array[1..min_consecutive_weekends[num_contracts,2], 1..num_shifts] of int: min_consecutive_weekends_delta;
array[1..num_contracts] of int: min_consecutive_weekends_weights;


int: num_unwanted_patterns;
array[1..num_unwanted_patterns,1..2] of int: unwanted_patterns;
array[1..unwanted_patterns[num_unwanted_patterns,2], 1..num_shifts] of int: unwanted_patterns_delta;

array[1..num_employees, 1..num_days] of int: day_on_requests;

array[1..num_employees, 1..num_days] of int: day_off_requests;

array[1..(num_shifts-1),1..2] of int: shift_on_request_indices;
array[1..shift_on_request_indices[num_shifts-1 , 2], 1..num_days] of int: shift_on_requests;

array[1..(num_shifts-1),1..2] of int: shift_off_request_indices;
array[1..shift_off_request_indices[num_shifts-1 , 2], 1..num_days] of int: shift_off_requests;

% The roster to be filled in ====================
array[1..num_employees, 1..num_days] of var shift_types: roster;


% ====================================================================
% Hard Constraints


% Nurses can only be assigned shifts for which they have the appropriate skill 
constraint forall(i in 1..num_employees)(
  forall(j in 1..num_days)(
  roster[i,j] in acceptable_shifts[i]
  ));


% Cover requirements
constraint forall(j in 1..num_days)(
    forall(s in shift_types)(
        if s < num_shifts then
        sum(i in 1..num_employees)(roster[i,j] == s) == cover_requirements[j , s] else none endif));
        
%dayonrequests

constraint forall(i in 1..num_employees)(
  forall(j in 1..num_days)(
    if day_on_requests[i,j] == 1 then
    roster[i,j] != num_shifts else none endif
));

%shiftonrequests
constraint forall(i in 1..num_employees)(
  forall(j in 1..num_days)(
    roster[i,j] = shift_on_requests[i,j]
));

%shiftoffrequests
constraint forall(i in 1..num_employees)(
  forall(j in 1..num_days)(
    roster[i,j] in shift_off_requests[i,j]
));


solve satisfy;


 output [ show(roster[i,j]) ++ if j==num_days then "\n" else " " endif
       | i in 1..num_employees, j in 1..num_days ]; 