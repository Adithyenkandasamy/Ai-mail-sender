from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
token = os.getenv("github_key")
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

# Initialize Flask app
app = Flask(__name__)
CORS(app)

def initialize_openai_client():
    """Initialize and return OpenAI client"""
    openai.api_key = token
    openai.api_base = endpoint
    return openai

def generate_subject(client, topic, recipient):
    """Generate email subject using OpenAI"""
    try:
        prompt = f"""Generate a professional and appropriate email subject line for an email to a {recipient} about: {topic}.
        The subject should be concise and clear. Return only the subject line without any additional text."""
        
        response = client.ChatCompletion.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional email writer. Generate only the subject line.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Error generating subject"

def generate_email(client, topic, recipient):
    """Generate email content using OpenAI"""
    try:
        prompt = f"""Write a professional email to {recipient} about: {topic}. 
        Use placeholders like [Your Name], [Your Position], and [Your Contact Information] where sender details are required. 
        Make it professional, concise, and clear."""
        
        response = client.ChatCompletion.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional email writer. Write clear and concise emails with placeholders for sender details.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Error generating email body"

@app.route('/generate', methods=['POST'])
def generate():
    """API to generate email subject and body"""
    try:
        data = request.json
        topic = data.get("topic")
        recipient = data.get("recipient")
        
        client = initialize_openai_client()
        subject = generate_subject(client, topic, recipient)
        email_body = generate_email(client, topic, recipient)
        
        return jsonify({"subject": subject, "body": email_body})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/replace-placeholders', methods=['POST'])
def replace_placeholders():
    """API to replace placeholders in email body"""
    try:
        data = request.json
        email_body = data.get("body")
        replacements = data.get("replacements")  # Dictionary of {placeholder: value}

        for placeholder, value in replacements.items():
            email_body = email_body.replace(f"[{placeholder}]", value)
        
        return jsonify({"updated_body": email_body})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/send', methods=['POST'])
def send_email_api():
    """API to send email"""
    try:
        data = request.json
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        recipient_email = data.get("recipient_email")
        subject = data.get("subject")
        body = data.get("body")
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return jsonify({"message": "Email sent successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
