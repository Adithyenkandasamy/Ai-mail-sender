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
        
        subject = response.choices[0].message.content.strip()
        print(f"\nGenerated Subject: {subject}")
        return subject
    except Exception as e:
        print(f"Error generating subject: {e}")
        return "Invitation"  # Default fallback subject

def replace_bracketed_content(email_body):
    """Replace bracketed content with user input"""
    # [Previous implementation remains the same]
    brackets = re.findall(r'\[(.*?)\]', email_body)
    modified_email = email_body
    
    if brackets:
        print("\nPlease provide the following details:")
        for placeholder in brackets:
            user_input = input(f"Enter {placeholder}: ").strip()
            modified_email = modified_email.replace(f"[{placeholder}]", user_input)
        
        print("\nHere's your final email:\n")
        print(modified_email)
        
        while True:
            confirm = input("\nIs this final version okay? (yes/no): ").strip().lower()
            if confirm == 'yes':
                return modified_email
            elif confirm == 'no':
                return replace_bracketed_content(email_body)
            else:
                print("Please answer 'yes' or 'no'")
    
    return modified_email

def generate_email(client, topic, recipient):
    """Generate email content using OpenAI"""
    try:
        prompt = f"""Write a professional email to {recipient} about: {topic}. 
        Make it professional, concise, and clear. 
        Do NOT include 'Subject:' line in the email body - start directly with the salutation."""
        
        response = client.ChatCompletion.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional email writer. Write clear and concise emails without including Subject lines in the body.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        
        email_body = response.choices[0].message.content.strip()
        return replace_bracketed_content(email_body)
    except Exception as e:
        print(f"Error generating email draft: {e}")
        return None

def send_email(sender_email, sender_password, recipient_email, subject, body):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    try:
        # Initialize OpenAI client
        client = initialize_openai_client()

        # Get email details from user
        topic = input("What is the main topic of the email? ").strip()
        recipient = input("Who is the recipient to you (e.g., manager, teacher, client)? ").strip()

        # Generate subject automatically
        subject = generate_subject(client, topic, recipient)
        print(f"Using generated subject: {subject}")

        # Generate email draft
        print("\nGenerating a high-quality email draft...")
        email_body = generate_email(client, topic, recipient)
        
        if not email_body:
            print("Failed to generate email draft.")
            return

        # Confirm sending
        confirm = input("\nDo you want to send this email? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Email not sent.")
            return

        # Get sending details
        recipient_email = input("Enter the recipient's email address: ").strip()
        sender_email = "aadithyen1@gmail.com"  # Consider moving to environment variables
        sender_password = "lgdr rexb fnvu xtxn"  # Consider moving to environment variables

        # Send the email
        send_email(sender_email, sender_password, recipient_email, subject, email_body)

    except KeyboardInterrupt:
        print("\nProgram interrupted by the user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()