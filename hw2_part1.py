import pandas as pd
import numpy as np
import networkx as nx

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

def get_students_and_projects(n) -> tuple:
    preferences = pd.read_csv("data/preferences_{0}.csv".format(n))
    grades = pd.read_csv("data/grades_{0}.csv".format(n))
    students = {}
    projects = dict(map(lambda x : (int(x), Project(int(x))), preferences.columns[1:].values.tolist()))
    for index, student in grades.iterrows() :
        utils = dict(map(lambda item: (int(item[0]), int(item[1])), preferences.loc[preferences['student_id'] == student['student_id']][preferences.columns[1:]].iteritems()))
        students[int(student['student_id'])] = Student(int(student['student_id']), get_preferences(utils), student['math_grades'], student['cs_grades'], utils)
    return students, projects

def get_free_student(students) -> Student:
    for student_obj in students.values() :
        if student_obj.is_free():
            return student_obj

def deferred_acceptance(students, projects):
    matching = dict.fromkeys(projects)
    while True:
        student = get_free_student(students)
        if student is None:
            return dict(map(lambda item: (item[1], item[0]), filter(lambda value: value[1] != None, matching.items())))
        for preference in student.pref_list :
            if matching[preference] is None:
                student.project = preference
                matching[preference] = student.sid
                break
            elif projects[preference].grade_type == "math_grade":
                if students[matching[preference]].math_grade < student.math_grade :
                    students[matching[preference]].project = None
                    student.project = preference
                    matching[preference] = student.sid
                    break
            elif students[matching[preference]].cs_grade < student.cs_grade:
                students[matching[preference]].project = None
                student.project = preference
                matching[preference] = student.sid
                break

def run_deferred_acceptance(n) -> dict:
    students, projects = get_students_and_projects(n)
    return deferred_acceptance(students, projects)

def merge(student1, student2) -> tuple:
    if student1.math_grade + student1.cs_grade > student2.math_grade + student2.cs_grade:
        return student1.sid, student2.sid
    else :
        return student2.sid, student1.sid

def merge_pairs(n, students) -> dict:
    merge_pair_file_name = "data/pairs_{0}.csv".format(n)
    pairs = pd.read_csv(merge_pair_file_name)
    merged_pairs = {}
    for index, pair in pairs.iterrows():
        if np.isnan(pair['partner_1']) and np.isnan(students[pair['partner_2']]):
            continue
        elif np.isnan(pair['partner_1']):
            student2 = students[pair['partner_2']]
            merged_pairs[student2.sid] = student2.sid
            continue
        elif np.isnan(pair['partner_2']):
            student1 = students[pair['partner_1']]
            merged_pairs[student1.sid] = student1.sid
            continue
        student_id, merged_student_id = merge(students[pair['partner_1']], students[pair['partner_2']])
        merged_pairs[student_id] = merged_student_id
    return merged_pairs

def run_deferred_acceptance_for_pairs(n) -> dict:
    students, projects = get_students_and_projects(n)
    merged_pairs = merge_pairs(n,students)
    merged_students = dict(filter(lambda x : x[0] in merged_pairs.keys(), students.items()))
    matches = deferred_acceptance(merged_students, projects)
    for key, value in merged_pairs.items() :
        matches[value] = matches[key]
    return matches

def get_blocking_pairs(students, projects, matching) -> list:
    blocking_pairs = []
    for sid, pid in matching.items() :
        student1 = students[sid]
        matched_project_index = student1.pref_list.index(pid)
        if matched_project_index > 0:
            for student2 in filter(lambda x : x is not student1, students.values()):
                wanted_projects = student1.pref_list[0: matched_project_index]
                student2_project = projects[matching[student2.sid]]
                if student2_project.pid in wanted_projects:
                    if student2_project.grade_type == 'cs_grade':
                        if student1.cs_grade > student2.cs_grade:
                            blocking_pairs.append((student1.sid, student2.sid))
                    else:
                        if student1.math_grade > student2.math_grade:
                            blocking_pairs.append((student1.sid, student2.sid))
    return list(filter(lambda student: (student[1], student[0]) in blocking_pairs, blocking_pairs))

def convert_matching_file_to_dict(matching_file) -> dict:
    return dict(map(lambda x: (int(x[1]['sid']), int(x[1]['pid'])), pd.read_csv(matching_file).iterrows()))

def count_blocking_pairs(matching_file, n) -> int:
    students, projects = get_students_and_projects(n)
    blocking_pairs = get_blocking_pairs(students, projects, convert_matching_file_to_dict(matching_file))
    return int(len(blocking_pairs)/2)

def calculate_total_welfare(students, projects, matching) -> int:
    total_welfare = 0
    for sid, pid in matching.items() :
        total_welfare += students[sid].utils[pid]
    return total_welfare

def calc_total_welfare(matching_file, n) -> int:
    students, projects = get_students_and_projects(n)
    return calculate_total_welfare(students, projects, convert_matching_file_to_dict(matching_file))

def part3(n):
    students, projects = get_students_and_projects(n)
    merged_students = merge_pairs(n,students)
    graph = nx.Graph()
    graph.add_nodes_from(merged_students.keys(), bipartite=0)
    graph.add_nodes_from(map(lambda x : x + 1000, projects.keys()), bipartite=1)
    for student, merged_student in merged_students.items():
        for project, score in students[student].utils.items():
            graph.add_edge(student, project + 1000, weight=score + students[merged_student].utils[project])
    matching = nx.max_weight_matching(graph)
    formated_matching = dict(map(lambda x : (x[1], x[0] - 1000) if x[0] >= 1000 else (x[0], x[1] - 1000), matching))
    for key, value in merged_students.items() :
        formated_matching[value] = formated_matching[key]
    return formated_matching