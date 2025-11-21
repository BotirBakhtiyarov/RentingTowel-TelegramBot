import requests
import json
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL


class DeepSeekAIService:
    """DeepSeek AI service for generating reports about towel renting"""

    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL

    def generate_report(self, report_data: dict) -> str:
        """Generate AI report based on towel renting data"""
        
        if not self.api_key or self.api_key == 'your_deepseek_api_key_here':
            return "DeepSeek API key is not configured. Please set DEEPSEEK_API_KEY in .env file."

        prompt = self._create_prompt(report_data)
        
        try:
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an AI assistant that analyzes towel rental business data and provides insights and reports in a clear, professional manner."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', 'Failed to generate report.')
            else:
                return f"API Error: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Error generating AI report: {str(e)}"

    def _create_prompt(self, report_data: dict) -> str:
        """Create prompt for AI based on report data"""
        
        given_towels = report_data.get('given_towels', 0)
        taken_towels = report_data.get('taken_towels', 0)
        total_transactions = report_data.get('total_transactions', 0)
        start_date = report_data.get('start_date', '')
        end_date = report_data.get('end_date', '')

        prompt = f"""
Analyze the following towel rental business data and provide a comprehensive report with insights:

Period: {start_date} to {end_date}

Statistics:
- Towels Given (Rented Out): {given_towels} pieces
- Towels Taken (Returned): {taken_towels} pieces
- Total Transactions: {total_transactions}

Please provide:
1. Summary of the rental activity
2. Key trends and patterns
3. Analysis of towel flow (given vs taken)
4. Business insights and recommendations
5. Any notable observations

Format the response in a clear, professional manner suitable for business reporting.
"""

        return prompt


# Global instance
ai_service = DeepSeekAIService()

