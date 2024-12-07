from .base_agent import BaseAgent
import json
import os
import subprocess

class MatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__("MatcherAgent")

    def load_job_data(self, file_path):
        """
        Load job descriptions from a JSON file.
        :param file_path: Path to the JSON file containing job descriptions.
        :return: List of job descriptions.
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.log(f"Job file not found at: {file_path}", "error")
            return []

    def process(self, combined_data, job_list_path):
        """
        Match the resume data with job descriptions using both extracted and analyzed data.
        :param combined_data: Dictionary containing both extracted resume details and analysis results
        :param job_list_path: Path to the JSON file containing job descriptions
        :return: List of matched jobs and their respective confidence scores
        """
        job_list = self.load_job_data(job_list_path)

        self.log("Starting job matching process")

        # Prepare a more comprehensive prompt using both extracted and analyzed data
        prompt = (
            f"As an AI recruiter, match this candidate with the following jobs. Consider both the candidate's "
            f"profile and the analysis of their strengths and weaknesses.\n\n"
            f"Candidate Profile:\n"
            f"- Name: {combined_data.get('name', 'N/A')}\n"
            f"- Skills: {', '.join(combined_data.get('skills', []))}\n"
            f"- Education: {'; '.join(combined_data.get('education', []))}\n"
            f"- Experience: {'; '.join(combined_data.get('experience', []))}\n\n"
            f"Candidate Analysis:\n"
            f"- Strengths: {', '.join(combined_data.get('strengths', []))}\n"
            f"- Profile Confidence: {combined_data.get('confidence_score', 0.0)}\n\n"
            f"Available Jobs:\n"
        )

        # Add job descriptions to the prompt
        for i, job in enumerate(job_list, start=1):
            prompt += (
                f"\nJob {i}:\n"
                f"Title: {job['title']}\n"
                f"Description: {job['description']}\n"
                f"Required Skills: {', '.join(job.get('required_skills', []))}\n"
            )

        prompt += (
            "\nFor each job, provide a match score and brief explanation in this format:\n"
            "Job Title: [exact title from list]\n"
            "Match Score: [0.0 to 1.0]\n"
            "Reasoning: [brief explanation of the match]\n"
        )

        llama_response = self.ollama_request(prompt)

        if llama_response:
            return self.parse_llama_response(llama_response)
        else:
            self.log("No response from matching process", "error")
            return []

    def parse_llama_response(self, response):
        """
        Parse the response into structured job match results.
        :param response: Raw response text from Llama
        :return: List of matched jobs with scores and reasoning
        """
        matches = []
        current_job = {}

        try:
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.lower().startswith('job title:') or line.lower().startswith('title:'):
                    if current_job and 'title' in current_job:  # Save previous job if exists
                        matches.append(current_job)
                    current_job = {'title': line.split(':', 1)[1].strip()}
                elif line.lower().startswith('match score:') or line.lower().startswith('score:'):
                    try:
                        score = float(line.split(':', 1)[1].strip().split()[0])
                        current_job['confidence_score'] = min(max(score, 0.0), 1.0)
                    except ValueError:
                        current_job['confidence_score'] = 0.0
                elif line.lower().startswith('reasoning:'):
                    current_job['reasoning'] = line.split(':', 1)[1].strip()
            
            if current_job and 'title' in current_job:  # Add the last job if exists
                matches.append(current_job)
                
        except Exception as e:
            self.log(f"Failed to parse matching response: {str(e)}", "error")

        # Sort matches by confidence score in descending order
        matches.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        return matches
