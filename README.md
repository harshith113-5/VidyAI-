# VidyAI++
# 🌟 VidyAI++ – Multilingual AI Tutoring & Mentorship Platform for BPL Government School Students

## 🚀 Project Title
**VidyAI++** – Multilingual AI Tutoring & Mentorship Platform for BPL Government School Students

## 🌐 Selected Domain
**Education Technology (EdTech) / AI for Social Good**

## ❓ Problem Statement / Use Case
Underprivileged (BPL) students in Indian government schools often lack access to personalized education, mentorship, and inclusive learning experiences. Language barriers, limited teacher availability, poor connectivity, and diverse learning needs hinder their academic growth. There is a need for an AI-powered system that provides dynamic, adaptive, and multilingual support aligned with India’s National Education Policy (NEP).

## 📄 Abstract / Problem Description
VidyAI++ is a web-based AI-powered multilingual education and mentorship platform designed for BPL students in Indian government schools. The system acts as an inclusive academic assistant that adapts to individual learning styles, emotional states, and regional languages. It offers generative tutoring, real-time adaptive content, webcam-based emotion detection, gamified learning, and AI mentor matchmaking.

The platform integrates cutting-edge technologies like GPT-4o, OpenCV, DeepFace, and PWA to ensure accessibility even in low-bandwidth zones. It supports voice navigation and screen-reader enhancements, making it usable for students and parents with zero literacy. By blending AI with empathy, VidyAI++ aims to democratize quality education and build long-term student engagement, motivation, and achievement.

---

## 🧠 Tech Stack Used

### 🔧 Backend
- **Python 3.11**
- **Flask** – Lightweight web framework
- **Flask-Login** – Authentication and session management
- **Flask-SQLAlchemy** – ORM for database operations
- **Werkzeug** – Secure password hashing
- **Gunicorn** – WSGI HTTP server for deployment

### 🗄️ Database
- **PostgreSQL** – Relational DBMS
- **psycopg2-binary** – PostgreSQL adapter for Python

### 🤖 AI & Machine Learning
- **OpenAI GPT-4o API** – Generative tutoring and multilingual content
- **DeepFace** – Emotion detection (with fallback support)
- **OpenCV (cv2)** – Webcam and vision-based engagement tracking
- **NumPy** – Scientific computing (for vision features)
- **TensorFlow Lite** – Edge AI inference for offline functionality

### 🎨 Frontend
- **HTML5 / CSS3**
- **Bootstrap 5** – Responsive design
- **Bootstrap Icons**
- **JavaScript**
- **Progressive Web App (PWA)** – Offline-first architecture

### 📦 APIs and Web Features
- **Web Speech API** – Voice recognition & text-to-speech
- **MediaDevices API** – Webcam access
- **IndexedDB / Web Storage / Cache API** – Offline local storage
- **Fetch API** – AJAX communication

### ♿ Accessibility
- **ARIA Attributes** – Screen reader support
- **Voice-based Navigation**
- **Text-to-Speech and Speech Recognition**

### 🔐 Security
- **Environment Variables** – For sensitive configs (API keys, DB credentials)
- **Password Hashing** – Secure authentication
- **CSRF Protection** – Built-in via Flask

---

## 📚 Project Explanation

VidyAI++ is an AI-powered education platform crafted to empower underprivileged students through personalized and inclusive digital learning. Key features include:

1. **Multilingual AI Tutoring**: GPT-4o generates localized lessons and quizzes in multiple Indian languages with text + voice support.
2. **Adaptive Content Delivery**: Real-time adjustment of lesson complexity based on user performance and learning pace.
3. **Emotion-Aware Vision System**: Uses webcam (OpenCV + DeepFace) to detect boredom, fatigue, or stress; adapts content accordingly.
4. **Mentor Matchmaking**: ML-based system pairs students with virtual/local mentors based on emotional and academic profiles.
5. **Learning Persona Engine**: Classifies learners into visual, auditory, or kinesthetic and modifies delivery formats accordingly.
6. **Gamified Learning**: Implements progress tracking, digital badges, streaks, and skill heatmaps to enhance retention and motivation.
7. **Offline-First Architecture**: Fully functional in low-bandwidth areas with PWA capabilities and TensorFlow Lite models.
8. **Zero Literacy UI**: Visual navigation and voice interaction for students and guardians with limited reading ability.

---

## 📌 How to Run the Project (Local Setup)

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/vidyai-plusplus.git
   cd vidyai-plusplus
2.**Set up virtual environment and install dependencies**
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

3. **Set environment variables**
   FLASK_APP=app.py
FLASK_ENV=development
OPENAI_API_KEY=your_openai_key
DATABASE_URL=your_postgres_url
SECRET_KEY=your_flask_secret_key
4.** Run the Flask server**
   flask run
