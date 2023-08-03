import guidance

guidance.llm = guidance.llms.OpenAI("gpt-4")

parse_intent = guidance(
'''{{#system~}}
You are a helpful assistant.
{{~/system}}
{{#user~}}
Analyze the following message, and then select the answer that best matches the user's intention.
User message: "{{user_message}}"
{{#if previous_message}}For reference, here is an excerpt from the previous message in the conversation:
"{{previous_message}}"
{{~/if}}
Answer options:
---{{#each options}}
Option {{@index}}: {{this}}{{/each}}
---
Respond only with the number (int) of your selected option, and nothing else.
{{~/user}}
{{#assistant~}}
{{gen 'answer' temperature=0 max_tokens=5}}
{{~/assistant}}
''')