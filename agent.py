from typing import TypedDict

from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    question: str
    reponse: str
    type_question: str


def analyse_node(state):
    print("Analyse de la question...")
    return state


def greeting_node(state):
    state["reponse"] = "Bonjour ! Comment puis-je vous aider ?"
    return state


def calculatrice_node(state):
    state["reponse"] = "Résultat du calcul"
    return state


def reponse_node(state):
    question = state["question"]
    state["reponse"] = f"Votre question est : {question}"
    return state


def decision_node(state):
    question = state["question"]

    if "bonjour" in question.lower():
        state["type_question"] = "salutation"
    elif "+" in question:
        state["type_question"] = "calcul"
    else:
        state["type_question"] = "documentation"

    return state


# Création du workflow
workflow = StateGraph(AgentState)

workflow.add_node("analyse", analyse_node)
workflow.add_node("reponse", reponse_node)
workflow.add_node("salutation", greeting_node)

workflow.set_entry_point("analyse")

workflow.add_edge("analyse", "reponse")
workflow.add_edge("salutation", END)

# Compilation de l'agent
agent = workflow.compile()

# Exécution
resultat = agent.invoke(
    {
        "bonjour": "Votre question est : {question}"
    }
)

print(resultat)