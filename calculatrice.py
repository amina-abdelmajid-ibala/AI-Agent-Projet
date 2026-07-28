from typing import TypedDict
from langgraph.graph import StateGraph, END


# -----------------------------
# Définition de l'état
# -----------------------------
class AgentState(TypedDict):
    question: str
    reponse: str
    type_question: str


# -----------------------------
# Nœuds
# -----------------------------
def analyse_node(state):
    print("Analyse de la question...")
    return state


def decision_node(state):
    question = state["question"]

    if any(op in question for op in ["+", "-", "*", "/"]):
        state["type_question"] = "calcul"
    else:
        state["type_question"] = "documentation"

    return state


def calculatrice(expression):
    return eval(expression)


def calculatrice_node(state):
    question = state["question"]

    try:
        resultat = calculatrice(question)
        state["reponse"] = f"Résultat : {resultat}"
    except Exception:
        state["reponse"] = "Expression mathématique invalide."

    return state


def reponse_node(state):
    question = state["question"]
    state["reponse"] = f"Votre question est : {question}"
    return state


# -----------------------------
# Fonction de routage
# -----------------------------
def route_question(state):
    return state["type_question"]


# -----------------------------
# Création du workflow
# -----------------------------
workflow = StateGraph(AgentState)

workflow.add_node("analyse", analyse_node)
workflow.add_node("decision", decision_node)
workflow.add_node("calcul", calculatrice_node)
workflow.add_node("documentation", reponse_node)

workflow.set_entry_point("analyse")

workflow.add_edge("analyse", "decision")

workflow.add_conditional_edges(
    "decision",
    route_question,
    {
        "calcul": "calcul",
        "documentation": "documentation",
    },
)

workflow.add_edge("calcul", END)
workflow.add_edge("documentation", END)

# -----------------------------
# Compilation
# -----------------------------
agent = workflow.compile()

# -----------------------------
# Test 1
# -----------------------------
resultat = agent.invoke(
    {
        "question": "5+5"
    }
)

print(resultat)

# -----------------------------
# Test 2
# -----------------------------
resultat = agent.invoke(
    {
        "question": "100/2"
    }
)

print(resultat)

# -----------------------------
# Test 3
# -----------------------------
resultat = agent.invoke(
    {
        "question": "Quels sont les congés annuels ?"
    }
)

print(resultat)