import os
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Load environment variables
load_dotenv()
app = Flask(__name__)

# 🔹 Allow ONLY requests from your frontend
CORS(app, resources={r"/*": {"origins": "https://homebasebank-1smm.vercel.app"}})

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Server is running!"}), 200

# 🔹 Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_SUPPRESS_SEND'] = False  # Ensure Flask-Mail actually sends emails

mail = Mail(app)

# 🔹 Function to Generate PDF
def generate_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Attestation Form", styles["Title"]))
    elements.append(Spacer(1, 12))

    def add_entry(label, value):
        elements.append(Paragraph(f"<b>{label}:</b> {value}", styles["Normal"]))
        elements.append(Spacer(1, 6))

    fields = [
        "Referee1Name", "Referee1Address", "Referee2Name", "Referee2Address", 
        "Referee3Name", "Referee3Address", "Institution", "Registryaddress", 
        "Attestationname", "Signature", "Date", "Comments", "Hcname", "Hcsignature"
    ]
    
    for field in fields:
        add_entry(field.replace("Registryaddress", "Registry Address").replace("Attestationname", "Attestation Name"), data.get(field, "N/A"))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# 🔹 Test Email Sending
@app.route('/test-email', methods=['GET'])
def test_email():
    try:
        msg = Message("Test Email", recipients=["your_email@gmail.com"])
        msg.body = "This is a test email from Flask."
        mail.send(msg)
        return jsonify({"message": "Test email sent successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Handle Form Submission and Send Email
@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        form_data = request.json
        pdf_content = generate_pdf(form_data)
        recipient_email = os.getenv("RECIPIENT_EMAIL")

        if not recipient_email:
            return jsonify({"error": "Recipient email not configured"}), 500
        
        msg = Message('Form Submission PDF', recipients=[recipient_email])
        msg.body = "Attached is the submitted form in PDF format."
        msg.attach("submission.pdf", "application/pdf", pdf_content)
        
        mail.send(msg)
        print("✅ Email sent successfully!")  # Debugging log
        return jsonify({"message": "Form submitted successfully and sent via email!"}), 200
    
    except Exception as e:
        print("❌ Error sending email:", str(e))  # Debugging log
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))
