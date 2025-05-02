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
- `templates.json` — Subject/game template metadata
- `analytics.json` — Analytics event log
- `users.json` — Registered user data
- `tests/` — Automated tests

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE) 