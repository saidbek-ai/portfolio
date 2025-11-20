# 🧑‍💻 Full-Stack Portfolio & Real-Time Chat App

A modern, production-ready **full-stack portfolio application** built with:

- **Django** — backend framework  
- **Django Rest Framework (DRF)** — API layer  
- **Django Channels** — real-time WebSocket communication  
- **Redis** — message broker & caching  
- **React.js** — interactive chat UI rendered inside Django  

This project demonstrates my ability to build scalable, real-time, and production-ready full-stack applications.

---

## 🚀 Features

### 🌐 Portfolio  
- Dynamic project listing  
- About me section  
- Contact form API  
- Admin dashboard for managing content  
- SEO-friendly structure  

### 💬 Real-Time Chat System  
- WebSocket-based real-time messaging  
- One-to-many CRM-style chat  
- Two UIs:
  - **Regular users** → message list + input  
  - **Staff/admins** → user list + chat window  
- Redis-powered channel layer  
- Secure authentication for chat rooms  

### 🧩 Tech Stack

#### Backend
- Django  
- DRF  
- Channels  
- Redis  
- PostgreSQL(With Django ORM),
- Allauth for authentication(including OAuth) with email verification

#### Frontend
- Django template rendering
- TailwindCSS  
- WebSocket client


---
##💬 Real-Time Chat Architecture
```vbnet
Client (React)
   ⬇ WebSocket
Django Channels
   ⬇ Pub/Sub
Redis
   ⬆ Pub/Sub
Django Channels
   ⬆ WebSocket
Client (React)
```

✔ Real-time communication
✔ Redis-backed channel layer
✔ Async chat consumers
✔ Authenticated WebSocket connections

##🛠️ Future Improvements
-File & image sharing
-Typing indicators
-Voice messages
-Web push notifications
-AI-powered chat assistant


## About Me

I am a full-stack developer specializing in Django + React, real-time chat systems, scalable backend architecture, and modern UI development.
This portfolio serves as a demonstration of my ability to build robust end-to-end applications.

