from ai21 import AI21Client
from ai21.models.chat import UserMessage
import json
import os
import win32com.client as win32

myapi_key = 'INSERT_YOUR_API_KEY_HERE'
client = AI21Client(api_key=myapi_key)

with open('professors_data.json', 'r') as file:
    professors = json.load(file)

resume_path = "INSERT_RESUME_PATH_HERE"
subject = "Research Position Inquiry"
log_file = "email_log.txt"
outlook = win32.Dispatch("Outlook.Application")

def create_outlook_draft(professor, email_body):
    mail = outlook.CreateItem(0)
    mail.Subject = subject
    mail.Body = email_body
    mail.To = professor['Email']
    mail.Attachments.Add(resume_path)
    mail.Save()

def generate_email(professor, resume_text):
    prompt = f"""
    Write a professional email to Professor {professor['Name']} regarding a research position.
    Mention that you are a student with relevant experience and skills in {professor['Research Interest']}. 
    DO NOT MAKE UP ANY SKILLS THAT ARE NOT IN THE RESUME. DO NOT MAKE UP BACKGROUND; 
    Talk about how your past skills from your resume will make you a good fit for their research, but don't overly emphasize your own skills. 
    Express passion for learning about their research if it's not directly on your resume. Focus on how your skills are useful for their research. 
    If you don't meet the qualifications: {professor['Student Qualifications']}, express interest and your passion for this opportunity.
    Don't generate a subject or closing remarks; only generate the email body and keep it brief.

    Here's a brief summary of your background from the resume:
    {resume_text[:500]}
    """
    
    messages = [
        UserMessage(
            content=prompt
        )
    ]

    response = client.chat.completions.create(
        model="jamba-1.5-large",
        messages=messages,
        top_p=1.0
    )
  
    response_dict = response.to_dict()
    email_body = response_dict['choices'][0]['message']['content'].replace("\\n", "\n")
    return email_body

resume_text = """
INSERT_RESUME_DETAILS_HERE
"""

with open(log_file, "w") as log:
    for professor in professors[201:300]:
        email_body = generate_email(professor, resume_text)
        create_outlook_draft(professor, email_body)
        log.write(f"Draft email created for {professor['Name']} ({professor['Email']})\n")
        print(f"Draft email created for {professor['Name']} ({professor['Email']})")
