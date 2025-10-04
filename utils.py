import base64
import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

# Load environment variables
load_dotenv(".env.local", override=True)


class ScoreWithReasoning(BaseModel):
    score: int
    reasoning: str


class CandidateEvaluation(BaseModel):
    name: str
    filename: str
    technical_skills: ScoreWithReasoning
    experience: ScoreWithReasoning
    industry_relevance: ScoreWithReasoning
    education: ScoreWithReasoning
    overall_fit: ScoreWithReasoning
    total_score: int
    key_strengths: List[str]
    concerns: List[str]


class RankedCandidate(BaseModel):
    name: str
    score: int
    ranking_reason: str
    recommendation: str  # Hire/Strong Consider/Interview/Pass


class ResumeEvaluationResults(BaseModel):
    candidates: List[CandidateEvaluation]
    final_ranking: List[RankedCandidate]
    total_candidates_evaluated: int
    top_recommendation: str
    ready_for_interview: List[str]
    notes: str = ""  # Optional notes for any issues


def pdf_to_base64(pdf_path: str) -> str:
    """Convert PDF file directly to base64 string."""
    with open(pdf_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()
        base64_data = base64.b64encode(pdf_data).decode("utf-8")
        return base64_data


def load_text_file(file_path: str) -> str:
    """Load text content from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def get_resume_files(resumes_dir: str = "resumes") -> List[Path]:
    """Get all PDF files from the resumes directory."""
    resumes_path = Path(resumes_dir)
    if not resumes_path.exists():
        raise FileNotFoundError(f"Resumes directory '{resumes_dir}' not found")

    pdf_files = list(resumes_path.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in '{resumes_dir}' directory")

    return pdf_files


def prepare_resume_inputs(pdf_files: List[Path]) -> List[Dict[str, Any]]:
    """Prepare resume files as OpenAI API input format."""
    resume_inputs = []

    for pdf_file in pdf_files:
        base64_data = pdf_to_base64(str(pdf_file))
        resume_input = {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "filename": pdf_file.name,
                    "file_data": f"data:application/pdf;base64,{base64_data}",
                }
            ],
        }
        resume_inputs.append(resume_input)

    return resume_inputs


def call_openai_api(
    guidance_prompt: str, job_description: str, resume_inputs: List[Dict[str, Any]]
) -> tuple[ResumeEvaluationResults, object]:
    """Make API call to OpenAI with all resumes and get evaluation."""

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    # Prepare the full prompt
    full_prompt = f"""
{guidance_prompt}

## JOB DESCRIPTION:
{job_description}

## YOUR TASK:
Please evaluate each of the resume PDFs provided against this job description. Follow the evaluation format specified in the guidance above.
"""

    # Build the input array
    input_messages = [
        {"role": "developer", "content": [{"type": "input_text", "text": full_prompt}]}
    ]

    # Add all resume inputs
    input_messages.extend(resume_inputs)

    try:
        response = client.responses.parse(
            model="gpt-5",
            input=input_messages,
            text_format=ResumeEvaluationResults,
            reasoning={"effort": "high", "summary": "auto"},
            text={"verbosity": "high"},
        )

        # Return both the parsed output and the full response for reasoning access
        return response.output_parsed, response

    except Exception as e:
        raise Exception(f"OpenAI API call failed: {str(e)}")


def setup_environment():
    """Setup and validate environment."""

    # Check if .env.local exists
    env_file = Path(".env.local")
    if not env_file.exists():
        raise FileNotFoundError(
            ".env.local file not found. Please copy .env.example to .env.local and add your OpenAI API key"
        )

    # Load and validate API key
    load_dotenv(".env.local", override=True)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "sk-proj-your-openai-key":
        raise ValueError("Please set a valid OPENAI_API_KEY in your .env.local file")

    return api_key
