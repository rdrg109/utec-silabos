from unidecode import unidecode
import os
import re
import shlex
import subprocess

class Course:
    def __init__(self, id, name, page_start):
        self.id = id
        self.name = name
        self.start = page_start
        
    def __str__(self):
        return " ".join([self.id, self.start, self.name])

# List of words which need to be written in uppercase

acronyms = ['stem']

# List of recognized errors

recognized_errors = {'infomacion': 'informacion'}

def capitalize_acronyms_in_course_name(course_name):
    for word in acronyms:
        if re.search('\\b' + word + '\\b', course_name, re.IGNORECASE):
            course_name = re.sub('\\b' + word + '\\b', word.upper(), course_name)
    return course_name

def replace_ortography_errors(course_name):
    for word in recognized_errors:
        if re.search('\\b' + word + '\\b', course_name, re.IGNORECASE):
            course_name = re.sub('\\b' + word + '\\b', recognized_errors[word], course_name)
    return course_name

def get_courses_information(syllabus_book, page_range):
    courses = []
    
    output = subprocess.run(['pdfgrep', '--page-range=' + page_range, '.', syllabus_book], stdout = subprocess.PIPE)
    output = output.stdout.decode('utf-8')

    for line in iter(output.splitlines()):
        if search := re.search('([A-Z]{2}[A-Z0-9]{3,4})\.\s*([^\.]+).*?([0-9]+)', line):
            id = search.group(1)
            name = search.group(2)
            start = search.group(3)
            courses.append(Course(id, name, start))
            
    return courses

def write_commands(syllabus_book, page_range):
    if search := re.search('^([0-9]+)-([0-9]+).pdf$', syllabus_book):
        year = search.group(1)
        semester = search.group(2)
    else:
        return
    
    courses = get_courses_information(syllabus_book, page_range)

    for course in courses:
        course.name = unidecode(course.name)
        course.name = re.sub('[^a-zA-Z ]', '', course.name)
        course.name = course.name.strip().lower().capitalize()
        course.name = re.sub('\s+', '-', course.name)
        course.name = re.sub(r'\b(i(i+|v|x)?|x|v(i{0,3}))\b', lambda m: m.expand(r'\1').upper(), course.name)
        course.name = replace_ortography_errors(course.name)
        course.name = capitalize_acronyms_in_course_name(course.name)

    for idx,course in enumerate(courses):
        if idx == len(courses) - 1:
            end = 'end'
        else:
            end = str(int(courses[idx + 1].start) - 1)

        location = course.id + "-" + course.name

        if not os.path.isdir(location):
            os.mkdir(location)

        command = "pdftk {file} cat {start}-{end} output {output}".format(
            file = shlex.quote(syllabus_book),
            start = shlex.quote(course.start),
            end = shlex.quote(end),
            output = shlex.quote(location + '/' + "-".join([year, semester, 'spa-libro.pdf']))
        )

        print(command)
        os.system(command)
        
syllabi = [
    {
        'name': '2017-2.pdf',
        'page_range': '3-5'
    },
    {
        'name': '2018-1.pdf',
        'page_range': '3-5'
    },
    {
        'name': '2019-1.pdf',
        'page_range': '3-5'
    }
]

for syllabus in syllabi:
    write_commands(syllabus['name'], syllabus['page_range'])
