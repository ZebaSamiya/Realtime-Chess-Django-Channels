# Realtime-Chess-Django-Channels

This repository contains two projects that implement a full-stack, multiplayer chess game using Django. The first version uses AJAX polling to update game state, while the enhanced version incorporates real-time communication using WebSockets and Django Channels. Both projects use server-side rendering (SSR) and are deployed to Google Cloud Platform (GCP).

---

## 📁 Repository Structure

- **Realtime-Chess-Django-Channels/**
  - 📂 **Multiplayer-chess-ajax/** → AJAX Polling version  
  - 📂 **Realtime-chess-channels/** → WebSockets version


---

## Project 2: Multiplayer Chess Ajax

**Path:** `Multiplayer-chess-ajax`

### Overview
A multiplayer chess web application built with Django, leveraging SSR and AJAX for dynamic updates. The game logic and move validation are powered by the `python-chess` library. The app supports user sessions, game state persistence, and game history.

### Features
- Turn-based multiplayer chess
- AJAX polling for move synchronization
- Session-based authentication
- Game state managed using `python-chess`
- Responsive UI with Bootstrap
- Deployed on Google Cloud Platform (GCP)

---

## Project 3: Realtime Chess with Django Channels

**Path:** `Realtime-chess-channels`

### Overview
An enhanced version of the multiplayer chess app that replaces AJAX polling with real-time bi-directional communication using WebSockets via Django Channels. This improves gameplay responsiveness and provides a smoother user experience.

### Features
- Real-time gameplay with WebSockets
- Integrated with Django Channels
- Maintains SSR with Django templating
- `python-chess` for game state and move validation
- Deployed on Google Cloud Platform (GCP)

---

## Tech Stack

| Category    | Technologies |
|-------------|--------------|
| Frontend    | HTML, CSS, JavaScript, Bootstrap |
| Backend     | Django (SSR), Django Channels |
| Real-time   | WebSockets |
| Game Logic  | python-chess |
| Deployment  | Google Cloud Platform, Gunicorn, Nginx, Cloud SQL (PostgreSQL) |

---

## Deployment Details

Both projects were deployed to Google Cloud Platform and configured using:
- **Cloud SQL** for the PostgreSQL database
- **Instance Group + Load Balancer** for scaling
- **SSL Certificate** via Google-managed HTTPS

## 📄 License

This project is licensed under the [MIT License](LICENSE).
