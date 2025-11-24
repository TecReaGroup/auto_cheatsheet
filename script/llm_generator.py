"""LLM API client for generating cheatsheet YAML files"""
import requests
from pathlib import Path


class LLMGenerator:
    """Generate cheatsheet YAML using LLM API"""
    
    def __init__(self, api_url, api_key, model):
        """
        Initialize LLM generator
        
        Args:
            api_url: OpenAI-compatible API base URL
            api_key: API key for authentication
            model: Model name to use
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.model = model
    
    def generate_cheatsheet(self, command_name, timeout=30):
        """
        Generate a cheatsheet YAML for the given command
        
        Args:
            command_name: Name of the command/tool to generate cheatsheet for
            timeout: Request timeout in seconds
            
        Returns:
            tuple: (success: bool, content: str, error: str)
        """
        if not self.api_key:
            return False, "", "API key is not configured. Please set it in Settings."
        
        if not command_name or not command_name.strip():
            return False, "", "Command name cannot be empty."
        
        prompt = self._build_prompt(command_name)
        
        try:
            response = self._call_api(prompt, timeout)
            
            if response.get("error"):
                return False, "", response["error"]
            
            content = response.get("content", "")
            if not content:
                return False, "", "Empty response from API"
            
            # Validate and clean the YAML content
            cleaned_content = self._clean_yaml_response(content)
            
            return True, cleaned_content, ""
            
        except requests.exceptions.Timeout:
            return False, "", f"Request timeout after {timeout} seconds"
        except requests.exceptions.ConnectionError:
            return False, "", "Connection error. Please check your network and API URL."
        except Exception as e:
            return False, "", f"Error: {str(e)}"
    
    def _build_prompt(self, command_name):
        """Build the prompt for LLM"""
        return f"""Generate a comprehensive cheatsheet YAML file for the "{command_name}" command/tool.

Think about the most commonly used commands and organize them into logical sections.

Output ONLY the YAML content without any markdown code blocks, explanations, or additional text.

Required format:
```yaml
filename: {command_name.lower().replace(' ', '_')}_cheatsheet
terminal_title: {command_name} Cheatsheet
sections:
  - title: Section Name
    commands:
      - command: command example
        description: What it does
      - command: another command
        description: What it does
  - title: Another Section
    commands:
      - command: more commands
        description: Description
```

Important rules:
1. filename must end with "_cheatsheet" and use lowercase with underscores
2. terminal_title should be the tool name with "Cheatsheet" suffix
3. Include 5-8 sections with relevant categories
4. Each section should have 4-8 commands
5. Commands should be practical and commonly used
6. Descriptions should be concise (under 50 characters)
7. Use proper YAML indentation (2 spaces)
8. Output ONLY the YAML, no explanations or markdown

Generate the YAML now:"""
    
    def _call_api(self, prompt, timeout):
        """
        Call the OpenAI-compatible API
        
        Returns:
            dict: {"content": str, "error": str}
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            
            if response.status_code == 401:
                return {"content": "", "error": "Invalid API key"}
            elif response.status_code == 404:
                return {"content": "", "error": "Invalid API endpoint. Check your API URL."}
            elif response.status_code != 200:
                error_msg = f"API error ({response.status_code})"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except (ValueError, KeyError):
                    pass
                return {"content": "", "error": error_msg}
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            return {"content": content, "error": ""}
            
        except Exception as e:
            return {"content": "", "error": str(e)}
    
    def _clean_yaml_response(self, content):
        """Clean the YAML response from LLM"""
        # Remove markdown code blocks if present
        content = content.strip()
        
        # Remove ```yaml and ``` markers
        if content.startswith("```yaml"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        return content
    
    def save_to_file(self, content, command_name):
        """
        Save generated content to YAML file
        
        Args:
            content: YAML content to save
            command_name: Command name for filename
            
        Returns:
            tuple: (success: bool, filepath: Path, error: str)
        """
        try:
            doc_dir = Path("./src/doc")
            doc_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename from command name
            filename = f"{command_name.lower().replace(' ', '_')}_cheatsheet.yaml"
            filepath = doc_dir / filename
            
            # Check if file already exists
            if filepath.exists():
                return False, filepath, f"File already exists: {filepath.name}"
            
            # Write content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, filepath, ""
            
        except Exception as e:
            return False, None, f"Error saving file: {str(e)}"


def test_generator():
    """Test the generator with sample data"""
    generator = LLMGenerator(
        api_url="https://api.openai.com/v1",
        api_key="test_key",
        model="gpt-4"
    )
    
    success, content, error = generator.generate_cheatsheet("kubectl")
    
    if success:
        print("Generated content:")
        print(content)
    else:
        print(f"Error: {error}")


if __name__ == "__main__":
    test_generator()