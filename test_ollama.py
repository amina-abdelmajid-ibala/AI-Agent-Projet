import requests
def llm_local(prompt):
    url = (
    "http://localhost:11434/api/generate"
    )
    data = {
    "model": "phi3",
    "prompt": prompt,
    "stream": False
    }
    response = requests.post(
    url,
    json=data
    )
    return response.json()[
    "response"
    ]
print(
llm_local(
"Qu'est-ce qu'un Agent IA ?"
)
)
print(
llm_local("Explique le RAG simplement.")
) 
print(
llm_local("Quelle est la différence entre GPT et BERT ?")
)
print(
llm_local("Explique LangGraph.")
)