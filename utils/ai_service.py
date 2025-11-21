import requests
import json
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL


class DeepSeekAIService:
    """DeepSeek AI service for generating reports about towel renting"""

    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL

    def _call_deepseek(self, system_prompt: str, user_content: str) -> str:
        """Internal helper to call DeepSeek chat completion API"""
        if not self.api_key or self.api_key == 'your_deepseek_api_key_here':
            return "DeepSeek API key is not configured. Please set DEEPSEEK_API_KEY in .env file."

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
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_content
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

    def generate_report(self, report_data: dict) -> str:
        """Generate high-level AI report based on aggregated towel renting data"""
        prompt = self._create_prompt(report_data)
        system_prompt = (
            "You are an AI assistant that analyzes towel rental business data and "
            "provides insights and reports in a clear, professional manner."
        )
        return self._call_deepseek(system_prompt, prompt)

    def answer_question_with_data(self, question: str, data: dict) -> str:
        """
        Answer an arbitrary analytics question using raw database data.

        The data argument should already contain all relevant information
        (users, transactions, inventory, etc.) serialized to basic Python
        types so it can be converted to JSON.
        """
        # Serialize data to JSON string for the prompt
        try:
            data_json = json.dumps(data, ensure_ascii=False)
        except TypeError:
            # Fallback: if something is not JSON serializable
            data_json = str(data)

        user_content = (
            "You are given real database data for a towel rental business.\n\n"
            "IMPORTANT RULES:\n"
            "- All timestamps are in ISO 8601 format and represent UTC time.\n"
            "- The business is located in Uzbekistan and uses Asia/Tashkent time (UTC+5).\n"
            "- When the user mentions dates or words like 'today', 'yesterday', "
            "'this week', etc., interpret them using Uzbekistan time (UTC+5).\n"
            "- Answer ONLY based on the provided data. If the data is insufficient, "
            "clearly say that you cannot answer exactly and explain what is missing.\n"
            "- When referencing users, match by their name field in the data.\n\n"
            f"User question:\n{question}\n\n"
            "Here is the database data in JSON format:\n"
            f"{data_json}\n\n"
            "Now, answer the user's question as clearly as possible, in the same "
            "language as the question (Uzbek or English), and include short numeric "
            "summaries (counts, totals, etc.) where appropriate."
        )

        system_prompt = (
            "You are an analytics assistant for a towel rental business in Uzbekistan. "
            "Use ONLY the provided JSON data to answer questions. Be precise with numbers."
        )

        return self._call_deepseek(system_prompt, user_content)

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

