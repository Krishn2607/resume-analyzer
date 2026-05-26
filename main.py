name = "Resume Analyzer"
print(f"Welcome to {name}")

def greet_user(name):
    print(f"Hello {name}, let's analyze your resume!")

skills=["Python","SQL","Machine Learning"]
person={"name":"John","experience":2}

greet_user("Your Name")
print(skills)
print(person)

def read_file(filepath):
    try:
        with open(filepath,"r") as f:
            content=f.read()
        return content
    except FileNotFoundError:
        return "Error:File Not Found!"
    
result=read_file("sample_resume.txt")
print(result)