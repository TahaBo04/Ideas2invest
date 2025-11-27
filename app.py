from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# --- Dummy data for MVP (replace later with database) ---

IDEAS = [
    {
        "id": 1,
        "title": "Smart Water Monitoring Platform",
        "sector": "Cleantech",
        "stage": "Prototype",
        "country": "Morocco",
        "funding_goal": 80000,
        "teaser": "Real-time water quality monitoring for industries and cities.",
    },
    {
        "id": 2,
        "title": "AI-based Maintenance Prediction",
        "sector": "Industry 4.0",
        "stage": "MVP",
        "country": "France",
        "funding_goal": 150000,
        "teaser": "Predictive maintenance using machine learning for heavy equipment.",
    },
    {
        "id": 3,
        "title": "EdTech Micro-Learning App",
        "sector": "EdTech",
        "stage": "Early Users",
        "country": "Morocco",
        "funding_goal": 50000,
        "teaser": "Short, gamified courses for engineering students and young professionals.",
    },
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ideas")
def ideas():
    return render_template("ideas.html", ideas=IDEAS)


@app.route("/ideas/<int:idea_id>")
def idea_public(idea_id):
    idea = next((i for i in IDEAS if i["id"] == idea_id), None)
    if not idea:
        return "Idea not found", 404
    return render_template("idea_public.html", idea=idea)


@app.route("/ideas/<int:idea_id>/nda", methods=["GET", "POST"])
def idea_nda(idea_id):
    idea = next((i for i in IDEAS if i["id"] == idea_id), None)
    if not idea:
        return "Idea not found", 404

    if request.method == "POST":
        # TODO: here you would:
        # - store NDA signature in database
        # - create an access_grant entry
        # - maybe log IP and timestamp
        return redirect(url_for("idea_confidential", idea_id=idea_id))

    return render_template("nda.html", idea=idea)


@app.route("/ideas/<int:idea_id>/confidential")
def idea_confidential(idea_id):
    idea = next((i for i in IDEAS if i["id"] == idea_id), None)
    if not idea:
        return "Idea not found", 404

    # TODO: in real app, check if this investor has signed NDA before allowing access
    return render_template("idea_confidential.html", idea=idea)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
