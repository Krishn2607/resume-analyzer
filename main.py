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

class Resumeanalyzer:
    def __init__(self,filepath):
        self.filepath=filepath
        self.content=None
        
    def load(self):
        try:
            with open(self.filepath,"r") as f:
                self.content=f.read()
            print("Resume loaded successfully!")
        except FileNotFoundError:
            print("Error: Resume file not found!")
        except Exception as e:
            print(f"Something went wrong: {e}")
            
    def display(self):
        if self.content:
            print(self.content)
        else:
            print("No resume loaded yet!")
        
analyzer=Resumeanalyzer("sample_resume.txt")
analyzer.load()
analyzer.display()

bad=Resumeanalyzer("fake_file.txt")
bad.load()