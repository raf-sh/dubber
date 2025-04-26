import json
import os

class Processor:
    """Base class for all processors in the pipeline"""
    def __init__(self, config):
        self.config = config
        self.name = self.__class__.__name__
        
    def process(self, data=None):
        """Process data and return result"""
        raise NotImplementedError("Each processor must implement process()")
        
    def save_output(self, data, filename):
        """Save processor output to file"""
        file_path = os.path.join(self.config.output_path, f"{self.name}_{filename}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def load_output(self, filename):
        """Load previously saved output"""
        file_path = os.path.join(self.config.output_path, f"{self.name}_{filename}")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None