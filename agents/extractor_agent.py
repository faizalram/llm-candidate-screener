from .base_agent import BaseAgent
import pdfplumber
import os

class ExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__("ExtractorAgent")

    def process(self, input_data):
        """
        Extracts relevant data from a resume PDF using Llama2.
        :param input_data: Path to the resume PDF
        :return: Extracted information as a dictionary
        """
        self.log("Starting extraction process")
        
        extracted_data = {
            "name": None,
            "skills": [],
            "education": [],
            "experience": []
        }
        
        try:
            # Extract text from all pages to capture complete information
            with pdfplumber.open(input_data) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"

            # Create a more detailed and structured prompt
            prompt = (
                "You are an expert resume parser. Extract the following information from this resume text.\n"
                "Format your response EXACTLY as shown below:\n\n"
                "Name: [Full Name]\n\n"
                "Skills: [List all technical and professional skills, separated by commas]\n\n"
                "Education:\n"
                "- [Degree/Certificate] from [Institution], [Year]\n"
                "- [Add more education entries if present]\n\n"
                "Experience:\n"
                "- [Job Title] at [Company], [Duration]\n"
                "- [Add more experience entries if present]\n\n"
                "Important: Ensure each section is properly formatted and includes all relevant information.\n\n"
                f"Resume text:\n{text[:2000]}"  # Increased text limit to capture more content
            )

            llama_response = self.ollama_request(prompt)
            
            if llama_response:
                current_section = None
                
                for line in llama_response.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.lower().startswith('name:'):
                        extracted_data['name'] = line.split(':', 1)[1].strip()
                    
                    elif line.lower().startswith('skills:'):
                        skills = line.split(':', 1)[1].strip()
                        # Clean and deduplicate skills
                        skills_list = [s.strip() for s in skills.split(',')]
                        extracted_data['skills'] = list(dict.fromkeys(filter(None, skills_list)))
                    
                    elif line.lower().startswith('education:'):
                        current_section = 'education'
                        continue
                    
                    elif line.lower().startswith('experience:'):
                        current_section = 'experience'
                        continue
                    
                    elif line.startswith('-') and current_section:
                        # Remove the leading dash and clean the entry
                        entry = line[1:].strip()
                        if entry:
                            extracted_data[current_section].append(entry)
                    
                    elif current_section and line:
                        # Handle entries without dashes
                        if not any(line.lower().startswith(x) for x in ['name:', 'skills:', 'education:', 'experience:']):
                            extracted_data[current_section].append(line)

            # Clean up the extracted data
            for key in ['skills', 'education', 'experience']:
                # Remove duplicates and empty entries
                extracted_data[key] = list(dict.fromkeys(filter(None, extracted_data[key])))
                # Clean up any remaining formatting issues
                extracted_data[key] = [item.strip(' -•') for item in extracted_data[key]]

            self.log(f"Extraction completed: {extracted_data}")
            return extracted_data
                
        except Exception as e:
            self.log(f"Error during extraction: {str(e)}", "error")
            return extracted_data