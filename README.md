# CB-CTT
CB-CTT problem solving using ALNS + MaxSAT hybrid algorithm


## Problem definition

Course timetabling (CTT) consists of the weekly scheduling of the lectures of a set of university courses within a given number of rooms and time periods, satisfying various con-
straints due to conflicts and other features. Among the different versions of CTT, one distinguishing feature is whether student enrollments are available or not. In the negative case, conflicts between courses are set according to the curricula, which can be either published by the university or designed based on experience from previous years. In the case of this problem conflicts are based on curricula, and the resulting problem is named Curriculum-Based Course Timetabling (CB-CTT).

#### Hard constraints

- Lectures: all the lectures of a course must be scheduled and they must be assigned
to distinct time periods;
- Room occupancy: each room can host at most one lecture per time period;
- Conflicts: lectures of courses belonging to the same curriculum or taught by the
same teacher cannot be scheduled in the same time period;
- Availabilities: unavailable time periods for the teacher of the course cannot be used
for scheduling a lecture of that course.

#### Soft constraints

- Minimum number of working days: for each course, a penalty is given for each day
below the minimum number of working days;
- Curriculum compactness: it is preferable that the lectures of a curriculum are con-
secutive, without any empty time period in between; thus, a penalty is given for each isolated lecture, i.e., a lecture not adjacent to any other lecture of the same curriculum in the same day;
- Room capacity: a penalty is given for each student that cannot have a seat in the room assigned to the course lecture;
- Room stability: it is preferable that a course is always taught in the same room, thus, a penalty is given for each additional room used for a course.

#### Objective function

The goal is the minimization of the weighted sum (according to given weights) of multiple objective functions, representing the costs for the violation of the soft constraint.

## Solvers

### ALNS

In LNS an initial solution has to be created first. At each iteration, parts of the incumbent solution are destroyed and subsequently repaired. New solutions are accepted according to a certain criterion to become the new incumbent solution. The algorithm keeps track of the best solution, i.e., the solution with the least soft penalties among the solutions with the smallest
number of unscheduled lectures. In the end the best solution found is returned. The Adaptive Large Neighborhood Search (ALNS) heuristic extends the LNS by allowing multiple destroy and repair methods (multiple neighborhoods) to be used within the same search. Each destroy/repair method is assigned a weight that controls how often the particular method is attempted during the search. The weights are adjusted dynamically as the search progresses using recorded performance of the neighborhoods.

Simulated Annealing (SA) is used as a technique inside ALNS for exploring the neighborhood and solution evaluator.

### Destroy operators

- Worst courses removal: removes <b><i>l</i></b> lectures of courses that increase cost the most
- Worst curricula removal: removes <b><i>l</i></b> lectures of courses in currucula that increase cost the most
- Random lecture removal: removes <b><i>l</i></b> lectures randomly
- Random day/period removal: removes <b><i>l</i></b> lectures in random timeslots
- Random room/day removal: removes <b><i>l</i></b> lectures in random days and rooms
- Restricted room/course removal: removes <b><i>l</i></b> lectures of courses that are schedules in room which are restricted
- Random teacher removal: removes <b><i>l</i></b> lectures of courses of random teachers

### Repair operator

#### Max-SAT

A complete SAT solver is a tool that, given a set of clauses, either finds a model for it or reports unsatisfiability.
There exist several optimization versions of the SAT problem. In MaxSAT, the aim is to find a model that maximizes the number of satisfied clauses. In Partial MaxSAT the input consists of two sets of clauses, the hard ones and soft ones, and the problem is to find a model for the hard clauses that maximizes the number of satisfied soft clauses. In Weighted (Partial) MaxSAT each soft clause has a weight and the aim is to minimize the sum of the weights of the falsified soft clauses.
Because Max-SAT is called as repair method from ALNS algorithm, it takes as input a fixed schedule (the solution after destroy operator is applied), and a list with lectures that are removed (after destroying solution with any of the destroy operators), and the clauses are generated taken into consideration the fixed lectures.
The result returned from Max-SAT solver is then evaluated and decided if it's accepted or not, and if it qualifies as the global best.

## Technologies

The main algorithm is developed in Python 3.6 in Linux environment. 
Max-SAT is developed in Java and is consumed by ALNS as a black-box, executed as external JAR process.

## Parameters

Parameters are configured to their optimal values in <i>parameters.py</i> file, which are updated in experiemts scripts, to match the instances and iterations.

## Instances format

The program should work with two instances format, <b><xml></b> and <b>ectt</b> .
