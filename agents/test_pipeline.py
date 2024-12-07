from extractor_agent import ExtractorAgent
from analyzer_agent import AnalyzerAgent
from matcher_agent import MatcherAgent
from screener_agent import ScreenerAgent
import os

def main():
    # Initialize all agents
    extractor = ExtractorAgent()
    analyzer = AnalyzerAgent()
    matcher = MatcherAgent()
    screener = ScreenerAgent()
    
    # Path to the sample resume PDF and job list JSON
    sample_pdf = os.path.join("data/dummy_resumes", "rama.pdf")
    job_list_path = os.path.join("data", "job_list.json")
    
    if os.path.exists(sample_pdf):
        print(f"\nProcessing resume: {sample_pdf}\n")
        
        # Step 1: Extract data
        print("Step 1: Extracting data...")
        extracted_data = extractor.process(sample_pdf)
        print("\nExtracted Data:")
        for key, value in extracted_data.items():
            print(f"\n{key.upper()}:")
            print(value)
            
        # Step 2: Analyze extracted data
        print("\nStep 2: Analyzing extracted data...")
        analysis_results = analyzer.process(extracted_data)
        print("\nAnalysis Results:")
        for key, value in analysis_results.items():
            print(f"\n{key.upper()}:")
            print(value)
        
        # Step 3: Match jobs using extracted and analyzed data
        print("\nStep 3: Matching jobs...")
        combined_data = {**extracted_data, **analysis_results}
        matched_jobs = matcher.process(combined_data, job_list_path)
        print("\nMatched Jobs:")
        for job in matched_jobs:
            print(f"Job Title: {job.get('job_title', 'Unknown')}, Match Score: {job.get('confidence_score', 0.0)}")
            if job.get('reasoning'):
                print(f"Reasoning: {job['reasoning']}\n")
        
        # Step 4: Screen candidate using analysis results and matched jobs
        print("\nStep 4: Screening candidate...")
        screening_results = screener.process(analysis_results, matched_jobs)
        print("\nScreening Results:")
        for key, value in screening_results.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    else:
        print(f"Sample resume not found at {sample_pdf}")

if __name__ == "__main__":
    main()