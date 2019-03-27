from __future__ import division
from __future__ import print_function
from ortools.sat.python import cp_model


def read_file(filename):

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=FIELDS)
        student_requests = {}
        courses = {}
        reader.next() # consume the first line, which is just column headers

        for row in reader:
            id = int(row['ID'])
            class_year = row['CLASS']
            crn = int(row['CRN'])
            tree = int(row['TREE'])
            branch = int(row['BRANCH'])

            #unique students
            ids=[]
            if id not in ids:
                ids.append(id)

            #to understand which nodes are empty(CAN YOU DO THIS IN A LIST?)
            student_requests={}
            student_requests[id]+=(tree, branch)

            #the tree structure, helpful when assigning random variables
            #so that you don't add to tree 4 branch 7
            trees={1:range(1,8), 2:range(1,8), 3:range(1,8), 4:range(1,5)}

            courses[crn] = int(row['COURSE_CEILING'])

            #the data based on the row number given on the excel sheet
            #(helpful for crn-(id,tree,branch) conversion
            rowId[row]=id
            rowTree[row] = tree
            rowBranch[row] = branch
            rowCrn[row] = int(row['CRN'])

        def main():
            model = cp_model.CpModel()

        #assigns random classes
        students = {}
        for id in ids:
            for tree in trees:
                for branch in trees[key]:
                    students[(id, tree, branch)] = model.NewBoolVar('student_id%itree%ibranch%i' % (id, tree, branch))



        #CONSTRAINTS
        #students can have at most 4 classes
        for id in ids:
            model.Add(sum(students[(id, tree, branch)] for key in trees for branch in trees[key]) <=4)


        #1 cannot be assigned to a branch with no classes in it
        for id in ids:
            for key in trees:
                for branch in trees[key]:
                    if (key, branch) not in student_requests[id]:
                        model.Add(students[(id, tree, branch)] == 0)



        #this is a way to get to crn from tree, branch or id
        #this can be modified to
        def findRowNumber(id,rowId):
            for row in len(rowId):
                if id=rowId[row]:
                    return row

        #calculates the size of of class

        classSizes{}
        for rows in len(rowCrn)
            i=0
            classSizes[rowCrn[i]]+=students[(idOfStudent[i], tree[i], branch[i])]
            i++


        #class size cannot be bigger than the ceiling
        for key in classSizes:
            model.Add(classeSizes[crn] <= courses[crn])





        #THE OBJECTIVE FUNCTION(ADD PENALTY)
        model.Minimize(
        sum(tree * branch * students[(id, tree, branch)] for id in ids
            for tree in trees for branch in trees[tree]))
