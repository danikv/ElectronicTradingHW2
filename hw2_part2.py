from hw2_part1 import get_students_and_projects, get_preferences, convert_matching_file_to_dict, calculate_total_welfare
import pandas as pd
from itertools import combinations

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

def perfect_matching(matches):
    return all(len(set(match1).intersection(set(match2))) == 0
               for match1, match2 in combinations(matches, 2))

def get_minimal_constrined_set(matches):
    constrined_set = set()
    for match1, match2 in combinations(matches, 2):
        if len(set(match1).intersection(set(match2))) != 0:
            constrined_set.add(match1[1])
    return constrined_set

def get_higest_preferences_size(student):
    return len(list(filter(lambda util : util==student.utils[student.pref_list[0]] ,student.utils.values())))

def max_matching(students):
    selected_projects = set()
    matching = set()
    for sid, student in sorted(students.items(), key=lambda x : get_higest_preferences_size(x[1])):
        preference_pid = -1
        preferences_size = get_higest_preferences_size(student)
        if preferences_size == 1:
            preference_pid = student.pref_list[0]
            matching.add((sid, student.pref_list[0] + 1000))
            selected_projects.add(student.pref_list[0])
        elif len(set(student.pref_list[0:preferences_size]).intersection(selected_projects)) == preferences_size:
            preference_pid = set(student.pref_list[0:preferences_size]).pop()
            matching.add((sid, preference_pid + 1000))
        else:
            preference_pid = set(student.pref_list[0:preferences_size]).difference(selected_projects).pop()
            matching.add((sid, preference_pid + 1000))
        selected_projects.add(preference_pid)
    return matching

def run_market_clearing(n):
    students, projects = get_students_and_projects(n)
    prices = dict(map(lambda x : (x,0) , projects.keys()))
    while True:
        matching = max_matching(students)
        if perfect_matching(matching):
            return dict(map(lambda x : (x[0], x[1] - 1000), matching)), prices
        minimal_constrined_set = get_minimal_constrined_set(matching)
        for pid in minimal_constrined_set:
            prices[pid - 1000] += 1
            for student_obj in students.values():
                student_obj.utils[pid - 1000] -= 1
                student_obj.pref_list = get_preferences(student_obj.utils)

def calc_total_welfare(matching_file, n) -> int:
    students, projects = get_students_and_projects(n)
    return calculate_total_welfare(students, projects, convert_matching_file_to_dict(matching_file))
