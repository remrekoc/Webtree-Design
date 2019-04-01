from __future__ import division
from __future__ import print_function
from ortools.sat.python import cp_model
import csv
import sys

FIELDS = ['ID','CLASS','CRN','TREE','BRANCH','COURSE_CEILING',
          'MAJOR','MAJOR2','SUBJ','NUMB','SEQ']
treeConvert = {1:4, 2:3, 3:2, 4:1}
branchConvert= {1:7, 2:6, 3:5, 4:4, 5:3, 6:2, 7:1}
year_to_scale = {'SENI': 6, 'JUNI': 5, 'SOPH': 4, 'FRST': 3, 'OTHER': 3}

def read_file(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=FIELDS)

        requests = {}
        yearScale = {}
        courseCeilings = {}

        #reader.next() # consume the first line, which is just column headers
        skip = True
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
                    yearScale[id] = year_to_scale[class_year]

                #NO REPEATS
                score = (1 + 4-tree) * (1 + 7-branch)
                if crn not in requests[id].keys():
                    requests[id][crn] = (tree,branch)
                elif (score > (5-requests[id][crn][0])*(8-requests[id][crn][1])):
                    requests[id][crn] = (tree,branch)

                if crn not in courseCeilings:
                    courseCeilings[crn] = int(row['COURSE_CEILING'])

    return  requests, courseCeilings, yearScale

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

    requests, courseCeilings, yearScale = read_file(sys.argv[1])
    num_classes = {}
    model = cp_model.CpModel()

    #VARIABLES
    studentAssign = {}
    for id in requests.keys():
        studentAssign[id] = []
        for crn in requests[id].keys():
            studentAssign[id].append((crn,
                (5-requests[id][crn][0])*(8-requests[id][crn][1]),
                model.NewBoolVar('studentAssign%iid%icrn' % (id, crn))))

    #CONSTRAINTS
        #1. students can have 2-4 classes
    for id in studentAssign.keys():
        model.Add(sum(studentAssign[id][tup][2]
                for tup in range(0, len(studentAssign[id])) ) <=4)
        if (len(studentAssign[id]) > 2):
            model.Add(sum(studentAssign[id][tup][2]
                for tup in range(0, len(studentAssign[id])) ) >=2)
        else:
            model.Add(sum(studentAssign[id][tup][2]
                for tup in range(0, len(studentAssign[id])) ) >=1)

        #2. class size cannot be bigger than the ceiling
    classSizes = {}
    for id in studentAssign.keys():
        for tup in range(0, len(studentAssign[id])):
            crn = studentAssign[id][tup][0]
            if crn not in classSizes:
                classSizes[crn] = 0
            classSizes[crn] += studentAssign[id][tup][2]
            model.Add(classSizes[crn] <= courseCeilings[crn])

    #THE OBJECTIVE FUNCTION
    model.Maximize(sum(yearScale[id] * studentAssign[id][t][1] * studentAssign[id][t][2]
        for id in studentAssign.keys()
        for t in range(0, len(studentAssign[id])) ))

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

    # Statistics.
    print()
    print('Statistics')
    print('  - Happiness = %i' % solver.ObjectiveValue())
    print('  - wall time       : %f s' % solver.WallTime())

    # for id in studentAssign.keys():
    #     print()
    #     print('ID: %d' % id)
    #     for tup in range(0, len(studentAssign[id])):
    #         crn = studentAssign[id][tup][0]
    #         if solver.Value(studentAssign[id][tup][2]):
    #             score = studentAssign[id][tup][1]
    #             tup = ''.join(str(requests[id][crn]))
    #             print(tup + ' -> ' + str(score))

    #How to find num illegal trees?


#can make illegal trees -> quantify how many illegal trees <- for paper
#for project find flaws, find way to quantify

if __name__ == '__main__':
    main()
