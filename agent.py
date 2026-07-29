from typing import TypedDict

from docx import Document
from langgraph.graph import END, StateGraph
from pypdf import PdfReader


# ============================
# État de l'agent
# ============================
class AgentState(TypedDict):
    question: str
    reponse: str
    type_question: str


# ============================
# Lecture des fichiers
# ============================
def txt_reader(chemin_fichier):
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        return fichier.read()


def pdf_reader(chemin_fichier):
    lecteur = PdfReader(chemin_fichier)
    contenu = ""

    for page in lecteur.pages:
        texte = page.extract_text()
        if texte:
            contenu += texte + "\n"

    return contenu


def docx_reader(chemin_fichier):
    doc = Document(chemin_fichier)
    contenu = ""

    for paragraphe in doc.paragraphs:
        contenu += paragraphe.text + "\n"

    return contenu


# ============================
# Nœuds
# ============================
def analyse_node(state):
    print("Analyse de la question...")
    return state


def greeting_node(state):
    state["reponse"] = "Bonjour ! Comment puis-je vous aider ?"
    return state


def calculatrice_node(state):
    question = state["question"]

    try:
        resultat = eval(question)
        state["reponse"] = str(resultat)
    except Exception:
        state["reponse"] = "Calcul impossible."

    return state


def reponse_node(state):
    state["reponse"] = f"Votre question est : {state['question']}"
    return state


def txt_reader_node(state):
    state["reponse"] = txt_reader("documents/rh.txt")
    return state


def pdf_reader_node(state):
    state["reponse"] = pdf_reader("documents/formation.pdf")
    return state


def docx_reader_node(state):
    state["reponse"] = docx_reader("documents/procedure.docx")
    return state


def documentation_node(state):
    state["reponse"] = (
        "Documents disponibles :\n"
        "- rh.txt\n"
        "- formation.pdf\n"
        "- procedure.docx"
    )
    return state


# ============================
# Routage
# ============================
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


# ============================
# Création du workflow
# ============================
workflow = StateGraph(AgentState)

workflow.add_node("analyse", analyse_node)
workflow.add_node("reponse", reponse_node)
workflow.add_node("salutation", greeting_node)
workflow.add_node("calculatrice", calculatrice_node)
workflow.add_node("txt_reader", txt_reader_node)
workflow.add_node("pdf_reader", pdf_reader_node)
workflow.add_node("docx_reader", docx_reader_node)
workflow.add_node("documentation", documentation_node)

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

# ============================
# Compilation
# ============================
agent = workflow.compile()

# ============================
# Tests
# ============================
questions = [
    "Bonjour",
    "50+25",
    "Lis rh.txt",
    "Lis formation.pdf",
    "Lis procedure.docx",
    "Quels documents sont disponibles ?",
]

for question in questions:
    print("\n==============================")
    print("Question :", question)

    resultat = agent.invoke(
        {
            "question": question,
            "reponse": "",
            "type_question": "",
        }
    )

    print("Réponse :")
    print(resultat["reponse"])