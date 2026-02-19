# SecureVault — Flask Authentication & Document Sharing

A full-stack Flask web application featuring secure user authentication, role-based access control, grade viewing, and document upload/sharing.

---

## Features

- **User Registration & Login** with password hashing (Werkzeug)
- **Session Management** via Flask-Login
- **Role-Based Access Control** (Admin / User)
- **Profile Management** — update personal details, change password
- **Grades** — read-only view for students, admin can add grades
- **Document Sharing** — upload, download, share privately or make public
- **Responsive Frontend** — Bootstrap 5 dark theme with glassmorphism

---

## Project Structure

```
login/
├── run.py                  # Entry point
├── config.py               # Configuration
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── uploads/                # Uploaded documents (auto-created)
├── app/
│   ├── __init__.py         # Flask factory, extensions
│   ├── models.py           # SQLAlchemy models
│   ├── forms.py            # WTForms definitions
│   ├── routes/
│   │   ├── auth.py         # Signup, Login, Logout
│   │   ├── main.py         # Dashboard, Profile, Grades, Admin
│   │   └── documents.py    # Upload, Download, Share, Delete
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   ├── change_password.html
│   │   ├── grades.html
│   │   ├── documents.html
│   │   ├── upload.html
│   │   ├── share.html
│   │   ├── admin_users.html
│   │   └── admin_grades.html
│   └── static/
│       └── css/style.css
└── seed.py                 # Seed database with sample data
```

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- MySQL Server running locally

### 1. Create MySQL Database
```sql
CREATE DATABASE flask_auth_db;
```

### 2. Configure Environment
Edit `.env` and update your MySQL credentials:
```
SECRET_KEY=change-me-to-a-random-secret
DATABASE_URI=mysql+pymysql://root:YOUR_PASSWORD@localhost/flask_auth_db
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python run.py
```
This will automatically create all database tables on first run.

### 5. (Optional) Seed Sample Data
```bash
python seed.py
```
Creates demo users:
| Username | Email | Password | Role |
|---|---|---|---|
| `admin` | admin@securevault.com | `admin123` | Admin |
| `student1` | student1@securevault.com | `student123` | User |

---

## Database Schema

```
┌─────────────────┐     ┌──────────────────┐
│     users        │     │     grades        │
├─────────────────┤     ├──────────────────┤
│ id (PK)         │──┐  │ id (PK)          │
│ username        │  │  │ user_id (FK)     │
│ email           │  └──│ subject          │
│ password_hash   │     │ score            │
│ full_name       │     │ semester         │
│ phone           │     └──────────────────┘
│ role            │
│ created_at      │     ┌──────────────────┐
└─────────────────┘     │    documents      │
        │               ├──────────────────┤
        ├───────────────│ id (PK)          │
        │               │ owner_id (FK)    │
        │               │ filename         │
        │               │ original_name    │
        │               │ file_size        │
        │               │ is_public        │
        │               │ upload_date      │
        │               │ description      │
        │               └──────────────────┘
        │                       │
        │               ┌──────────────────┐
        │               │ shared_documents  │
        │               ├──────────────────┤
        └───────────────│ id (PK)          │
                        │ document_id (FK) │
                        │ shared_with_id   │
                        │ shared_date      │
                        └──────────────────┘
```

---

## License
MIT
