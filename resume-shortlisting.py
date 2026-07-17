import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("wrong api")

client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"
role="user"


# structuring it in json format

from pydantic import BaseModel,Field

class Ticket(BaseModel):
    candidate_name: str
    core_web_dev_stack: list[str] = Field(description="Extract all frontend and backend web development technologies mentioned.")
    dsa_and_logic: list[str] = Field(description="Extract any mentions of Data Structures, Algorithms, or competitive programming.")
    buzzword_count: int = Field(description="Count how many times they use meaningless corporate jargon (e.g., 'synergy', 'ninja', 'rockstar').")
    brutal_critique: str = Field(description="A quirky, brutally honest one-sentence review of the resume's overall vibe.")
    hireability_score: int = Field(description="A strict score from 1-10 based purely on project impact and technical skills, ignoring fluff.")


schema = Ticket.model_json_schema()

response_format={
    "type":"json_object"
}

system_prompt =f"""

You are a highly experienced, slightly cynical, but incredibly insightful senior tech recruiter. Your job is to tear down resumes, ignore the corporate fluff, and extract the absolute truth about a candidate's technical abilities.

Analyze the provided resume text and extract the required data strictly based on this schema: {schema}.

Rules for your analysis:
1. Do not hallucinate or invent skills the candidate does not explicitly mention.
2. Be ruthless about buzzwords. If they claim to be a "coding ninja", dock their hireability score.
3. Be brutally honest but fair in your "brutal_critique". Call out weak projects, highlight strong technical foundations, and keep your tone witty and entertaining.
4. Output strictly in JSON format. Do not add any conversational text before or after the JSON object.
"""


message_system = {
    "role":"system",
    "content":system_prompt
}



resume_text = """
Rajat Tyagi 
Web Developer & DSA Specialist

Summary: 
I am a passionate coding ninja looking to leverage synergy in scalable solutions. As a rockstar developer, I thrive in fast-paced environments where I can disrupt traditional paradigms.

Skills: 
Python, C++, JavaScript, HTML, CSS, Tailwind CSS, LangChain, Streamlit.

Projects:
- AI Q&A Chatbot: Built a fully functional chatbot utilizing LangChain, Streamlit, and the Groq API for lightning-fast inference.
- Uno Game GUI: Engineered a complete Uno game in Python using Pygame, handling complex deck shuffling and state logic.
- Virtual Fan Simulator: Developed an interactive physics-based fan simulation using HTML, JS, and advanced Tailwind CSS for momentum and speed controls.

Experience:
- Actively grinding Data Structures and Algorithms in C++ to optimize problem-solving capabilities solved more than 70 questions with an active streak of 50+ days. 
"""

user_prompt = f"""
Here is the candidate's resume text. Please analyze it and extract the data:

{resume_text}
"""




message = {
    "role":role ,
    "content":user_prompt
}

messages= [message_system , message]






response=client.chat.completions.create(model=model , messages=messages , response_format=response_format , temperature=2)

answer = response.choices[0].message.content
# print(answer)


# reading the json file

# reading the json file
ticket = Ticket.model_validate_json(answer)

print(f"Candidate: {ticket.candidate_name}")
print(f"Tech Stack: {ticket.core_web_dev_stack}")
print(f"DSA Skills: {ticket.dsa_and_logic}")
print(f"Buzzword Count: {ticket.buzzword_count}")
print(f"Critique: {ticket.brutal_critique}")
print(f"Score: {ticket.hireability_score}/10")

