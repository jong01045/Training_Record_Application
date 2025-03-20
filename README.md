# Training Record Application

## Overview

This project implements a **Training Record Application**, a web-based system for managing training records. The application consists of:
- A **Python-based web server** that provides the backend functionality.
- A **browser-based client** (HTML, CSS, JavaScript) that serves as the user interface.

The primary objective is to extend the provided skeleton code and implement the required backend API functionality using **Python** and **SQL**.

---

## Features

- **User Authentication**: Secure login and session management.
- **Skill Management**: View, enroll in, and manage training classes.
- **Trainer Functionality**: Create, edit, and cancel classes.
- **API Implementation**: Handle data interactions securely via a POST-based API.

---

## Files and Structure

### Provided Files
- `Test Suite\server.py`: The main backend code to be extended.
- `pages/`: Contains pre-built HTML pages for the frontend. **Do not modify**.
  - `index.html`: Main dashboard for upcoming training classes.
  - `skills.html`: Displays user's skills.
  - `class.html`: Shows class details.
  - `create.html`: Class creation form.
  - `login.html`: Login page.
  - `logout.html`: Logout page.
  - `menu.html`: Navigation menu.
- `css/`: CSS stylesheets.
- `js/`: JavaScript files for AJAX requests.
- `db/`: Contains initial SQLite database files.

### Database Schema
The application uses an **SQLite3 database** with the following tables:
1. `users`: User information.
2. `session`: User session tokens.
3. `skill`: Skill data.
4. `class`: Training class details.
5. `attendee`: Tracks attendees of each class.
6. `trainer`: Tracks trainers authorized to teach specific skills.

---

## Installation and Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
2. Install the required dependencies (if any):
   pip install -r requirements.txt
3. Run the server:
   python server.py 8081
4. Open your web browser and navigate to:
   http://127.0.0.1:8081
