import logging
import subprocess
import json
import os
from .base_agent import BaseAgent

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("AnalyzerAgent")

    def process(self, extracted_data):
        """
        Analyze the extracted data using Llama 3 (via Ollama) to generate insights.
        :param extracted_data: Dictionary containing extracted resume details.
        :return: Analysis results as a dictionary.
        """
        self.log("Starting analysis process")

        # Prepare a more structured prompt for better analysis
        prompt = (
            "As an AI recruiter, analyze this candidate's profile and provide specific insights in the following format:\n\n"
            "Strengths: [List 3 key strengths based on skills and experience]\n"
            "Weaknesses: [List 2 potential areas for improvement]\n"
            "Suggestions: [Provide 2 specific career development suggestions]\n"
            "Confidence Score: [Rate profile completeness from 0.0 to 1.0]\n\n"
            f"Candidate Profile:\n"
            f"- Name: {extracted_data.get('name', 'N/A')}\n"
            f"- Skills: {', '.join(extracted_data.get('skills', []))}\n"
            f"- Education: {'; '.join(extracted_data.get('education', []))}\n"
            f"- Experience: {'; '.join(extracted_data.get('experience', []))}\n"
        )

        try:
            llama_response = self.ollama_request(prompt)
            
            if llama_response:
                return self.parse_llama_response(llama_response)
            else:
                self.log("No response from Llama", "error")
                return {
                    'strengths': [],
                    'weaknesses': [],
                    'suggestions': [],
                    'confidence_score': 0.0
                }
            
        except Exception as e:
            self.log(f"Analysis error: {str(e)}", "error")
            return {
                'strengths': [],
                'weaknesses': [],
                'suggestions': [],
                'confidence_score': 0.0
            }

    def parse_llama_response(self, response):
        """
        Parse the response from Llama into structured analysis results.
        """
        analysis_results = {
            'strengths': [],
            'weaknesses': [],
            'suggestions': [],
            'confidence_score': 0.0
        }

        try:
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if line.lower().startswith('strengths:'):
                    current_section = 'strengths'
                    items = line.split(':', 1)[1].strip()
                    analysis_results['strengths'] = [item.strip() for item in items.split(',')]
                elif line.lower().startswith('weaknesses:'):
                    current_section = 'weaknesses'
                    items = line.split(':', 1)[1].strip()
                    analysis_results['weaknesses'] = [item.strip() for item in items.split(',')]
                elif line.lower().startswith('suggestions:'):
                    current_section = 'suggestions'
                    items = line.split(':', 1)[1].strip()
                    analysis_results['suggestions'] = [item.strip() for item in items.split(',')]
                elif line.lower().startswith('confidence score:'):
                    try:
                        score = float(line.split(':', 1)[1].strip())
                        analysis_results['confidence_score'] = min(max(score, 0.0), 1.0)
                    except ValueError:
                        analysis_results['confidence_score'] = 0.0
                elif current_section and line:
                    analysis_results[current_section].append(line.strip())

        except Exception as e:
            self.log(f"Error parsing response: {str(e)}", "error")

        return analysis_results
