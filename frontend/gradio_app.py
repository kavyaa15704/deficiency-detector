"""
Gradio frontend for the Deficiency Detector.

Talks to the FastAPI backend over HTTP - the frontend never touches the
model, MongoDB, or Spoonacular directly. Make sure the API is running first:
  uvicorn app.main:app --reload
Then, in a second terminal:
  python frontend/gradio_app.py
"""
import requests
import gradio as gr

API_URL = "http://127.0.0.1:8000"


def api_register(username, email, password):
    if not username or not email or not password:
        return "Please fill in all fields."
    try:
        r = requests.post(f"{API_URL}/register", json={
            "username": username, "email": email, "password": password,
        }, timeout=10)
    except requests.exceptions.ConnectionError:
        return "Cannot reach the API. Is uvicorn running?"

    if r.status_code == 201:
        return "Registered! Go to the Login tab to sign in."
    return f"Error: {r.json().get('detail', 'registration failed')}"


def api_login(username, password):
    if not username or not password:
        return None, "Please enter a username and password."
    try:
        r = requests.post(f"{API_URL}/login", data={
            "username": username, "password": password,
        }, timeout=10)
    except requests.exceptions.ConnectionError:
        return None, "Cannot reach the API. Is uvicorn running?"

    if r.status_code == 200:
        token = r.json()["access_token"]
        return token, f"Logged in as {username}."
    return None, f"Error: {r.json().get('detail', 'login failed')}"


def api_predict(token, symptoms_selected):
    if not token:
        return "Please log in first (see the Login tab)."
    if not symptoms_selected:
        return "Select at least one symptom."

    try:
        r = requests.post(f"{API_URL}/predict",
                          json={"symptoms": symptoms_selected},
                          headers={"Authorization": f"Bearer {token}"},
                          timeout=15)
    except requests.exceptions.ConnectionError:
        return "Cannot reach the API. Is uvicorn running?"

    if r.status_code == 401:
        return "Your session expired. Please log in again."
    if r.status_code != 200:
        return f"Error: {r.json().get('detail', 'prediction failed')}"

    result = r.json()
    lines = [f"**Symptoms:** {', '.join(result['input_symptoms'])}\n"]
    for pred in result["predictions"]:
        lines.append(f"### {pred['nutrient']} — {pred['confidence']:.1%} confidence")
        lines.append(f"**Foods:** {', '.join(pred['recommended_foods'][:6])}")
        if pred["recipes"]:
            lines.append("**Recipes:**")
            for rec in pred["recipes"]:
                lines.append(f"- [{rec['title']}]({rec['url']})")
        lines.append("")
    return "\n".join(lines)


def fetch_symptom_list():
    try:
        r = requests.get(f"{API_URL}/symptoms", timeout=10)
        return sorted(r.json()["symptoms"]) if r.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        return []


with gr.Blocks(title="Deficiency Detector") as demo:
    gr.Markdown("# Nutrient Deficiency Detector")
    gr.Markdown("*Educational project - not medical advice.*")

    token_state = gr.State(value=None)

    with gr.Tab("Register"):
        reg_username = gr.Textbox(label="Username")
        reg_email = gr.Textbox(label="Email")
        reg_password = gr.Textbox(label="Password", type="password")
        reg_button = gr.Button("Register")
        reg_output = gr.Markdown()
        reg_button.click(api_register, [reg_username, reg_email, reg_password], reg_output)

    with gr.Tab("Login"):
        login_username = gr.Textbox(label="Username")
        login_password = gr.Textbox(label="Password", type="password")
        login_button = gr.Button("Login")
        login_output = gr.Markdown()
        login_button.click(api_login, [login_username, login_password],
                           [token_state, login_output])

    with gr.Tab("Predict"):
        symptoms_checklist = gr.CheckboxGroup(
            choices=fetch_symptom_list(),
            label="Select your symptoms",
        )
        predict_button = gr.Button("Predict Deficiencies", variant="primary")
        predict_output = gr.Markdown()
        predict_button.click(api_predict, [token_state, symptoms_checklist], predict_output)


if __name__ == "__main__":
    demo.launch()
