# Nomics Education Platform

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-app-red)](https://streamlit.io/)

## Overview

The Nomics Education Platform enables teachers to create engaging, customizable educational games for their students. It supports dynamic game templates, analytics, user accounts, admin management, and optional LMS integration (Schoology, Canvas, Blackboard).

## Features
- Multi-step game creation flow
- Dynamic subject/game templates
- Teacher registration/login
- Admin panel for template and analytics management
- Analytics dashboard (admin and teacher views)
- Downloadable Lua game scripts and input data
- Optional LMS integration fields
- Responsive, modern UI/UX
- Automated tests for core logic

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/GrayGhostDev/nomics_edu_AI.git
   cd nomics_edu_AI
   ```
2. **Create a virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## Usage
- Register or log in as a teacher to create games.
- Use the admin panel (with password) to manage templates and view analytics.
- Download generated Lua scripts and input data for use in Roblox Studio or other platforms.

## Directory Structure
- `streamlit_app.py` — Main Streamlit application
- `Games/` — Lua template files for each subject/game
- `games_input/` — Saved input data for generated games
- `games_output/` — Generated Lua scripts
- `src/server/` — For Roblox ServerScriptService (used with Rojo)
- `src/shared/` — For Roblox ReplicatedStorage (used with Rojo)
- `src/client/` — For Roblox StarterPlayer (used with Rojo)
- `templates.json` — Subject/game template metadata
- `analytics.json` — Analytics event log
- `users.json` — Registered user data
- `tests/` — Automated tests

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE)

## Docker Usage

You can run the app in a Docker container with support for both Ollama (local) and OpenAI LLMs.

### Build the Docker image
```bash
docker build -t nomics-edu-app .
```

### Run with Ollama (local)
- Make sure the Ollama server is running on your host (default: http://localhost:11434)
- Run the container:
```bash
docker run -p 8501:8501 \
  --network=host \
  nomics-edu-app
```

### Run with OpenAI API
- Set your OpenAI API key as an environment variable:
```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-... \
  nomics-edu-app
```
- Or enter the key in the app sidebar when prompted.

### Notes
- The app exposes port 8501 for Streamlit.
- For Ollama, the container must be able to reach the Ollama server (use `--network=host` or set the correct `base_url`).
- You can use both LLMs by selecting the provider in the sidebar. 