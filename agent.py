import importlib
import time
from typing import TypedDict

from docx import Document
from langgraph.graph import END, StateGraph
import requests  # <-- Assurez-vous que cette ligne est collée au bord gauche
from pypdf import PdfReader

# =====================================================
# ETAT
# =====================================================

class AgentState(TypedDict):
    question: str
    reponse: str
    type_question: str
    historique: str


# =====================================================
# LECTURE DES DOCUMENTS
# =====================================================

def txt_reader(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "Fichier introuvable."


def pdf_reader(path):
    try:
        lecteur = PdfReader(path)
        contenu = ""

        for page in lecteur.pages:
            texte = page.extract_text()
            if texte:
                contenu += texte + "\n"

        return contenu

    except Exception:
        return "Fichier introuvable."


def docx_reader(path):
    try:
        doc = Document(path)
        contenu = ""

        for p in doc.paragraphs:
            contenu += p.text + "\n"

        return contenu

    except Exception:
        return "Fichier introuvable."


# =====================================================
# OLLAMA
# =====================================================

def llm_local(prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=data)
        return response.json()["response"]
    except Exception as e:
        return f"Erreur de connexion à Ollama : {e}"


# =====================================================
# NOEUDS
# =====================================================

def analyse_node(state):
    print("[LOG] Analyse :", state["question"])
    return state


def greeting_node(state):
    state["reponse"] = "Bonjour ! Comment puis-je vous aider ?"
    return state


def calculatrice_node(state):
    try:
        # Note : eval() comporte des risques de sécurité, préférez ast.literal_eval pour de la production
        resultat = eval(state["question"])
        state["reponse"] = str(resultat)
    except Exception:
        state["reponse"] = "Calcul impossible."
    return state


def reponse_node(state):
    state["reponse"] = "Je ne comprends pas votre demande."
    return state


def txt_reader_node(state):
    contenu = txt_reader("documents/rh.txt")
    prompt = f"""
Historique :
{state["historique"]}

Contexte :
{contenu}

Question :
{state["question"]}

Réponse :
"""
    state["reponse"] = llm_local(prompt)
    return state


def pdf_reader_node(state):
    contenu = pdf_reader("documents/formation.pdf")
    prompt = f"""
Historique :
{state["historique"]}

Contexte :
{contenu}

Question :
{state["question"]}

Réponse :
"""
    state["reponse"] = llm_local(prompt)
    return state


def docx_reader_node(state):
    contenu = docx_reader("documents/procedure.docx")
    prompt = f"""
Historique :
{state["historique"]}

Contexte :
{contenu}

Question :
{state["question"]}

Réponse :
"""
    state["reponse"] = llm_local(prompt)
    return state


def documentation_node(state):
    prompt = f"""
Historique :
{state["historique"]}

Question :
{state["question"]}

Réponse :
"""
    state["reponse"] = llm_local(prompt)
    return state


# =====================================================
# ROUTEUR
# =====================================================

def route_question(state):
    question = state["question"].lower()

    if any(op in question for op in ["+", "-", "*", "/"]):
        return "calcul"

    if ".pdf" in question or "formation" in question:
        return "pdf"

    if ".docx" in question or "procedure" in question:
        return "docx"

    if ".txt" in question or "rh" in question:
        return "txt"

    if "document" in question:
        return "documentation"

    if "bonjour" in question or "salut" in question:
        return "salutation"

    return "reponse"


# =====================================================
# WORKFLOW
# =====================================================

workflow = StateGraph(AgentState)

workflow.add_node("analyse", analyse_node)
workflow.add_node("calculatrice", calculatrice_node)
workflow.add_node("salutation", greeting_node)
workflow.add_node("txt_reader", txt_reader_node)
workflow.add_node("pdf_reader", pdf_reader_node)
workflow.add_node("docx_reader", docx_reader_node)
workflow.add_node("documentation", documentation_node)
workflow.add_node("reponse", reponse_node)

workflow.set_entry_point("analyse")

workflow.add_conditional_edges(
    "analyse",
    route_question,
    {
        "calcul": "calculatrice",
        "pdf": "pdf_reader",
        "docx": "docx_reader",
        "txt": "txt_reader",
        "documentation": "documentation",
        "salutation": "salutation",
        "reponse": "reponse",
    },
)

workflow.add_edge("calculatrice", END)
workflow.add_edge("pdf_reader", END)
workflow.add_edge("docx_reader", END)
workflow.add_edge("txt_reader", END)
workflow.add_edge("documentation", END)
workflow.add_edge("salutation", END)
workflow.add_edge("reponse", END)

agent = workflow.compile()


# =====================================================
# BOUCLE PRINCIPALE (Exécutée uniquement en script direct)
# =====================================================

if __name__ == "__main__":
    memoire = []

    print("===== Agent documentaire =====")
    print("Tapez 'quit' pour quitter.\n")

    while True:
        question = input("Vous : ")

        if question.lower() == "quit":
            break

        historique = "\n".join(memoire)
        debut = time.time()

        resultat = agent.invoke(
            {
                "question": question,
                "reponse": "",
                "type_question": "",
                "historique": historique,
            }
        )

        fin = time.time()
        reponse = resultat["reponse"]

        print("\nAssistant :", reponse)
        print(f"Temps : {fin - debut:.2f} s\n")

        memoire.append(f"Utilisateur : {question}")
        memoire.append(f"Assistant : {reponse}")
