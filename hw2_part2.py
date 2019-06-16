from hw2_part1 import create_dataset
import pandas as pd
import networkx as nx
from itertools import combinations
import collections

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

def alternating_bfs(graph, root):
    #pick unmatched root and start searching
    visited, queue = set(), collections.deque([root])
    while queue: 
        vertex = queue.popleft()
        for neighbour in nx.neighbors(graph, vertex): 
            if neighbour not in visited: 
                visited.add(neighbour)
                queue.append(neighbour) 

def run_market_clearing(n):
    students, projects = create_dataset(n)
    prices = dict(map(lambda x : (x,0) , projects.keys()))
    graph = nx.Graph()
    graph.add_nodes_from(students.keys(), bipartite=0)
    graph.add_nodes_from(map(lambda x : x + 200, projects.keys()), bipartite=1)
    for student_id in students.keys():
        for project, score in students[student_id].utils.items():
            graph.add_edge(student_id, project + 200, weight=score)
    while True:
        matching = nx.max_weight_matching(graph)
        if nx.is_perfect_matching(graph,matching):
            print('perfect')
        return dict(map(lambda x : (x[1], x[0] - 200) if x[0] >= 200 else (x[0], x[1] - 200), matching)), prices
        #return matching, prices
        #find minimal constirned set

        #increase sellers prices by 1
        # if all sellers increased thier prices , then decrease their price by 1
        # try to find perfect matching agian   

def calc_total_welfare(matching_file, n) -> int:
    students, projects = create_dataset(n)
    matches = pd.read_csv(matching_file)
    return sum(map(lambda value : students[int(value[1]['sid'])].utils[value[1]['pid']], matches.iterrows()))
