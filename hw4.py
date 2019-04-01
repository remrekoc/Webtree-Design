from __future__ import division
from __future__ import print_function
from ortools.sat.python import cp_model
import csv
import sys

FIELDS = ['ID','CLASS','CRN','TREE','BRANCH','COURSE_CEILING',
          'MAJOR','MAJOR2','SUBJ','NUMB','SEQ']

#returns crn of (id, tree, branch)
def findCrn(id, tree, branch, rowId, rowCrn, rowTree, rowBranch):
    for row in range(0, len(rowCrn)):
        if id == rowId[row] and tree == rowTree[row] and branch == rowBranch[row]:
            return rowCrn[row]
    return None


#returns number of students in each class
def classSize():
    classSizes = {}
    for i in range(0, len(rowCrn) ):
        if rowCrn[i] not in classSizes:
            classSizes.append(rowCrn[i])
        classSizes[rowCrn[i]]+=students[(rowId[i], rowTree[i], rowBranch[i])]
    return classSizes

def read_file(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=FIELDS)

        requests = {}
        yearPen = {}
        courseCeilings = {}

        #reader.next() # consume the first line, which is just column headers
        skip = True
        i = 0
        for row in reader:
            if skip == True:
                skip = False
            else:
                id = int(row['ID'])
                class_year = row['CLASS']
                crn = int(row['CRN'])
                tree = int(row['TREE'])
                branch = int(row['BRANCH'])

                #unique students
                if id not in requests:
                    requests[id] = {}
                    if class_year == 'SENI':
                        yearPen[id] = 6
                    elif class_year == 'JUNI':
                        yearPen[id] = 5
                    elif class_year == 'SOPH':
                        yearPen[id] = 4
                    else:
                        yearPen[id] = 3

                #NO REPEATS
                if crn not in requests[id]:
                    requests[id][crn] = (tree,branch)
                elif (tree*branch < requests[id][crn][0]*requests[id][crn][1]):
                    requests[id][crn] = (tree,branch)

                if crn not in courseCeilings:
                    courseCeilings[crn] = int(row['COURSE_CEILING'])

                i+=1
    return  requests, courseCeilings, yearPen

def main():

    if (len(sys.argv) != 2):
        print()
        print ("***********************************************************")
        print ("You need to supply a .csv file containing the WebTree data")
        print ("as a command-line argument.")
        print()
        print ("Example:")
        print ("    python baseline_webtree.py spring-2015.csv")
        print ("***********************************************************")
        print()
        return

    requests, courseCeilings, yearPen = read_file(sys.argv[1])
    num_classes = {}
    model = cp_model.CpModel()

    #VARIABLES
    studentAssign = {}
    for id in requests.keys():
        studentAssign[id] = []
        for crn in requests[id].keys():
            studentAssign[id].append((crn, requests[id][0] * requests[id][1],
                model.NewBoolVar('student_id%itree%ibranch%i' % (id, tree, branch))))

    #CONSTRAINTS
        #1. students can have 2-4 classes
    for id in studentAssign.keys():
        model.Add(sum(studentAssign[id][2] <=4))
        if (studentAssign[id].size() > 2):
            model.Add(sum(studentAssign[id][2] >=2))
        else:
            model.Add(sum(studentAssign[id][2] >=1))

        #2. class size cannot be bigger than the ceiling
    classSizes = {}
    for id in studentAssign.keys():
        for tup in studentAssign[id].keys():
            if tup[0] not in classSizes:
                classSizes[tup[0]] = 0
            classSizes[tup[0]] += studentAssign[id][2]
            model.Add(classSizes[tup[0]] <= courseCeilings[tup[0]])

    #THE OBJECTIVE FUNCTION
        #penalty ideas:
            #scale penalty by reverse year -> penalty of sr = 2*fr
                #fr = 1, soph = 1.33, jun = 1.66, sen = 2
            #penalize having less than 4 classes
                #for each class under 4, add 25
    model.Minimize(
    sum(yearPen[id] * (studentAssign[id][1] * studentAssign[id][2])
        for id in studentAssign.keys()))

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.FEASIBLE:
        print('feasible')

    elif status == cp_model.OPTIMAL:
        print('optimal')

    elif status == cp_model.INFEASIBLE:
        print('infeasible')

    elif status == cp_model.UNKNOWN:
        print('unknown')

    else:
        print('help')


    # # Statistics.
    # print()
    # print('Statistics')
    # print('  - Unhappiness = %i' % solver.ObjectiveValue())
    # print('  - wall time       : %f s' % solver.WallTime())
    #
    # for id in student_requests.keys():
    #     print()
    #     print('ID: %d' % id)
    #     for tree in trees.keys():
    #         for branch in trees[tree]:
    #             if solver.Value(students[(id, tree, branch)]):
    #                 print('(%d, %d) -> %d' % (tree, branch, findCrn(id, tree, branch, rowId, rowCrn, rowTree, rowBranch)))

#can make illegal trees -> quantify how many illegal trees <- for paper
#for project find flaws, find way to quantify
    #how many repeat classes people get

if __name__ == '__main__':
    main()
