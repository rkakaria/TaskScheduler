# TaskScheduler
Simplify task scheduling and prioritize/optimize the number of tasks that can be completed.

## Description
This project aims to simplify task scheduling and to prioritize/optimize the number of tasks that can be completed. Task-scheduling manually can be a substantial mental effort when there is a lot to get done, so this project is intended to ease that responsibility.

The file Task_Scheduler.py initializes several tasks (as objects) of different durations, due dates, values, and priorities, and schedules them out for the week based on one of three approaches, chosen by the user. Some tasks are daily, and others are weekly. The program generates several tables in a text file that contain the tasks for each day in a reasonable order, and marks which tasks will be late and which will be skipped altogether. The file is generated in the same directory in which the program is run.

## Dependencies
- Python 3
- [tabulate](https://pypi.org/project/tabulate/)

## Running the Program
```python3 Task_scheduler.py```
Follow the resulting terminal prompt to choose an approach.

## Algorithmic Approach
The program presents three options for the task scheduling, all of which are based on the [knapsack problem](https://en.wikipedia.org/wiki/Knapsack_problem). Weight is substituted by the duration of each task, and value is based on the due date of a task such that a task due in 2 days is more valuable than a task due in 5 days. By nature, this means that a daily task will always be higher priority than a weekly task due the next day; however, each task is also given a priority that is used as a multiplier on the value. Each task can also be treated as the vertex of a directed acyclic graph and has a list of neighbors. 

Each approach is run once for each day of the week, and keeps track of which tasks have been completed or partially completed on a particular day so that they are not scheduled again the following day. Daily tasks are on the table for scheduling every day. There are also a few tasks that are only necessary/allowed on the weekends. 

### Approach 1: 0/1 Knapsack
The first approach is a slightly modified standard 0/1 Knapsack problem algorithm. The knapsack algorithm is modified to not only store the maximum value that can be achieved, but also which tasks make up this value. This algorithm is run for each day of the week.

### Approach 2: Split Knapsack
The second approach is a ‘split’ approach. Each task object also has a property called ‘splittable.’ If a task is splittable, this means that this task can be accomplished in multiple one-hour increments that do not necessarily need to be completed in direct succession (e.g. 2 hours of homework can be completed as 1 hour on Monday and 1 hour on Wednesday). As such, running the split approach first pre-processes tasks and creates new objects for each hour of the task (but not all multi-hour tasks are considered splittable). The 0/1 Knapsack algorithm is then run on this new list of tasks. An inherent characteristic of this approach is that the value of tasks is then ‘double-counted.’ In the above example, the 2-hour homework task may have a value of 5; after processing, two tasks will exist of 1-hour duration, each of which also has a value of 5. 

### Approach 3: Fractional Knapsack
The third approach is based on the fractional Knapsack approach. This is again slightly modified because the algorithm needs to keep track of completed and remaining fractions of a task, as we proceed to run the algorithm on several subsequent days on which that task could be completed. However, the core logic is the same. The most valuable task has the highest result for the calculation $\frac{priority \times value}{duration}$, and we sort based on this equation to run this greedy algorithm.

### Topological Sort
Before results are displayed to the user, the schedule for each day undergoes a topological sort based on the neighbors list of the tasks. This is to ensure that breakfast is always scheduled before lunch, for example. 

## Limitations
- These algorithms cannot suggest sleeping later or something similar as a way to increase the total amount of time available to complete tasks.
- This program uses a weekly approach, but certain tasks might repeat over two weeks, or a task could be due in more than 7 days, which the program does not account for.
- Tasks must be added, deleted, and modified by directly editing the code.
