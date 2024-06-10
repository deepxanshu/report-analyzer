from fastapi import HTTPException
from dotenv import load_dotenv
import requests
import os
from crewai import Agent, Task, Crew
import fitz 

load_dotenv()
class CustomTool:
    name: str
    description: str

    def run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement this!")

class PDFReadTool(CustomTool):
    name: str = "PDFReadTool"
    description: str = "Extracts text from PDF files."

    def _run(self, pdf_content: bytes) -> str:
        pdf_text = ""
        with fitz.open(stream=pdf_content, filetype="pdf") as doc:
            for page in doc:
                pdf_text += page.get_text()
        return pdf_text

pdf_read_tool = PDFReadTool()

class MedicalAnalysisTool(CustomTool):
    name: str = "Medical Analysis Tool"
    description: str = "Analyzes the text of medical reports to generate summaries and recommendations."

    def _run(self, report_text: str) -> dict:
        api_key = os.getenv("OPENAI_API_KEY")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "gpt-3.5-turbo-0613",
            "messages": [
                {"role": "system", "content": "You are a top-tier medical AI assistant. Analyze the following blood report and provide a concise and relevant summary. Make sure to highlight any abnormal findings and give actionable recommendations."},
                {"role": "user", "content": report_text}
            ]
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content']
            return {"summary": summary, "recommendations": summary}
        else:
            raise Exception("Failed to get a response from the API")

medical_analysis_tool = MedicalAnalysisTool()

class Agent:
    def __init__(self, role, goal, backstory, tools, verbose=False):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools
        self.verbose = verbose

    def execute_tool(self, tool_name, *args, **kwargs):
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.run(*args, **kwargs)
        raise ValueError(f"Tool {tool_name} not found")

class Task:
    def __init__(self, description, expected_output, agent, context=None):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
        self.context = context or []

class Crew:
    def __init__(self, agents, tasks, verbose=0):
        self.agents = agents
        self.tasks = tasks
        self.verbose = verbose

    def kickoff(self, **kwargs):
        context_results = {}
        for task in self.tasks:
            for ctx_task in task.context:
                if ctx_task not in context_results:
                    context_results[ctx_task] = ctx_task.agent.execute_tool(
                        ctx_task.agent.tools[0].name, **kwargs
                    )
            task_input = context_results.get(task.context[0], kwargs)
            result = task.agent.execute_tool(task.agent.tools[0].name, **task_input)
            context_results[task] = result
        return context_results.get(self.tasks[-1])

pdf_extractor = Agent(
    role='PDF Extractor',
    goal='Extract text from PDF files',
    backstory='An expert in handling and extracting text from PDF documents.',
    tools=[pdf_read_tool],
    verbose=True
)

report_analyzer = Agent(
    role='Report Analyzer',
    goal='Analyze medical reports and provide summaries',
    backstory='A medical expert with extensive knowledge in interpreting blood reports.',
    tools=[medical_analysis_tool],
    verbose=True
)

extract_text_task = Task(
    description='Extract text from the PDF blood report.',
    expected_output='Text content of the PDF',
    agent=pdf_extractor
)

analyze_report_task = Task(
    description='Analyze the extracted blood report text and provide a summary and recommendations.',
    expected_output='Summary and recommendations based on the blood report',
    agent=report_analyzer,
    context=[extract_text_task]
)

crew = Crew(
    agents=[pdf_extractor, report_analyzer],
    tasks=[extract_text_task, analyze_report_task],
    verbose=2
)

async def analyze_report_and_fetch_articles(pdf_content: bytes) -> dict:
    import ipdb; ipdb.set_trace()
    result = crew.kickoff(pdf_content=pdf_content)
    
    if not result:
        raise HTTPException(status_code=500, detail="Analysis failed.")

    return result
  