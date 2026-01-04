import os
from openai import OpenAI

class LLMClient:
    def __init__(self, api_key=None, provider='ollama', model=None, base_url=None):
        """
        Initialize the LLMClient.
        
        Args:
            api_key (str): The API key (required for DashScope, optional for Ollama).
            provider (str): 'dashscope' or 'ollama' (default: 'dashscope').
            model (str): Default model name to use.
            base_url (str): Base URL for OpenAI compatible APIs (e.g. Ollama).
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

        if self.provider == 'dashscope':
            try:
                import dashscope
            except ImportError:
                print("Error: dashscope package not installed. Please install it or use provider='ollama'")
                return
            
            self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
            if not self.api_key:
                print("Warning: DASHSCOPE_API_KEY not found.")
            dashscope.api_key = self.api_key
            self.model = model or 'qwen-turbo'
            
        elif self.provider == 'ollama':
            self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')
            self.api_key = 'ollama' # Dummy key for local instance
            self.model = model or os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )

    def generate(self, prompt, model=None, **kwargs):
        """
        Generate text using the specified provider and model.
        
        Args:
            prompt (str): The input prompt for text generation.
            model (str, optional): Override the default model.
            **kwargs: Additional arguments for the generation request.
            
        Returns:
            The response object (normalized if possible, or raw).
        """
        target_model = model or self.model
        
        try:
            if self.provider == 'dashscope':
                # DashScope API
                from dashscope import Generation
                response = Generation.call(
                    model=target_model,
                    prompt=prompt,
                    **kwargs
                )
                return response
                
            elif self.provider == 'ollama':
                # Standard OpenAI format for Ollama
                response = self.client.chat.completions.create(
                    model=target_model,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )
                # Normalize response structure to match what existing code might expect 
                # OR return the object. 
                # Since the existing code likely accesses response.output.text or similar, 
                # we might need to adapt.
                # Let's inspect how the caller uses it.
                # Code typically does: response.output.text for DashScope.
                # OpenAI response is: response.choices[0].message.content
                
                # We need to wrap it to look like DashScope response if we want 100% compatibility
                # or update the caller. 
                # Updating the caller `mcp_server.py` is better for long term.
                # But for now, let's return a simple structure or adapt here.
                
                class MockOutput:
                    def __init__(self, text):
                        self.text = text
                        
                class MockResponse:
                    def __init__(self, text, status_code=200):
                        self.status_code = status_code
                        self.output = MockOutput(text)
                        
                content = response.choices[0].message.content
                return MockResponse(content)

        except Exception as e:
            print(f"An error occurred during generation ({self.provider}): {e}")
            return None
