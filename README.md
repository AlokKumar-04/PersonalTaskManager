# 🗂️ Personal Task Manager

A Django-based web application to manage your personal tasks efficiently. With features like user authentication, task filtering, priority management, and export options, it's built to help you stay organized and productive.

---

## 📸 Preview

> Add screenshots in the `screenshots/` folder and update paths below.

| Home Page | Dashboard | Task Detail |
|-----------|-----------|-------------|
| ![Home](screenshots/home.png) | ![Dashboard](screenshots/dashboard.png) | ![Task Detail](screenshots/task_details.png) |

---

## 📤 Export Tasks (CSV & PDF)

Easily export your tasks for reporting or backup purposes in **CSV** or **PDF** formats.

### ✅ Export Options:

- **📁 All Tasks to CSV**  
  Get a `.csv` file with all your task details (title, description, priority, due date, status, etc.).

- **📝 Single Task to CSV**  
  Export individual task info in CSV format.

- **📄 All Tasks to PDF**  
  Generate a PDF report including:
  - Task summary (total, completed, pending, overdue)
  - Detailed task table with creation and due dates

- **📌 Single Task to PDF**  
  Professionally formatted task document with complete metadata.

- **🧭 Export Options Page**  
  A dedicated view to access all export types and stats.

### 📍 Export Routes:

| URL | Description |
|-----|-------------|
| `/export_tasks_csv/` | Export all tasks as a CSV file |
| `/export_tasks_pdf/` | Export all tasks as a PDF file |
| `/export_single_task_csv/<int:task_id>/` | Export one task as CSV |
| `/export_single_task_pdf/<int:task_id>/` | Export one task as PDF |
| `/export_options/` | View export options and summary |

> 📦 Files are named with your username and a timestamp for easy tracking.

---

## 🛠️ Tech Stack

- **Backend**: Django, Python
- **Frontend**: HTML, CSS, Bootstrap
- **Database**: SQLite (default), can be replaced with PostgreSQL/MySQL
- **Exports**:  
  - CSV: Python `csv` module  
  - PDF: `reportlab` library

---

## 💻 Installation

```bash
git clone https://github.com/yourusername/personal-task-manager.git
cd personal-task-manager
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🔐 Admin Access

To create a superuser:
```bash
python manage.py createsuperuser
```

Then log in at `/admin/`.

---

## 📸 Screenshots

> *(Add your app screenshots here — e.g., dashboard view, export options page, task PDF sample)*

---

## 👤 Author

**Alok Kumar Panda**  
🔗 [Portfolio](https://portfolio-one-mu-78.vercel.app/)  
🔗 [LinkedIn](https://www.linkedin.com/in/alok-kumar-panda-864b421a4)

---

## 📃 License

This project is licensed under the MIT License.
