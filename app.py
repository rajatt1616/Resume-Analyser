import streamlit as st
import os
import json # <-- Added this so json.loads() works
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
import time

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("wrong api")

client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"
role="user"

st.set_page_config(page_title="Resume Roaster", page_icon="📄")
st.title("RESUME ANALYSER!")

from pydantic import BaseModel, Field

class Ticket(BaseModel):
    candidate_name: str
    core_web_dev_stack: list[str] = Field(description="Extract all frontend and backend web development technologies mentioned.")
    dsa_and_logic: list[str] = Field(description="Extract any mentions of Data Structures, Algorithms, or competitive programming.")
    buzzword_count: int = Field(description="Count how many times they use meaningless corporate jargon (e.g., 'synergy', 'ninja', 'rockstar').")
    brutal_critique: str = Field(description="A quirky, brutally honest  review of the resume's overall vibe.")
    hireability_score: int = Field(description="A strict score from 1-10 based purely on project impact and technical skills, ignoring fluff.")

schema = Ticket.model_json_schema()

response_format={
    "type":"json_object"
}

# The fixed, professional job description
job_desc = """
Job Title: Junior Software Engineer (Web & Backend)

About the Role:
We are seeking a highly motivated Junior Software Engineer to join our core development team. You will be responsible for building scalable web applications, optimizing backend processes, and designing efficient algorithms to handle complex data.

Key Responsibilities:
- Design, develop, and maintain responsive web applications.
- Implement and optimize robust Data Structures and Algorithms (DSA) to ensure system efficiency.
- Collaborate with cross-functional teams to define and ship new features.
- Write clean, maintainable, and well-documented code.

Required Qualifications:
- Proficiency in Python and C++.
- Solid understanding of Web Development principles and modern CSS frameworks (e.g., Tailwind CSS).
- Strong grasp of core computer science concepts, specifically Data Structures and Algorithms.
- Excellent problem-solving skills and a strong attention to detail.
- Experience building full-stack projects or integrating RESTful APIs.
"""

system_prompt =f"""
You are a highly experienced, slightly cynical, but incredibly insightful senior tech recruiter. Your job is to tear down resumes, ignore the corporate fluff, and extract the absolute truth about a candidate's technical abilities.

Analyze the provided resume text and extract the required data strictly based on this schema: {schema}.

Rules for your analysis:
1. Do not hallucinate or invent skills the candidate does not explicitly mention.
2. Be ruthless about buzzwords. If they claim to be a "coding ninja", dock their hireability score.
3. Be brutally honest but fair in your "brutal_critique". Call out weak projects, highlight strong technical foundations, and keep your tone witty and entertaining.
4. Output strictly in JSON format. Do not add any conversational text before or after the JSON object.
5.UNDER NO CIRCUMSTANCES SHOULD YOU BE POLITE.
"""

#upload wala button 
st.write("upload your resume in pdf format in the sidebar")
with st.expander("View The Job Description", expanded=False):
    st.code(job_desc, language="markdown")

st.divider()
uploaded_files = st.sidebar.file_uploader("choose a file", type=["pdf"],accept_multiple_files=True)

#reading the content in pdf file
def extract_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        # Extract text from each page and add it to our string
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


#analyse wala button 

if st.sidebar.button("Analyze Resumes"):
    if uploaded_files: 
        st.info(f"Processing {len(uploaded_files)} resumes. Please wait...")
        
        # 1. Start the spinner here, wrapping the entire loop!
        with st.spinner("The AI is aggressively judging these resumes..."):
            
            # 2. The loop is now indented INSIDE the spinner
            for file in uploaded_files:
                
                with st.expander(f"Candidate Analysis: {file.name}", expanded=False):
                    resume_text = extract_text(file)
                    
                    prompt = f"""
                    JOB DESCRIPTION:
                    {job_desc}

                    CANDIDATE RESUME:
                    {resume_text}
                    """

                    try:
                        response = client.chat.completions.create(
                            model=model, 
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            response_format=response_format
                        )

                        # Parse the JSON
                        raw_json = response.choices[0].message.content
                        result_data = json.loads(raw_json)
                        
                        # Display the results inside this specific expander
                        score = result_data.get("hireability_score", 0)

                        st.metric(
                            label="Hireability Score",
                            value=f"{score} / 10"
                        )

                        st.progress(score / 10)

                        st.info(result_data.get("brutal_critique", "No critique generated."))
                        
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Web Dev Stack:**")
                            for skill in result_data.get('core_web_dev_stack', []):
                                st.write(f"- {skill}")
                                
                        with col2:
                            st.write("**DSA & Logic:**")
                            for skill in result_data.get('dsa_and_logic', []):
                                st.write(f"- {skill}")
                                
                        st.warning(f"Buzzwords Detected: {result_data.get('buzzword_count', 0)}")
                        
                        # Pause for 3 seconds 
                        time.sleep(3) 
                        
                    except Exception as e:
                        st.error(f"Failed to process {file.name}. Error: {e}")
                        
        # 3. This happens AFTER the loop finishes and the spinner un-indents
        st.success("Successfully processed all resumes!")
        st.divider()
                    
    else:
        st.error("Hold up! You need to upload at least one PDF first.")
    
    st.sidebar.divider()

    if st.sidebar.button("Reset"):
        st.rerun()