import os
import json
import tempfile
import shutil
import pytest
from streamlit_app import load_templates, save_templates, load_users, save_users, hash_password, log_analytics, ANALYTICS_FILE, USERS_FILE, TEMPLATES_FILE

def test_template_load_save():
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, 'templates.json')
    data = {"Math": {"games": {}}}
    save_templates(data)
    loaded = load_templates()
    assert isinstance(loaded, dict)
    shutil.rmtree(temp_dir)

def test_user_load_save():
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, 'users.json')
    users = {"test@example.com": {"name": "Test", "password": hash_password("pw")}}
    save_users(users)
    loaded = load_users()
    assert loaded["test@example.com"]["name"] == "Test"
    shutil.rmtree(temp_dir)

def test_hash_password():
    pw1 = hash_password("abc123")
    pw2 = hash_password("abc123")
    pw3 = hash_password("different")
    assert pw1 == pw2
    assert pw1 != pw3

def test_log_analytics(tmp_path):
    analytics_file = tmp_path / "analytics.json"
    log_analytics("generate", "Math", "NumberParkour", user="test@example.com")
    assert os.path.exists(ANALYTICS_FILE)
    with open(ANALYTICS_FILE) as f:
        data = json.load(f)
        assert data[-1]["event"] == "generate"
        assert data[-1]["user"] == "test@example.com" 