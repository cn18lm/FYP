% ===============================================
% Generated code from MiniBrass, do not modify!
include "soft_constraints/mbr_types/probabilistic_type.mzn";
include "soft_constraints/mbr_types/fuzzy_type.mzn";
include "soft_constraints/mbr_types/relation-type.mzn";
include "soft_constraints/mbr_types/bool-type.mzn";
include "soft_constraints/mbr_types/cfn_type.mzn";
include "soft_constraints/mbr_types/weighted_type.mzn";
include "soft_constraints/mbr_types/cr_type.mzn";
include "soft_constraints/mbr_types/free-pvs-type.mzn";

% ---------------------------------------------------
% Overall exported predicate (and objective in case of atomic top-level PVS) : 

% ---------------------------------------------------
function ann:  postGetBetter() = mbr_postGetBetter_user1Prefs();
function ann:  postNotGetWorse() = mbr_postNotGetWorse_user1Prefs();
var int: topLevelObjective;
constraint topLevelObjective = mbr_overall_user1Prefs;

% ---------------------------------------------------
%   PVS user1Prefs
% ---------------------------------------------------
% Parameters: 
int : mbr_nScs_user1Prefs = 1; 
int : mbr_k_user1Prefs = 1000; 
array[1..mbr_nScs_user1Prefs] of int : mbr_weights_user1Prefs = [1]; 

% Decision variables: 
var int: mbr_overall_user1Prefs;
array[1..mbr_nScs_user1Prefs] of var bool: mbr_valuations_user1Prefs;
int: mbr_top_user1Prefs = 0;
constraint mbr_overall_user1Prefs = weighted_sum (mbr_valuations_user1Prefs,mbr_nScs_user1Prefs, mbr_k_user1Prefs, mbr_weights_user1Prefs);

% MiniSearch predicates: 

% Soft constraints: 
constraint mbr_valuations_user1Prefs[1] = (forall(i in 1..num_employees)(
sum(j in 1..num_days)(roster[i,j] != num_shifts) <= max_num_assignments[employee_contracts[i]]));

function ann: mbr_postGetBetter_user1Prefs() = post(is_worse_weighted(sol(mbr_overall_user1Prefs), mbr_overall_user1Prefs, mbr_nScs_user1Prefs, mbr_k_user1Prefs, mbr_weights_user1Prefs));

function ann: mbr_postNotGetWorse_user1Prefs() = post(not ( (sol(mbr_overall_user1Prefs) = mbr_overall_user1Prefs) \/ (is_worse_weighted(mbr_overall_user1Prefs, sol(mbr_overall_user1Prefs), mbr_nScs_user1Prefs, mbr_k_user1Prefs, mbr_weights_user1Prefs))));
output [ "\nValuations: mbr_overall_user1Prefs = \(mbr_overall_user1Prefs)\n"];

