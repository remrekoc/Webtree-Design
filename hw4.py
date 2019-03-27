from __future__ import division
from __future__ import print_function
from ortools.sat.python import cp_model


def read_file(filename):
    """Returns data read in from supplied WebTree data file.

    Parameters:
        filename - string containing the name of the CSV file.

    Returns:
        a) A dictionary mapping student IDs to records, where each record
           contains information about that student's WebTree requests.
        b) A dictionary mapping class years to student IDs, indicating
           which students are seniors, juniors, etc.
        c) A dictionary mapping course CRNs to enrollment capacities.
    """
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=FIELDS)
        student_requests = {}
        students_by_class = {'SENI': set([]), 'JUNI': set([]),
                             'SOPH': set([]), 'FRST': set([]),
                             'OTHER': set([])}
        courses = {}
        reader.next() # consume the first line, which is just column headers

        for row in reader:
            id = int(row['ID'])
            class_year = row['CLASS']
            crn = int(row['CRN'])
            tree = int(row['TREE'])
            branch = int(row['BRANCH'])
            if id in student_requests: # does this student already exist?
                student_requests[id].add_request(crn, tree, branch)
            else: # nope, create a new record
                s = Student(id, class_year)
                s.add_request(crn, tree, branch)
                student_requests[id] = s

            students_by_class[class_year].add(id)
            courses[crn] = int(row['COURSE_CEILING'])

    return student_requests, students_by_class, courses


def main():
    model = cp_model.CpModel()

    #CREATE VARIABLES
    studentClasses = {}
    for id in ids:
        for tree in trees:
            for branch in branches:
                students[(id, tree, branch)] = model.NewBoolVar('student_id%itree%ibranch%1' % (id, tree, branch))

    #CREATE CONSTRAINTS
    for id in ids:
        model.Add(sum(ids[(id, tree, branch)] for tree in trees for branch in branches) <=4)
        #model.Add(sum(ids[(id, tree, branch)] for tree in trees for branch in branches) >=3)
        #SHOULD WE LIMIT?

    for crn in classeSizes:
        model.Add(classeSizes[crn] <= courseCeilings[crn])

    for id in ids:
        for tree in range(0,3): #for tree 1, 2, and 3
            model.Add(if(ids[id, tree, 0] == False))
