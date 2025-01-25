# SPAC '24 Management System  

This repository contains the **SPAC '24 Management System**, a web-based tool developed for the flagship event **"SPAC '24"** organized by the **IEEE NSU Student Branch**. The system streamlines the management of **food distribution**, **goodies allocation**, and other logistical processes by providing participants with unique QR codes for each session.  

## Acknowledgments  

Special thanks to the **IEEE NSU Student Branch** for their support and for organizing **SPAC '24**, where this system was successfully implemented.  

This system was developed by the **IEEE NSU SB Website Development Team**, whose efforts made the event management process efficient and streamlined.  

---


## Key Features  

- **QR Code Generation**  
  Every participant receives a unique QR code to ensure secure and organized token management.  

- **QR Code Scanning**  
  Quickly scan QR codes during each session to validate and track token usage.  

- **Session-Based Management**  
  Seamlessly handles multiple sessions across the event for different food and goodies distributions.  

- **Data Tracking**  
  Keeps a real-time record of distributed food and goodies, ensuring no duplicates or errors in allocation.  

- **Efficiency and Speed**  
  Used by **190+ participants** across numerous sessions, significantly reducing manual effort and improving overall process efficiency.

- **Gmail API Integration**  
  - Automatically sends QR codes to all participants via email on api call.  
  - Provides a feature to resend the QR code to a provided email address if a participant cannot find their original email/QR code.

---

## Benefits  

- **Faster Queue Management**  
  Participants were served quickly without unnecessary delays.  

- **Accurate Tracking**  
  The system ensured a transparent count of distributed items, avoiding over-distribution or duplication.  

- **Streamlined Workflow**  
  Event organizers saved time and resources by automating the management process.  

---

## Technologies Used  

- **Backend**: Django (Python)  
- **Frontend**: HTML, CSS, JavaScript  
- **Database**: SQLite/MySQL  
- **QR Code Generation & Scanning**: QR code libraries (e.g., `qrcode`, `zxing`)  

---

## How It Works  

1. **Participant Registration**  
   - Each participant is registered in the system and assigned a unique QR code.  

2. **Session Scanning**  
   - QR codes are scanned at designated token distribution points.  
   - The system validates the QR code and logs the transaction.  

3. **Real-Time Updates**  
   - Organizers can view real-time statistics of distributed items for efficient inventory management.  

---

## Usage  

1. Clone this repository:  
   ```bash
   git clone https://github.com/ArmanMokammel/SPAC-24.git
   cd SPAC-24
   ```  
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ``` 
4. Run the development server:
   ```bash
   python manage.py runserver
   ```
5. Access the application in your browser:
   ```bash
   http://127.0.0.1:8000/
   ```
   
---
   
### Environment Variables  

To ensure the application functions correctly, create a `.env` file in the project's root directory and include the following variables:  

```env
SECRET_KEY=your_django_secret_key

SETTINGS=dev

DEV_GOOGLE_CLOUD_CLIENT_ID=your_google_cloud_client_id
DEV_GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project_id
DEV_GOOGLE_CLOUD_AUTH_URI=https://accounts.google.com/o/oauth2/auth
DEV_GOOGLE_CLOUD_TOKEN_URI=https://oauth2.googleapis.com/token
DEV_GOOGLE_CLOUD_AUTH_PROVIDER_x509_cert_url=https://www.googleapis.com/oauth2/v1/certs
DEV_GOOGLE_CLOUD_CLIENT_SECRET=your_google_cloud_client_secret

DEV_SCOPES=https://mail.google.com/

GOOGLE_MAIL_API_NAME=gmail
GOOGLE_MAIL_API_VERSION=v1
