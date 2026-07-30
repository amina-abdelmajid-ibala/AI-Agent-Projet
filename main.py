from agent import agent
from pydantic import BaseModel
from fastapi import FastAPI
app = FastAPI()
@app.get("/bonjour")
def bonjour():
    return {
    "message": "Bonjour"
    }
@app.get("/status")
def status():
    return {
    "status": "OK"
    }
@app.get("/info")
def info():
    return {
    "application": "Agent IA",
    "version": "1.0"
    }
@app.get("/utilisateur/{nom}")
def utilisateur(nom):
    return {
    "message": f"Bonjour {nom}"
    }
def accueil():
    return {
    "message":
    "Bienvenue dans l'Agent IA"
    }
class QuestionRequest(BaseModel):
    question: str
@app.post("/question")
def poser_question(request: QuestionRequest):
    resultat = agent.invoke(
        {
            "question": request.question,
            "reponse": "",
            "type_question": "",
            "historique": ""  # Optionnel : vous pourrez y connecter une vraie mémoire plus tard
        }
    )
    return resultat