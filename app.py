import os
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# 🔹 Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# 🔹 Allow requests from your Vercel frontend
CORS(app, resources={r"/*": {"origins": "https://homebasebank-1smm.vercel.app"}})

# 🔹 Flask-Mail Configuration (from .env)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# 🔹 Function to Generate a Properly Formatted PDF
def generate_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["Normal"]

    elements.append(Paragraph("Attestation Form", title_style))
    elements.append(Spacer(1, 12))

    def add_entry(label, value):
        elements.append(Paragraph(f"<b>{label}:</b> {value}", normal_style))
        elements.append(Spacer(1, 6))

    # 🔹 Add Form Fields Neatly
    for key, value in data.items():
        add_entry(key.replace("_", " ").title(), value if value else "N/A")

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# 🔹 Debug Route (For Testing)
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Backend is working!"})

# 🔹 API Route to Handle Form Submission
@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        form_data = request.json  # Get JSON data from frontend

        if not form_data:
            return jsonify({"error": "No form data received"}), 400

        # 🔹 Generate the PDF
        pdf_content = generate_pdf(form_data)

        # 🔹 Create Email with PDF Attachment
        recipient_email = os.getenv("RECIPIENT_EMAIL")  # Fetch from .env
        msg = Message('Form Submission PDF', recipients=[recipient_email])
        msg.body = "Attached is the submitted form in PDF format."
        msg.attach("submission.pdf", "application/pdf", pdf_content)

        # 🔹 Send the Email
        mail.send(msg)

        return jsonify({"message": "Form submitted successfully and sent via email!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Run the Flask App on Render
if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))
