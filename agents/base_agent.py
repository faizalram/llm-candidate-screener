import subprocess
import logging
import os

class BaseAgent:
    """
    Base class for AI agents in the recruiter agency app.
    Provides shared functionality such as logging and interaction with Ollama (Llama3).
    """
    def __init__(self, name):
        """
        Initialize the agent with a name and set up logging.
        :param name: Name of the agent (e.g., 'ExtractorAgent')
        """
        self.name = name
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """
        Set up a logger for the agent.
        :return: Logger instance
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('[%(name)s] %(levelname)s: %(message)s'))
        logger.addHandler(handler)
        return logger

    def log(self, message, level="info"):
        """
        Log a message with the specified level.
        :param message: Message to log
        :param level: Logging level ('info', 'debug', 'error', etc.)
        """
        if level == "info":
            self.logger.info(message)
        elif level == "debug":
            self.logger.debug(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.warning(message)

    def handle_error(self, error):
        """
        Handle errors that occur during processing.
        :param error: Exception instance
        """
        self.logger.error(f"An error occurred: {error}")

    def ollama_request(self, prompt):
        """
        Send a prompt to the Ollama Llama3 model and return the response.
        :param prompt: The prompt to be processed by the Ollama model
        :return: Response from Ollama
        """
        try:
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            process = subprocess.Popen(
                ['ollama', 'run', 'llama3', prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                encoding='utf-8'
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.handle_error(f"Ollama error: {stderr}")
                return None
            
            return stdout
            
        except Exception as e:
            self.handle_error(f"Error while calling Ollama Llama3: {str(e)}")
            return None
