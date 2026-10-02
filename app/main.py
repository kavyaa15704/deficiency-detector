"""
FastAPI backend - Step 4: one working endpoint, no auth/DB yet.

Run from the project root:
  uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs for interactive Swagger UI,
or test with Postman / curl.
"""
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import (check_connection, create_user, get_recent_predictions,
                          get_user_by_email, get_user_by_username, log_prediction)
from app.inference import recommend, valid_symptoms
from app.schemas import PredictRequest, PredictResponse, Token, UserOut, UserRegister

app = FastAPI(
    title="Deficiency Detector API",
    description="Predicts likely nutrient deficiencies from symptoms and "
                "suggests foods and recipes. Educational project - not medical advice.",
    version="0.1.0",
)

# Allow the React dev server (and later, your deployed frontend) to call this API.
# Add your production frontend URL here once deployed (e.g. Vercel).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Quick check that the server, model, and database are all up."""
    try:
        n = len(valid_symptoms())
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {
        "status": "ok",
        "symptoms_loaded": n,
        "database_connected": check_connection(),
    }


@app.get("/symptoms")
def list_symptoms():
    """All symptom names the model accepts, for building a frontend checklist."""
    return {"symptoms": sorted(valid_symptoms())}


@app.post("/register", response_model=UserOut, status_code=201)
def register(user: UserRegister):
    if get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = create_user(user.username, user.email, hash_password(user.password))
    return UserOut(id=user_id, username=user.username, email=user.email)


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Uses OAuth2PasswordRequestForm so this also works directly from
    Swagger's built-in 'Authorize' button, not just raw JSON requests."""
    user = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(user_id=str(user["_id"]), username=user["username"])
    return Token(access_token=token)


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, current_user: dict = Depends(get_current_user)):
    try:
        result = recommend(request.symptoms)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    try:
        log_prediction(result["input_symptoms"], result["predictions"],
                       user_id=current_user["user_id"])
    except Exception as e:
        print(f"WARNING: failed to log prediction to MongoDB: {e}")

    return result


@app.get("/predictions/recent")
def recent_predictions(limit: int = 10, current_user: dict = Depends(get_current_user)):
    """Only returns the logged-in user's own predictions."""
    return {"predictions": get_recent_predictions(limit=limit, user_id=current_user["user_id"])}
