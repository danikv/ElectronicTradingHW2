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


def get_preferences(preferences):
    return list(map(lambda item: item[0], sorted(preferences.items(), key=lambda x : x[1], reverse=True)))

def create_dataset(n) -> tuple:
    grades_file_name = "data/grades_{0}.csv".format(n)
    preference_file_name = "data/preferences_{0}.csv".format(n)
    student_grades = pd.read_csv(grades_file_name)
    preferences = pd.read_csv(preference_file_name)
    students = {}
    projects = dict(map(lambda x : (int(x), Project(int(x))), preferences.columns[1:].values.tolist()))
    for index, student in student_grades.iterrows() :
        utils = dict(map(lambda item: (int(item[0]), int(item[1])), preferences.loc[preferences['student_id'] == student['student_id']][preferences.columns[1:]].iteritems()))
        students[int(student['student_id'])] = Student(int(student['student_id']), 
        get_preferences(utils), student['math_grades'], student['cs_grades'], utils)
    return students, projects

def studnt_without_project(students) -> Student:
    for student in students.values() :
        if student.is_free():
            return student

def remove_and_assign(students, student, applications, pref):
    remove_old_student_from_project(students, applications, pref)
    assign_student_to_project(applications, pref, student)

def remove_old_student_from_project(students, applications, pref):
    students[applications[pref]].project = None

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
    matches = dict(map(lambda item: (item[1], item[0]), filter(lambda value: value[1] != None, applications.items())))
    return matches

def run_deferred_acceptance(n) -> dict:
    students, projects = create_dataset(n)
    return deferred_acceptance(students, projects)

def merge_students(students, pair) -> tuple:
    first_student = students[pair['partner_1']]
    second_student = students[pair['partner_2']]
    if first_student.math_grade + first_student.cs_grade > second_student.math_grade + second_student.cs_grade:
        return first_student.sid, second_student.sid
    else :
        return second_student.sid, first_student.sid

def merge_pairs(n, students) -> dict:
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
        student_id, merged_student_id = merge_students(students, pair)
        merged_pairs[student_id] = merged_student_id
    return merged_pairs

def run_deferred_acceptance_for_pairs(n) -> dict:
    students, projects = create_dataset(n)
    merged_students = merge_pairs(n,students)
    matches = deferred_acceptance(dict(filter(lambda x : x[0] in merged_students.keys(), students.items())), projects)
    for key, value in merged_students.items() :
        matches[value] = matches[key]
    return matches

def count_blocking_pairs(matching_file, n) -> int:
    blocking_pairs = {}
    students, projects = create_dataset(n)
    matches = pd.read_csv(matching_file)
    for index, match in matches.iterrows() :
        first_student = students[int(match['sid'])]
        project_index = first_student.pref_list.index(match['pid'])
        if project_index > 0:
            for second_student in filter(lambda x : x is not first_student, students.values()):
                wanted_projects = first_student.pref_list[0: project_index]
                first_student_project = projects[int(match['pid'])]
                second_studnet_project = projects[int(matches[matches['sid'] == second_student.sid]['pid'])]
                if second_studnet_project.pid in wanted_projects and second_studnet_project is not first_student_project:
                    if second_studnet_project.grade_type == 'cs_grade':
                        if first_student.cs_grade > second_student.cs_grade:
                            blocking_pairs[first_student.sid] = second_student.sid
                    else:
                        if first_student.math_grade > second_student.math_grade:
                            blocking_pairs[first_student.sid] = second_student.sid
    return int(len(list(filter(lambda student: student[1] in blocking_pairs.keys(), blocking_pairs.items())))/2)

def calc_total_welfare(matching_file, n) -> int:
    students, projects = create_dataset(n)
    matches = pd.read_csv(matching_file)
    return sum(map(lambda value : students[int(value[1]['sid'])].utils[value[1]['pid']], matches.iterrows()))