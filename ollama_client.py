import requests

# Adresse du serveur Ollama
OLLAMA_HOST = "http://192.168.1.25:11434"  # Adresse IP de votre PC
MODEL = "mistral:latest"                           # Modèle installé


def list_models():
    """
    Affiche les modèles disponibles sur le serveur Ollama.
    """
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
        resp.raise_for_status()

        models = resp.json().get("models", [])

        print("Modèles disponibles :")

        if not models:
            print("Aucun modèle trouvé.")
            return []

        for model in models:
            print("-", model["name"])

        return models

    except requests.exceptions.RequestException as e:
        print("Erreur de connexion :", e)
        return []


def generate(prompt, model=MODEL):
    """
    Génère une réponse avec l'API generate.
    """
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        resp.raise_for_status()

        return resp.json()["response"]

    except requests.exceptions.RequestException as e:
        return f"Erreur : {e}"


def chat(messages, model=MODEL):
    """
    Conversation avec l'API chat.
    """
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )

        resp.raise_for_status()

        return resp.json()["message"]["content"]

    except requests.exceptions.RequestException as e:
        return f"Erreur : {e}"


if __name__ == "__main__":

    print("=" * 50)
    print("Connexion au serveur Ollama")
    print("=" * 50)

    list_models()

    print("\n" + "=" * 50)
    print("Test generate()")
    print("=" * 50)

    reponse = generate("Donne-moi un fait intéressant sur les océans.")
    print(reponse)

    print("\n" + "=" * 50)
    print("Test chat()")
    print("=" * 50)

    messages = [
        {
            "role": "user",
            "content": "Bonjour ! Quel modèle utilises-tu ?",
        }
    ]

    reponse = chat(messages)

    print(reponse)