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

# Allow requests from your Vercel frontend
CORS(app, resources={r"/*": {"origins": "https://homebasebank-1smm.vercel.app"}})

@app.route('/')
def home():
    return jsonify({"message": "Backend is working!"})

if __name__ == "__main__":
    app.run(debug=True)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Gmail SMTP server
app.config['MAIL_PORT'] = 587  # TLS Port
app.config['MAIL_USE_TLS'] = True  # Enable TLS encryption
app.config['MAIL_USE_SSL'] = False  # SSL is not required
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Gmail Address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')  # Default sender email

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
    add_entry("Referee 1 Name", data.get("Referee1Name", "N/A"))
    add_entry("Referee 1 Address", data.get("Referee1Address", "N/A"))
    add_entry("Referee 2 Name", data.get("Referee2Name", "N/A"))
    add_entry("Referee 2 Address", data.get("Referee2Address", "N/A"))
    add_entry("Referee 3 Name", data.get("Referee3Name", "N/A"))
    add_entry("Referee 3 Address", data.get("Referee3Address", "N/A"))
    add_entry("Institution", data.get("Institution", "N/A"))
    add_entry("Registry Address", data.get("Registryaddress", "N/A"))
    add_entry("Attestation Name", data.get("Attestationname", "N/A"))
    add_entry("Signature", data.get("Signature", "N/A"))
    add_entry("Date", data.get("Date", "N/A"))
    add_entry("Comments", data.get("Comments", "N/A"))
    add_entry("HC Name", data.get("Hcname", "N/A"))
    add_entry("HC Signature", data.get("Hcsignature", "N/A"))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# 🔹 API Route to Handle Form Submission
@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        form_data = request.json  # Get JSON data from frontend

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
if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))
