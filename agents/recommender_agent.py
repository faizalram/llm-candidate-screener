import logging
from .base_agent import BaseAgent

class RecommenderAgent(BaseAgent):
    def __init__(self):
        super().__init__("RecommenderAgent")

    def recommend(self, analysis_results, screening_results, job_matches):
        """
        Provide a final recommendation for the candidate.
        :param analysis_results: Insights from the AnalyzerAgent.
        :param screening_results: Screening results for the candidate.
        :param job_matches: List of jobs matched to the candidate.
        :return: Final recommendation as a dictionary.
        """
        self.log("Starting recommendation process")

        # Prepare the prompt for Llama 3 to synthesize recommendations
        prompt = (
            "You are an AI recruiter. Based on the candidate's analysis, screening results, "
            "and job matches, provide a detailed recommendation in the following format:\n\n"
            "Recommendation Summary: [Provide a 2-3 sentence summary of the candidate's fit for the matched roles.]\n"
            "Top Matched Job: [Select the most suitable job from the matches.]\n"
            "Additional Notes: [Provide any additional observations or suggestions.]\n\n"
            f"Candidate Analysis:\n"
            f"- Strengths: {', '.join(analysis_results.get('strengths', []))}\n"
            f"- Weaknesses: {', '.join(analysis_results.get('weaknesses', []))}\n"
            f"- Suggestions: {', '.join(analysis_results.get('suggestions', []))}\n"
            f"- Confidence Score: {analysis_results.get('confidence_score', 0.0)}\n\n"
            f"Screening Results:\n"
            f"- Qualification Alignment Score: {screening_results.get('qualification_alignment_score', 0.0)}\n"
            f"- Experience Relevance Score: {screening_results.get('experience_relevance_score', 0.0)}\n"
            f"- Skills Match Score: {screening_results.get('skills_match_score', 0.0)}\n"
            f"- Potential Red Flags Score: {screening_results.get('potential_red_flags_score', 0.0)}\n\n"
            f"Matched Jobs:\n"
            + "\n".join(
                [f"- {job['title']} ({job.get('confidence_score', 0.0)})" for job in job_matches]
            )
        )

        try:
            llama_response = self.ollama_request(prompt)

            if llama_response:
                return self.parse_llama_response(llama_response)
            else:
                self.log("No response from Llama", "error")
                return self.default_response()

        except Exception as e:
            self.log(f"Recommendation error: {str(e)}", "error")
            return self.default_response()

    def parse_llama_response(self, response):
        """
        Parse the response from Llama into a structured recommendation.
        """
        recommendation_results = {
            "recommendation_summary": "",
            "top_matched_job": "",
            "additional_notes": "",
        }

        try:
            current_section = None
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if line.lower().startswith("recommendation summary:"):
                    current_section = "recommendation_summary"
                    recommendation_results[current_section] = line.split(":", 1)[1].strip()
                elif line.lower().startswith("top matched job:"):
                    current_section = "top_matched_job"
                    recommendation_results[current_section] = line.split(":", 1)[1].strip()
                elif line.lower().startswith("additional notes:"):
                    current_section = "additional_notes"
                    recommendation_results[current_section] = line.split(":", 1)[1].strip()
                elif current_section and line:
                    recommendation_results[current_section] += f" {line.strip()}"

        except Exception as e:
            self.log(f"Error parsing response: {str(e)}", "error")

        return recommendation_results

    def default_response(self):
        """
        Return a default response in case of errors.
        """
        return {
            "recommendation_summary": "No recommendation available.",
            "top_matched_job": "N/A",
            "additional_notes": "No additional notes.",
        }

# Example usage
if __name__ == "__main__":
    recommender_agent = RecommenderAgent()

    analysis_results = {
        "strengths": ["Python programming", "Data Analysis", "Team Leadership"],
        "weaknesses": ["Limited experience with cloud platforms"],
        "suggestions": ["Learn AWS or GCP", "Improve SQL proficiency"],
        "confidence_score": 0.85,
    }

    screening_results = {
        "qualification_alignment_score": 0.9,
        "experience_relevance_score": 0.8,
        "skills_match_score": 0.85,
        "potential_red_flags_score": 0.1,
    }

    job_matches = [
        {"title": "Data Scientist", "company": "TechCorp"},
        {"title": "Machine Learning Engineer", "company": "AI Innovations"},
    ]

    recommendation = recommender_agent.recommend(analysis_results, screening_results, job_matches)
    print("Final Recommendation:", recommendation)
