from hw2_part1 import create_dataset, get_preferences
import pandas as pd
import networkx as nx
from itertools import combinations
import random
from collections import defaultdict

class Student:
    free_students = set()

    def __init__(self, sid: int, pref_list: list, math_grade, cs_grade, utils):
        self.sid = sid
        self.math_grade = math_grade
        self.cs_grade = cs_grade
        self.pref_list = pref_list
        self.project = None
        self.utils = utils
        self.pair = None

    def is_free(self):
        return bool(not self.project)

class Project:
    def __init__(self, pid):
        self.pid = pid
        self.grade_type = 'cs_grade' if pid % 2 else 'math_grade'
        self.proposals = {}
        self.main_student = None
        self.partner_student = None
        self.price = 0

    def is_free(self):
        return bool(not self.main_student)

def minimal_constrined_set(matches):
    constrined_set = set()
    for e1, e2 in combinations(matches, 2):
        if len(set(e1) & set(e2)) != 0:
            constrined_set.add(e1[1])
    return constrined_set

def is_perfect_matching(matches):
    return all(len(set(e1) & set(e2)) == 0
               for e1, e2 in combinations(matches, 2))

def number_of_higest_preferences(student):
    return len(list(filter(lambda util : util==student.utils[student.pref_list[0]] ,student.utils.values())))

def calculate_matching(students):
    previosly_selected_projects = set()
    matching = set()
    for sid, student in sorted(students.items(), key=lambda x : number_of_higest_preferences(x[1])):
        higest_preferences_size = number_of_higest_preferences(student)
        if higest_preferences_size == 1:
            matching.add((sid, student.pref_list[0] + 200))
            previosly_selected_projects.add(student.pref_list[0])
        elif len(set(student.pref_list[0:higest_preferences_size]).intersection(previosly_selected_projects)) != higest_preferences_size:
            preference_pid = set(student.pref_list[0:higest_preferences_size]).difference(previosly_selected_projects).pop()
            matching.add((sid, preference_pid + 200))
            previosly_selected_projects.add(preference_pid)
        else :
            preference_pid = set(student.pref_list[0:higest_preferences_size]).pop()
            matching.add((sid, preference_pid + 200))
            previosly_selected_projects.add(preference_pid)
    return matching

def run_market_clearing(n):
    students, projects = create_dataset(n)
    prices = dict(map(lambda x : (x,0) , projects.keys()))
    while True:
        matching = calculate_matching(students)
        if is_perfect_matching(matching):
            return dict(map(lambda x : (x[0], x[1] - 200), matching)), prices
        #find minimal constrined set
        constrined_set = minimal_constrined_set(matching)
        #increase sellers prices by 1
        for pid in constrined_set:
            prices[pid - 200] += 1
            for sid, student in students.items():
                student.utils[pid - 200] -= 1
                student.pref_list = get_preferences(student.utils)
        # if all sellers increased thier prices , then decrease their price by 1, not sure where to put that

def calc_total_welfare(matching_file, n) -> int:
    students, projects = create_dataset(n)
    matches = pd.read_csv(matching_file)
    return sum(map(lambda value : students[int(value[1]['sid'])].utils[value[1]['pid']], matches.iterrows()))
