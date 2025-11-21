# AI integration

The repository ships with a local template-based summary generator (`ai/summaries.py`). To plug an external LLM:

1. Implement `SummaryGenerator` protocol with `for_postmortem` and `for_status_page`.
2. Keep secrets outside the repo (environment variables or vault). Do not hard-code keys.
3. Transform `CorrelationResult` into a prompt and call the chosen API respecting data protection policies.

Example skeleton:
```python
import os
from openai import OpenAI
from ru_mobile_outage_correlator.ai.summaries import SummaryGenerator

class OpenAISummary(SummaryGenerator):
    def __init__(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def for_postmortem(self, result):
        prompt = f"Сформулируй постмортем: {result}"
        return self.client.responses.create(model="gpt-4.1", input=prompt).output_text

    def for_status_page(self, result):
        prompt = f"Сформулируй статус: {result}"
        return self.client.responses.create(model="gpt-4.1", input=prompt).output_text
```

Always inform stakeholders before sending production data to third-party services.
