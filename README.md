# Secure E-Voting System

This project is a beginner-friendly, demo-ready secure electronic voting system built with Flask, SQLite, SQLAlchemy, Bootstrap, and Python cryptography. It is designed for a college project and educational demonstration only.

Important note:
- This is not a production election system.
- It is not suitable for real government elections.
- It is designed to teach the concepts of secure authentication, vote encryption, digital signatures, and result generation.

## 1. Project Introduction

The Secure E-Voting System allows:
- Voter registration
- Voter login
- Candidate view
- Secure voting
- Vote acknowledgement
- Admin login
- Election and candidate management
- Result generation

It shows how server authentication, RSA signatures, Diffie-Hellman key exchange, and AES encryption can protect the voting process in a demo environment.

## 2. Features

- Secure voter registration and login
- Password hashing using Werkzeug
- Session-based access control
- Duplicate user prevention
- Election and candidate management by admin
- Vote selection with confirmation
- AES-GCM encrypted vote storage
- RSA digital signature verification
- Diffie-Hellman concept demonstration
- Admin result dashboard
- Real database with SQLite and SQLAlchemy
- Responsive Bootstrap UI

## 3. Technology Stack

Frontend:
- HTML5
- CSS3
- JavaScript
- Bootstrap 5

Backend:
- Python 3
- Flask

Database:
- SQLite
- SQLAlchemy

Security:
- RSA
- Diffie-Hellman
- AES-GCM
- Digital signatures
- Password hashing
- Secure session handling

## 4. Security Techniques Used

This project demonstrates the following workflow:

1. Voter authentication
2. Server authentication
3. RSA digital signatures
4. Diffie-Hellman key exchange concept
5. AES encryption for vote storage
6. Signature verification
7. Secure database storage
8. Vote acknowledgement

The app explains the security flow in comments and UI messages. For real deployment, HTTPS/TLS is still required.

## 5. Architecture

The system is divided into the following layers:

- User / Voter
- Web frontend
- Flask backend
- Authentication layer
- Cryptography services
- SQLite database
- Admin panel
- Results module

High-level flow:

User -> Frontend -> Flask API -> Authentication -> Cryptography -> Database -> Admin Results

## 6. Folder Structure

```text
secure_e_voting/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── .gitignore
├── database/
│   ├── __init__.py
│   └── seed.py
├── models/
│   ├── __init__.py
│   └── models.py
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py
│   └── admin_routes.py
├── services/
│   ├── __init__.py
│   ├── rsa_service.py
│   ├── dh_service.py
│   ├── aes_service.py
│   ├── signature_service.py
│   └── voting_service.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── election.html
│   ├── receipt.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── candidates.html
│   └── results.html
├── public/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
├── keys/
│   └── .gitkeep
├── tests/
│   └── test_app.py
└── database/secure_voting.db
```

## 7. Installation Steps

Open the terminal in the project folder.

Windows PowerShell example:

```powershell
Set-Location "D:\SECURE VOTING SUSTEM"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If it works, you will see package installation logs ending in:
- `Successfully installed ...`

If an error appears:
- Check whether Python is installed.
- Make sure the path is correct.
- Re-run the command from the project folder.

## 8. Database Setup

The app uses SQLite by default.

When you run the app for the first time, the database file is created automatically.

Database file:
- `database/secure_voting.db`

The app also seeds demo data automatically if the database is empty.

## 9. How to Generate Keys

This project creates RSA and key files automatically when it starts.

The keys are stored in:
- `keys/server_private_key.pem`
- `keys/server_public_key.pem`
- `keys/vote_master_key.bin`

The app creates them for the demo. Do not share the private key.

If you want to reset them manually:

1. Delete the files in the `keys/` folder.
2. Restart the Flask app.
3. The app will generate fresh keys again.

## 10. How to Run the Application

Open PowerShell in the project folder:

```powershell
Set-Location "D:\SECURE VOTING SUSTEM"
.\.venv\Scripts\Activate.ps1
python app.py
```

Expected output:
- Flask development server starts
- Local URL appears, usually:
  `http://127.0.0.1:5000`

Open the browser and go to:
- `http://127.0.0.1:5000`

If an error appears:
- Confirm the project path is correct
- Ensure dependencies are installed
- Check the database file was created

## 11. Deploying to Vercel

The Flask application runs as a Vercel Function. Vercel's function storage is temporary, so configure a persistent PostgreSQL database before deployment; do not use the local SQLite database for a hosted election.

1. Import `saravanan0345/securevoting` into Vercel and select the repository root.
2. Create a PostgreSQL database through a Vercel Marketplace integration such as Neon, then set its connection string as `DATABASE_URL`.
3. Add `SECRET_KEY`, `VOTING_MASTER_KEY`, and `ADMIN_PASSWORD` as Vercel environment variables. Use unique, randomly generated values; never reuse the demo defaults.
4. Set `ADMIN_USERNAME` to `admin`. Vercel serves the files in `public/` and deploys the app on pushes to the connected branch.

The app refuses to start on Vercel when the database URL or required secrets are missing. Keep the database and encryption key stable so stored votes remain readable after function restarts.

## 12. Default Admin Setup

This project creates a default admin user automatically.

Admin login values:
- Username: `admin`
- Password: `SecureAdmin@123` (demo default; configure `ADMIN_PASSWORD` in `.env` for local use)

Admin route:
- `http://127.0.0.1:5000/admin/login`

## 13. Demo Data

The app creates sample data automatically on first run:
- 1 active election
- 3 candidates
- 3 sample voters
- 1 admin account

Sample voter login values:
- DEMO001 / Password123!
- DEMO002 / Password123!
- DEMO003 / Password123!

You can delete the database file and restart to reset the demo data.

## 14. Testing Steps

Run this command from the project folder:

```powershell
Set-Location "D:\SECURE VOTING SUSTEM"
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

Expected output:
- `9 passed`

This verifies:
- Registration
- Login
- Invalid login
- Admin login
- Vote process
- Duplicate vote attempt
- Result generation
- Security checks

## 15. Security Explanation

This project uses:

- Password hashing for voter and admin accounts
- Secure server-side sessions
- Safe database queries through SQLAlchemy ORM
- Diffie-Hellman key exchange concept for secure session secret generation
- RSA signatures for transaction verification
- AES-GCM encryption for storing votes securely
- Verification before accepting a vote
- No plain-text password storage
- No private key exposure in frontend JavaScript

Important limitation:
- This demo is for learning and college presentation only.
- Real production systems must use HTTPS/TLS, proper certificate management, protected infrastructure, and a full security-review process.

## 16. Limitations

This demo is educational and has limitations:
- It is not designed for real public elections
- It does not replace HTTPS/TLS
- It uses local demo keys and a local database
- It is not built for massive-scale election systems
- It is not suitable for government or legal voting

## 17. Future Enhancements

Possible upgrades:
- Real HTTPS deployment with certificates
- Role-based admin authorization improvements
- Better CSRF protection with Flask-WTF
- Candidate editing and deletion interface improvements
- Better voter audit logs
- Email verification
- Real multi-user deployment with PostgreSQL
- Frontend and backend separation with React or Vue

## 18. Viva Questions and Answers

Q1: What is the role of RSA in this project?
A: RSA is used for signing voting transactions and verifying the signature before the vote is accepted.

Q2: Why is the vote stored in encrypted form?
A: To prevent plain-text exposure and to protect the vote from unauthorized access.

Q3: What is Diffie-Hellman used for here?
A: It demonstrates how two parties can agree on a shared secret without directly sharing the final secret.

Q4: Why is AES used?
A: AES-GCM provides confidentiality and authentication for the encrypted vote data.

Q5: What is the difference between demo project and real election system?
A: This demo teaches the concepts, while real election systems need legal, operational, cryptographic, and infrastructure safeguards.

## 19. PPT Explanation Points

1. Project overview and objectives
2. Why secure voting matters
3. Architecture of the system
4. User registration and login
5. Server authentication and RSA signatures
6. Diffie-Hellman and AES encryption flow
7. Vote storage and verification
8. Admin panel and result generation
9. Demo data setup
10. Security limitations and real-world notes

## 20. Useful Notes

- To reset the demo app, delete `database/secure_voting.db`
- To regenerate keys, delete the files in `keys/`
- Use the admin page at `/admin/login`
- Use the voter page at `/login`
- This project is for demonstration and learning

## 21. Final Note

This is a secure demo voting system made for educational purposes. It is a strong learning project for college presentations and cybersecurity studies, but it is not a production-ready public election platform.
