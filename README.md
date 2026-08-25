# 🎓 Fortune Association – Event Management System

Fortune Association is a web-based event management system developed using **Flask**.  
It helps manage **cultural, technical, and sports events** for a college association with **admin and student access**.

---

## ✨ Features

### 👤 User (Student)
- Student signup & login
- View current events
- Register for events using registration links
- View events by category (Cultural / Technical / Sports)

### 🔐 Admin
- Admin login
- Add Academics
- Add Previous year events
- Add current events
- Edit existing events
- Delete events
- Manage event details from admin panel

---

## 🛠 Tech Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS, JavaScript, Jinja2
- **Database:** MySQL
- **Authentication:** Flask-Login
- **Version Control:** Git & GitHub

---

## 📁 Project Structure

fortune_association/
│
├── flaskr/
│ │
│ ├── templates/
│ │ ├── base.html
│ │ ├── index.html
│ │ ├── login.html
│ │ ├── signup.html
│ │ ├── about.html
│ │ ├── academic_details.html
│ │ ├── add_academics.html
│ │ ├── add_events.html
│ │ ├── contact.html
│ │ ├── list_academics.html
│ │ ├── error.html
│ │ ├── current_events.html
│ │ ├── current_events_admin.html
│ │ ├── fortune_association.sql
│ │
│ ├── app.py
│
├── requirements.txt
├── README.md
└── .gitignore



---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/fortune-association.git
cd fortune-association

### Create Virtual Environment
python -m venv venv
 
#Windows
venv\Scripts\activate

#Mac/Linux
source venv/bin/activate


#Install Dependencies
pip install -r requirements.txt

#Database Setup (MySQL)
Create a MySQL database
Create required tables (users, current_events, etc.)
Update database credentials in app.py

#Run the Application
python app.py
or 
python flaskr/app.py

#Open in browser:
http://127.0.0.1:5000

🖼️Home Page Preview
Welcome Box
Event types and Upcoming Events
Navbar with user dropdown (Login / Signup / Logout)

🔐Authentication
Flask-Login is used for authentication
Role-based access for Admin and User
Admin features are hidden from normal users

🚀Future Enhancements
Event registration tracking
Admin dashboard with analytics
Image upload for events
Email notifications

👨‍💻Author
Pragati Kadagi
Computer Science & Engineering
Fortune Association Project

📄License
This project is developed for College Mini project Submission.