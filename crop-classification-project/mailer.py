import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Ideally, these should be loaded from environment variables (.env)
SENDER_EMAIL = os.getenv("DEEPCROP_EMAIL", "deepcrop.ai.system@gmail.com")
SENDER_PASSWORD = os.getenv("DEEPCROP_EMAIL_PASSWORD", "your_app_password")

def send_dataset_notification(receiver_email, location_name, avg_ndvi, predicted_crop):
    """Sends an email notification when a new scan is processed."""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = f"DeepCrop AI: New Data Processed for {location_name}"

        body = f"""
        Hello,
        
        A new satellite scan has been processed for your Region of Interest: {location_name}.
        
        Summary:
        - Average NDVI: {avg_ndvi:.4f}
        - Predicted Crop: {predicted_crop}
        - Status: Data stored securely in Central Database.
        
        Login to the dashboard to view the full dataset.
        
        Best regards,
        DeepCrop AI Automated System
        """
        
        msg.attach(MIMEText(body, 'plain'))

        # Only attempt to send if passwords are setup, otherwise just log it
        if SENDER_PASSWORD != "your_app_password":
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            text = msg.as_string()
            server.sendmail(SENDER_EMAIL, receiver_email, text)
            server.quit()
            print(f"[INFO] Email notification sent successfully to {receiver_email}.")
        else:
            print(f"[INFO] Email notification generated for {receiver_email} but not sent (credentials missing).")
            print("--- Email Content ---")
            print(body)
            print("---------------------")
            
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

if __name__ == "__main__":
    # Test execution
    send_dataset_notification("test@example.com", "GKVK, Yelahanka", 0.65, "Maize")
