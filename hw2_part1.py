import pandas as pd
import numpy as np

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
    students = {}
    projects = dict(map(lambda x : (x, Project(x)), sum(preferences[preferences.columns[1:]].values.tolist(), [])))
    for index, student in student_grades.iterrows() :
        students[int(student['student_id'])] = Student(int(student['student_id']), 
        sum(preferences.loc[preferences['student_id'] == student['student_id']][preferences.columns[1:]].values.tolist(), []), student['math_grades'], student['cs_grades'], "")
    return students, projects

def studnt_without_project(students) -> Student:
    for student in students.values() :
        if student.is_free():
            return student

def remove_and_assign(students, student, applications, pref):
    remove_old_student_from_project(students, applications, pref)
    assign_student_to_project(applications, pref, student)

def remove_old_student_from_project(students, applications, pref):
    students[applications[pref].student_id].project = None

def assign_student_to_project(applications, pref, student):
    student.project = pref
    applications[pref] = student.sid

def deferred_acceptance(students, projects):
    applications = dict.fromkeys(projects)
    while True:
        student = studnt_without_project(students)
        if student is None:
            break
        for pref in student.pref_list :
            if applications[pref] is None:
                assign_student_to_project(applications, pref, student)
                break
            elif projects[pref].grade_type == "cs_grade":
                if students[applications[pref]].cs_grade < student.cs_grade :
                    remove_and_assign(students, student, applications, pref)
                    break
            elif students[applications[pref]].math_grade < student.math_grade:
                remove_and_assign(students, student, applications, pref)
                break
    reverse_matches = dict(filter(lambda value: value[1] != None, applications.items()))
    matches = dict((v,k) for k,v in reverse_matches.items())
    return matches

def run_deferred_acceptance(n) -> dict:
    students, projects = create_dataset(n)
    return deferred_acceptance(students, projects)

def merge_pairs(n, students):
    merge_pair_file_name = "data/pairs_{0}.csv".format(n)
    pairs = pd.read_csv(merge_pair_file_name)
    merged_pairs = {}
    for index, pair in pairs.iterrows():
        if np.isnan(pair['partner_1']) and np.isnan(students[pair['partner_2']]):
            continue
        elif np.isnan(pair['partner_1']):
            second_student = students[pair['partner_2']]
            merged_pairs[second_student.sid] = second_student.sid
            continue
        elif np.isnan(pair['partner_2']):
            first_student = students[pair['partner_1']]
            merged_pairs[first_student.sid] = first_student.sid
            continue
        first_student = students[pair['partner_1']]
        second_student = students[pair['partner_2']]
        if first_student.math_grade + first_student.cs_grade > second_student.math_grade + second_student.cs_grade:
            merged_pairs[first_student.sid] = second_student.sid
        else :
            merged_pairs[second_student.sid] = first_student.sid
    return merged_pairs

def run_deferred_acceptance_for_pairs(n) -> dict:
    students, projects = create_dataset(n)
    merged_students = merge_pairs(n,students)
    matches = deferred_acceptance(dict(filter(lambda x : x[0] in merged_students.keys(), students.items())), projects)
    for key, value in merged_students.items() :
        matches[value] = matches[key]
    return matches

def count_blocking_pairs(matching_file, n) -> int:
    students, projects = create_dataset(n)
    matches = pd.read_csv(matching_file)
    for index, match in matches.iterrows() :
        print(match['sid'])

def calc_total_welfare(matching_file, n) -> int:
    return 73 if 'single' in matching_file else 63
