from enum import Enum
from tabulate import tabulate
import copy
import subprocess
from datetime import datetime

class Day(Enum):
    """
    An Enum class representing day of the week and hours available to complete tasks each day.
    """

    TODAY = [-1] # special case for daily tasks
    MONDAY = [0, 5]
    TUESDAY = [1, 4]
    WEDNESDAY = [2, 5]
    THURSDAY = [3, 5]
    FRIDAY = [4, 3]
    SATURDAY = [5, 12]
    SUNDAY = [6, 12]

class Task:
    """
    A class representing tasks.

    Attributes:
        name (str): Task name
        duration (int): Duration to complete task
        dayDue (Day): Day of the week the task is due
        weekendOnly (bool): True if task can only be completed on weekends
        splittable (bool): True if task can be completed in segments
        complete (bool): True if task has been completed for the week
        neighbors (list): List of task neighbors for topological sorting
        value (int): The value of a task, based on how when it is due. A task due on the same day has a value of 7, whereas a task due in 7 days has a value of 1. Initializes to 7, since some tasks are daily.
        priority (int): The priority level of a task, from 1-5.

    """

    def __init__(self, name, duration, dayDue, weekendOnly, splittable, complete, priority):
        """
        Initialize a new task.

        Args:
            name (str): Task name
            duration (int): Duration to complete task
            dayDue (Day): Day of the week the task is due
            weekendOnly (bool): True if task can only be completed on weekends
            splittable (bool): True if task can be completed in segments
            complete (bool): True if task has been completed for the week
            priority (int): The priority level of a task, from 1-5.
        """

        self.name = name
        self.duration = duration
        self.dayDue = dayDue # if due TODAY, indicates it is a daily task
        self.weekendOnly = weekendOnly
        self.splittable = splittable
        self.complete = complete
        self.neighbors = []
        self.value = 7
        self.priority = priority

        if priority > 5:
            priority = 5
        if priority < 1:
            priority = 1
    
    def displayData(self):
        """
        Return essential task data that can be used for display.

        Returns:
            list: Name, duration, and day due of task
        """

        return [self.name, self.duration, self.dayDue.name]

def print_array(A):
    """
    A helper function for debugging/testing to print a list of lists as a formatted array.

    Args:
        A (list): list of lists containing data
    """

    for i in range(len(A)):
        print(A[i])
    print('\n')

def zero_one_knapsack(time, tasks, day): 
    """
    A function using the zero-one knapsack algorithm to calculate the optimal set of tasks to complete on a given day.
    Weight is equivalent to the duration of the task.
    Value scales inversely to the number of days remaining to complete the task.

    Args:
        time (int): Number of hours available to work on tasks
        tasks (list): The set of available tasks to choose from
        day (int): A number representing the day of the week it is

    Returns:
        list: The optimal set tasks to complete.
    """

    cols = time
    rows = len(tasks)

    memo = [[0]*(cols+1) for i in range(rows + 1)] # create memoization array to store values
    optimized_tasks = [[[]]*(cols+1) for i in range(rows + 1)] # create memoization array to store tasks

    for i in range(rows):
        for j in range(1, time + 1):

            optimized_tasks[i+1][j] = optimized_tasks[i][j] # initialize a row's values to the previous row's

            if tasks[i].duration > j:
                memo[i + 1][j] = memo[i][j]

            else:
                # update value of tasks that are not daily based on what day they are due
                if tasks[i].dayDue.value[0] != -1:
                    tasks[i].value = 7 + day - tasks[i].dayDue.value[0]
                
                # multiply task value by task priority to calculate weighted value
                new_res = max(memo[i][j], memo[i][j - tasks[i].duration] + (tasks[i].priority*tasks[i].value))
                
                # update array of tasks if necessary
                if new_res != memo[i][j] and tasks[i] not in optimized_tasks[i][j - tasks[i].duration]:
                        optimized_tasks[i+1][j] = optimized_tasks[i][j - tasks[i].duration] + [tasks[i]]

                memo[i + 1][j] = new_res

    res = optimized_tasks[rows][cols] # return last cell in the array

    return res

def fractional_knapsack(time, tasks, day):
    """
    Greedy knapsack approach to the task-scheduling problem that allows for fractions of tasks to be completed.

    Args:
        time (int): Number of hours available to work on tasks
        tasks (list): The set of available tasks to choose from
        day (int): A number representing the day of the week it is

    Returns:
        list: The optimal set tasks to complete.
    """

    # modify a copy of tasks for fractional approach
    processed_tasks = copy.deepcopy(tasks)

    # update value of non-daily tasks based on what day they are due
    for x in processed_tasks:
        if x.dayDue.value[0] != -1:
            x.value = 7 + day - x.dayDue.value[0]

    processed_tasks.sort(key=lambda x:(x.priority*x.value/x.duration), reverse = True) # sort by weighted value in decreasing order

    optimized_tasks = []
    time_remaining = time

    for task in processed_tasks:
        if task.duration < time_remaining:
            task.complete = True
            optimized_tasks.append(task)
            time_remaining -= task.duration
        elif task.duration == time_remaining:
            task.complete = True
            optimized_tasks.append(task)
            break
        else:
            task.duration = time_remaining
            if "_PARTIAL" not in task.name:
                task.name = task.name + "_PARTIAL" # mark that a fraction of a task is completed
            optimized_tasks.append(task)
            break
    
    return optimized_tasks

def split_processing(tasks):
    """
    A function to create new task objects for a given task that can be split into segments.

    Args:
        tasks (list): The current set of all tasks

    Returns:
        tasks (list): The processed set of tasks with splittable tasks having been divided into x new Task objects with a duration of 1, where x is the duration of the original splittable task
    """

    for task in tasks:
        if task.splittable == True and task.duration > 1:
            for i in range(task.duration - 1):
                newTask = copy.deepcopy(task)
                newTask.name = task.name + "_" + str(i + 1)
                newTask.duration = 1
                newTask.splittable = False

                ''' 
                Add each new task to the neighbors list of the previous task in the same category.
                Used for topological sorting of tasks to maintain ordering in the task schedule.
                e.g. If splitting up Task into three parts, then Task_0 -> Task_1 -> Task_2
                '''
                if i == 0:
                    task.neighbors.append(newTask)
                else:
                    tasks[-1].neighbors.append(newTask)
                tasks.append(newTask)
            task.name = task.name + "_0"
            task.duration = 1
    
    return tasks

def weekly_schedule(tasks, knapsack):
    """
    A function to produce a full week's schedule of tasks.

    Args:
        tasks (list): The list of tasks available to choose from
        knapsack (function): The knapsack approach to be used (zero-one or fractional)
    
    Returns:
        list: A list of lists containing each day's schedule for the full week.
    """

    sched = []

    # delineate tasks that can be completed on any day from those that are weekend only
    tasks.sort(key = lambda x: x.weekendOnly)
    index = 0
    for i in range(len(tasks)):
        if tasks[i].weekendOnly == True:
            index = i
            break
        else:
            index = -1
    
    week_tasks = tasks[:index]

    # determine schedule for each day of the week
    for day in Day:
        if day.name == "TODAY":
            continue
        
        if day.name != "SATURDAY" and day.name != "SUNDAY":
            daily_schedule = knapsack(day.value[1], week_tasks, day.value[0])
        else:
            daily_schedule = knapsack(day.value[1], tasks, day.value[0])

        for task in daily_schedule: # remove completed weekly tasks from list of all tasks
            # update duration remaining for fractionally completed tasks
            if task.name[-8:] == "_PARTIAL" and task.dayDue.name != "TODAY":
                name = task.name[:-8]

                for i in tasks:
                    if name in i.name:
                        i.duration -= task.duration
                        if "_PARTIAL" not in i.name:
                            i.name += "_PARTIAL"
                    if i.duration == 0:
                        i.complete = True
                        tasks.remove(i)
                        if i in week_tasks:
                            week_tasks.remove(i)

            elif task.dayDue.name != "TODAY":
                for i in tasks:
                    if task.name == i.name:
                        task.complete = True
                        i.complete = True
                        tasks.remove(i)
                for j in week_tasks:
                    if task.name == j.name:
                        week_tasks.remove(j)
        
        daily_schedule = topological_sort(daily_schedule, []) # sort tasks in the daily schedule
        sched.append(daily_schedule) 

    return sched

def displayAllTasks(tasks):
    """
    A helper function for debugging to display key data for all tasks in a list.

    Args:
        tasks (list): A list of Task objects
    """
    for task in tasks:
        print(task.displayData())

def display(tasks, schedules):
    """
    A function to display formatted task schedules for the week.

    Args:
        tasks (list): A list of all possible tasks
        schedules (list): A list of lists containing all daily schedules
    """

    # create a timestamped text file
    timestamp = str(datetime.now())[:-7]
    filename = "schedule" + timestamp + ".txt"
    file = open(filename, "a") 

    titles = ["Task", "Duration (Hours)", "Day Due"]

    # determine which daily and weekly tasks cannot be completed
    remaining = [x for x in tasks if x.complete == False]
    daily = [x for x in tasks if x.dayDue.value[0] == -1]
    week_daily = [x for x in daily if x.weekendOnly == False]

    # create a table of tasks for each day
    for day in Day:
        if day.name == "TODAY":
            continue
        
        if day.name != "SATURDAY" or day.name != "SUNDAY":
            remaining_daily = week_daily
        else:
            remaining_daily = daily

        schedule = []
        for task in schedules[day.value[0]]:

            remaining_daily = [x for x in remaining_daily if task.name not in x.name]

            task_info = task.displayData()

            if task.dayDue.value[0] != -1 and task.dayDue.value[0] < day.value[0]: # check if a weekly task is scheduled to be completed late
                task_info[2] += " - LATE"
            schedule.append(task_info)
        
        file.write("\n" + day.name + '\n')
        file.write(tabulate(schedule, headers = titles, tablefmt = "simple_grid") + "\n\n")
        
        file.write("UNFINISHED DAILY TASKS:\n")
        for i in remaining_daily:
            file.write(str(i.duration) + " hour(s) of " + i.name + ", due " + i.dayDue.name + "\n")
    
    file.write("\n\nUNFINISHED WEEKLY TASKS:\n\n")

    for i in remaining:
        file.write(str(i.duration) + " hour(s) of " + i.name + ", due " + i.dayDue.name + "\n")

    file.close()

    # open the schedules file on the OS
    subprocess.run(['open', filename], check = True)

def initTasks():
    """
    Initialize the tasks that need to be completed.

    returns:
        list: All initialized tasks
    """

    shower = Task("Shower", 1, Day.TODAY, False, False, None, 3)
    dinner = Task("Dinner", 1, Day.TODAY, False, False, None, 2)
    break_task = Task("Break", 1, Day.TODAY, False, False, None, 1)
    algo_homework = Task("Algorithms Homework", 6, Day.FRIDAY, False, True, False, 5)
    networks_homework = Task("Networks Homework", 3, Day.WEDNESDAY, False, True, False, 5)
    cleaning = Task("Cleaning", 2, Day.SUNDAY, False, True, False, 2)
    groceries = Task("Groceries", 2, Day.FRIDAY, False, False, False, 4)
    social = Task("Social Life", 2, Day.SUNDAY, False, True, False, 1)
    career = Task("Career", 2, Day.SUNDAY, False, False, False, 3)
    readings = Task("Assigned Readings", 4, Day.SUNDAY, False, True, False, 2)
    breakfast = Task("Breakfast", 1, Day.TODAY, True, False, None, 1)
    lunch = Task("Lunch", 1, Day.TODAY, True, False, None, 2)
    clerical = Task("Miscellaneous Tasks", 2, Day.SATURDAY, True, False, False, 2)
    workout = Task("Exercise", 1, Day.SUNDAY, False, False, False, 1)

    # assign neighbors after initializing all tasks
    dinner.neighbors.append(shower)
    cleaning.neighbors.append(shower)
    groceries.neighbors.append(lunch)
    career.neighbors.append(lunch)
    breakfast.neighbors.extend([lunch, groceries, algo_homework, networks_homework, readings, clerical, career, cleaning])
    lunch.neighbors.extend([dinner, social, break_task])
    workout.neighbors.append(dinner)

    tasks = [dinner, shower, break_task, algo_homework, networks_homework, cleaning, groceries, social, career, readings, breakfast, lunch, clerical, workout]

    return tasks

def topological_sort(tasks, visited):
    """
    Topologically sort the DAG of tasks based on neighbors lists.
    Recursive sub-function dfs_visit conducts a depth-first search.

    Args:
        tasks (list): A list of Task objects (vertices)
        visited (list): An empty list to keep track of visited vertices
    
    Returns:
        list: The topologically sorted tasks.
    """

    def dfs_visit(node, visited):
        for neighbor in node.neighbors:
            if neighbor not in visited and neighbor in tasks:
                dfs_visit(neighbor, visited)
        visited.insert(0, node)
    
    visited = []
    for i in tasks:
        if i not in visited:
            dfs_visit(i, visited)
    
    return visited

def main():
    tasks = initTasks()

    while True:
        query = input("How would you like to organize your tasks this week?\n"
                        "Enter 1 for traditional 0-1 knapsack\n"
                        "Enter 2 for split 0-1 knapsack\n"
                        "Enter 3 for fractional knapsack\n"
                        "Enter x to exit\n")
        if query == '1':
            schedule = weekly_schedule(tasks, zero_one_knapsack)
            display(tasks, schedule)
            break
        if query == '2':
            tasks = split_processing(tasks)
            schedule = weekly_schedule(tasks, zero_one_knapsack)
            display(tasks, schedule)
            break
        if query == '3':
            schedule = weekly_schedule(tasks, fractional_knapsack)
            display(tasks, schedule)
            break
        if query == 'x':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid input. Try again.")

if __name__ == "__main__":
    main()