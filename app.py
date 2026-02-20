from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    df = pd.read_csv(file)

    return jsonify({
        "columns": list(df.columns),
        "preview": df.head().to_dict(orient="records")
    })

if __name__ == "__main__":
    app.run(debug=True)
