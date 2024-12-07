# LLM Candidate Screener

An AI-powered resume screening and job matching system that uses Large Language Models (LLM) to analyze resumes, match candidates with job listings, and provide detailed recruitment insights.

## 🌟 Features

- **Resume Data Extraction**: Automatically extracts key information from PDF resumes
- **Candidate Analysis**: Evaluates candidate profiles with detailed strengths and weaknesses
- **Job Matching**: Matches candidates with suitable job positions using AI
- **Screening**: Provides comprehensive screening scores across multiple criteria
- **Recommendations**: Generates personalized career development suggestions

## 🏗️ Architecture

The system uses a multi-agent architecture with specialized components:

1. **ExtractorAgent**: Parses PDF resumes to extract structured data
2. **AnalyzerAgent**: Analyzes candidate profiles using LLM to identify strengths and weaknesses
3. **MatcherAgent**: Matches candidates with job listings using AI-powered comparison
4. **ScreenerAgent**: Evaluates candidates on multiple criteria
5. **Orchestrator**: Coordinates the workflow between all agents

## 🛠️ Technical Stack

- **Python**: Core programming language
- **Ollama**: Local LLM integration
- **Streamlit**: Web interface (planned)
- **PDFPlumber**: PDF processing
- **Swarm**: Agent coordination

## 📋 Prerequisites

- Python 3.8+
- Ollama installed and running locally
- PDF resume files
- Job listings in JSON format

## 📊 Output Format

The system provides structured output including:
- Extracted resume data
- Candidate analysis results
- Job matches with confidence scores
- Screening results across multiple criteria
- Career development recommendations
