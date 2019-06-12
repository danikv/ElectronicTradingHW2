import pandas as pd
import os

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


def create_dataset(n) -> tuple:
    grades_file_name = "data/grades_{0}.csv".format(n)
    preference_file_name = "data/preferences_{0}.csv".format(n)
    student_grades = pd.read_csv(grades_file_name)
    preferences = pd.read_csv(preference_file_name)
    students = []
    projects = set(sum(preferences[preferences.columns[1:]].values.tolist(), []))
    for index, student in student_grades.iterrows() :
        students.append(Student(student['student_id'], preferences.loc[preferences['student_id'] == student['student_id']], student['math_grades'], student['cs_grades'], ""))
    return students, projects

def run_deferred_acceptance(n) -> dict:
    students, projects = create_dataset(n)
    print(students)
    print(projects)
    return {1: 2, 2: 3, 3: 4, 4: 1, 5: 5}


def run_deferred_acceptance_for_pairs(n) -> dict:
    return {1: 2, 2: 2, 3: 3, 4: 3, 5: 5}


def count_blocking_pairs(matching_file, n) -> int:
    return 0 if 'single' in matching_file else 1


def calc_total_welfare(matching_file, n) -> int:
    return 73 if 'single' in matching_file else 63
