import logging
from .base_agent import BaseAgent

class ScreenerAgent(BaseAgent):
    def __init__(self):
        super().__init__("ScreenerAgent")

    def process(self, analysis_results, matched_jobs):
        """
        Screen the candidate based on analysis results and matched jobs.
        :param analysis_results: Dictionary containing analysis results from AnalyzerAgent.
        :param matched_jobs: List of matched jobs from MatcherAgent.
        :return: Screening results as a dictionary.
        """
        self.log("Starting screening process")

        # Prepare a prompt to generate screening scores
        prompt = (
            "You are an AI recruiter. Based on the candidate's analysis and job matches, provide scores for the following categories on a scale of 0 to 1:\n"
            "- Qualification Alignment Score\n"
            "- Experience Relevance Score\n"
            "- Skills Match Score\n"
            "- Potential Red Flags Score\n\n"
            f"Candidate Analysis:\n"
            f"- Strengths: {', '.join(analysis_results.get('strengths', []))}\n"
            f"- Weaknesses: {', '.join(analysis_results.get('weaknesses', []))}\n"
            f"- Suggestions: {', '.join(analysis_results.get('suggestions', []))}\n"
            f"- Confidence Score: {analysis_results.get('confidence_score', 0.0)}\n\n"
            "Matched Jobs:\n"
        )

        for job in matched_jobs:
            prompt += (
                f"\nJob Title: {job.get('job_title', 'Unknown')}\n"
                f"Match Score: {job.get('confidence_score', 0.0)}\n"
                f"Reasoning: {job.get('reasoning', 'N/A')}\n"
            )

        prompt += (
            "\nProvide the scores in this format:\n"
            "Qualification Alignment Score: [0.0 to 1.0]\n"
            "Experience Relevance Score: [0.0 to 1.0]\n"
            "Skills Match Score: [0.0 to 1.0]\n"
            "Potential Red Flags Score: [0.0 to 1.0]\n"
        )

        try:
            llama_response = self.ollama_request(prompt)

            if llama_response:
                return self.parse_llama_response(llama_response)
            else:
                self.log("No response from Llama", "error")
                return self.default_response()

        except Exception as e:
            self.log(f"Screening error: {str(e)}", "error")
            return self.default_response()

    def parse_llama_response(self, response):
        """
        Parse the response from Llama into structured screening results.
        """
        screening_results = {
            "qualification_alignment_score": 0.0,
            "experience_relevance_score": 0.0,
            "skills_match_score": 0.0,
            "potential_red_flags_score": 0.0,
        }

        try:
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if line.lower().startswith("qualification alignment score:"):
                    screening_results["qualification_alignment_score"] = self.extract_score(line)
                elif line.lower().startswith("experience relevance score:"):
                    screening_results["experience_relevance_score"] = self.extract_score(line)
                elif line.lower().startswith("skills match score:"):
                    screening_results["skills_match_score"] = self.extract_score(line)
                elif line.lower().startswith("potential red flags score:"):
                    screening_results["potential_red_flags_score"] = self.extract_score(line)

        except Exception as e:
            self.log(f"Error parsing response: {str(e)}", "error")

        return screening_results

    def extract_score(self, line):
        """
        Extract a numeric score from a line of text.
        """
        try:
            score = float(line.split(":")[1].strip())
            return max(0.0, min(score, 1.0))  # Ensure score is between 0 and 1
        except ValueError:
            self.log(f"Error extracting score from line: {line}", "error")
            return 0.0

    def default_response(self):
        """
        Return a default response in case of errors.
        """
        return {
            "qualification_alignment_score": 0.0,
            "experience_relevance_score": 0.0,
            "skills_match_score": 0.0,
            "potential_red_flags_score": 0.0,
        }

# Example usage
if __name__ == "__main__":
    screener_agent = ScreenerAgent()

    candidate_profile = {
        "name": "Jane Doe",
        "skills": ["Python", "Machine Learning", "Data Analysis"],
        "education": ["Master's in Data Science"],
        "experience": ["Data Scientist at XYZ Corp"]
    }

    job_description = {
        "title": "Senior Data Scientist",
        "skills": ["Python", "Machine Learning", "SQL", "Big Data"],
        "education": "Master's in Data Science",
        "experience": "5+ years of data science experience"
    }

    screening_results = screener_agent.screen_candidate(candidate_profile, job_description)
    print("Screening Results:", screening_results)
