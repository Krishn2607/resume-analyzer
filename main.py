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

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def talk_to(message):
    try:
        client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


result = talk_to("Hello! I am a CS student building an AI Resume Analyzer. Say hello back in one sentence!")
print(result)