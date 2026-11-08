from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from core.chrono_engine import ChronoEngine
import uuid

app = FastAPI(title="PnevmaChrono Platform")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

engine = ChronoEngine()

class StartReq(BaseModel):
    loss_score: int
    context: str = "General"

class ThoughtReq(BaseModel):
    text: str
    emotion: str
    intensity: int

class EndReq(BaseModel):
    loss_score_after: int
    action: str
    context: str = "General"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start")
def start_session(req: StartReq):
    session_id = str(uuid.uuid4())
    return engine.start_session(session_id, req.loss_score, req.context)

@app.post("/thought")
def analyze_thought(req: ThoughtReq):
    if not engine.active_sessions: return {"error": "No active session"}
    session_id = next(iter(engine.active_sessions))
    return engine.process_thought(session_id, req.text, req.emotion, req.intensity)

@app.post("/complete")
def complete_session(req: EndReq):
    if not engine.active_sessions: return {"error": "No active session"}
    session_id = next(iter(engine.active_sessions))
    return engine.complete_session(session_id, req.loss_score_after, req.action, req.context)