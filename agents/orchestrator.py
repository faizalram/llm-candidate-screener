from .base_agent import BaseAgent
from .extractor_agent import ExtractorAgent
from .analyzer_agent import AnalyzerAgent
from .matcher_agent import MatcherAgent
from .screener_agent import ScreenerAgent
from .recommender_agent import RecommenderAgent
import os

class Orchestrator:
    def __init__(self):
        """Initialize all agents and set up logging."""
        self.extractor_agent = ExtractorAgent()
        self.analyzer_agent = AnalyzerAgent()
        self.matcher_agent = MatcherAgent()
        self.screener_agent = ScreenerAgent()
        self.recommender_agent = RecommenderAgent()

    def process_resume(self, resume_path, job_list_path):
        """
        Orchestrates the entire resume processing workflow.
        :param resume_path: Path to the uploaded resume (PDF)
        :param job_list_path: Path to the job listings JSON file
        :return: Final output containing results from all agents
        """
        try:
            # Step 1: Extract data from resume
            self.extractor_agent.log("Starting resume extraction")
            extracted_data = self.extractor_agent.process(resume_path)
            if not extracted_data:
                return {"error": "Failed to extract data from resume"}

            # Step 2: Analyze extracted data
            self.analyzer_agent.log("Starting resume analysis")
            analysis_results = self.analyzer_agent.process(extracted_data)
            if not analysis_results:
                return {"error": "Failed to analyze resume data"}

            # Step 3: Match with job listings
            self.matcher_agent.log("Starting job matching")
            combined_data = {**extracted_data, **analysis_results}
            matched_jobs = self.matcher_agent.process(combined_data, job_list_path)
            if not matched_jobs:
                return {"error": "Failed to match jobs"}

            # Step 4: Screen candidate
            self.screener_agent.log("Starting candidate screening")
            screening_results = self.screener_agent.process(analysis_results, matched_jobs)
            if not screening_results:
                return {"error": "Failed to screen candidate"}

            # Step 5: Generate recommendations
            self.recommender_agent.log("Starting recommendation generation")
            recommendations = self.recommender_agent.recommend(
                analysis_results, screening_results, matched_jobs
            )
            if not recommendations:
                return {"error": "Failed to generate recommendations"}

            # Aggregate all results
            final_output = {
                "extracted_data": extracted_data,
                "analysis_results": analysis_results,
                "matched_jobs": matched_jobs,
                "screening_results": screening_results,
                "recommendations": recommendations,
            }

            return final_output

        except Exception as e:
            error_message = f"Error in Orchestrator: {str(e)}"
            self.extractor_agent.log(error_message, "error")
            return {"error": error_message}


def main():
    """Example usage of the Orchestrator"""
    orchestrator = Orchestrator()
    
    # Define paths
    resume_path = os.path.join("data", "dummy_resumes", "rama.pdf")
    job_list_path = os.path.join("data", "job_list.json")
    
    # Process resume
    if os.path.exists(resume_path) and os.path.exists(job_list_path):
        results = orchestrator.process_resume(resume_path, job_list_path)
        
        # Print results in a structured way
        if "error" in results:
            print(f"Error: {results['error']}")
        else:
            print("\n=== Extracted Data ===")
            for key, value in results["extracted_data"].items():
                print(f"\n{key.upper()}:")
                print(value)

            print("\n=== Analysis Results ===")
            for key, value in results["analysis_results"].items():
                print(f"\n{key.upper()}:")
                print(value)

            print("\n=== Matched Jobs ===")
            for job in results["matched_jobs"]:
                print(f"\nJob Title: {job.get('title', 'Unknown')}")
                print(f"Match Score: {job.get('confidence_score', 0.0)}")
                if job.get('reasoning'):
                    print(f"Reasoning: {job['reasoning']}")

            print("\n=== Screening Results ===")
            for key, value in results["screening_results"].items():
                print(f"{key.replace('_', ' ').title()}: {value}")

            print("\n=== Recommendations ===")
            for key, value in results["recommendations"].items():
                print(f"{key.replace('_', ' ').title()}: {value}")
    else:
        print(f"Error: Resume file not found at {resume_path} or job list not found at {job_list_path}")


if __name__ == "__main__":
    main()
