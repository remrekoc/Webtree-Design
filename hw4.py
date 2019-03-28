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

        student_requests = {}
        courseCeilings = {}
        rowId = {}
        rowTree = {}
        rowBranch = {}
        rowCrn = {}

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
                if id not in student_requests:
                    student_requests[id] = {}

                student_requests[id][tree, branch] = crn

                courseCeilings[crn] = int(row['COURSE_CEILING'])

                #the data based on the row number given on the excel sheet
                #(helpful for crn-(id,tree,branch) conversion
                rowId[i]=id
                rowTree[i] = tree
                rowBranch[i] = branch
                rowCrn[i] = int(row['CRN'])
                i+=1
    return  student_requests, courseCeilings, rowId, rowTree, rowBranch, rowCrn

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

    student_requests, courseCeilings, rowId, rowTree, rowBranch, rowCrn = read_file(sys.argv[1])
    model = cp_model.CpModel()

    #the tree structure, helpful when assigning random variables
    #so that you don't add to tree 4 branch 7
    trees={1:range(1,8), 2:range(1,8), 3:range(1,8), 4:range(1,5)}

    #VARIABLES
    students = {}
    for id in student_requests.keys():
        for tree in trees.keys():
            for branch in trees[tree]:
                students[(id, tree, branch)] = model.NewBoolVar('student_id%itree%ibranch%i' % (id, tree, branch))

    #CONSTRAINTS
        #1. students can have 2-4 classes
    for id in student_requests.keys():
        model.Add(sum(students[(id, tree, branch)] for tree in trees.keys() for branch in trees[tree]) <=4)
        model.Add(sum(students[(id, tree, branch)] for tree in trees.keys() for branch in trees[tree]) >=2)

        #2. cannot be assigned to a branch with no classes in it
    for id in student_requests.keys():
        for tree in trees.keys():
            for branch in trees[tree]:
                if (tree, branch) not in student_requests[id]:
                    model.Add(students[(id, tree, branch)] == 0)

        #3. class size cannot be bigger than the ceiling
        classSizes = {}
        for i in range(0, len(rowCrn) ):
            if rowCrn[i] not in classSizes:
                classSizes[rowCrn[i]] = 0
            classSizes[rowCrn[i]]+=students[(rowId[i], rowTree[i], rowBranch[i])]
            model.Add(classSizes[rowCrn[i]] <= courseCeilings[rowCrn[i]])

        #4. Cannot have repeats


    #THE OBJECTIVE FUNCTION
        #penalty ideas: scale penalty by reverse year -> penalty of sr = 4*fr
    model.Minimize(
    sum(tree * branch * students[(id, tree, branch)] for id in student_requests.keys()
        for tree in trees for branch in trees[tree]))

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)

    # Statistics.
    print()
    print('Statistics')
    print('  - Unhappiness = %i' % solver.ObjectiveValue())
    print('  - wall time       : %f s' % solver.WallTime())

    for id in student_requests.keys():
        print()
        print('ID: %d' % id)
        for tree in trees.keys():
            for branch in trees[tree]:
                if solver.Value(students[(id, tree, branch)]):
                    print('(%d, %d) -> %d' % (tree, branch, findCrn(id, tree, branch, rowId, rowCrn, rowTree, rowBranch)))

#can make illegal trees -> quantify how many illegal trees <- for paper
#for project find flaws, find way to quantify
    #how many repeat classes people get

if __name__ == '__main__':
    main()
