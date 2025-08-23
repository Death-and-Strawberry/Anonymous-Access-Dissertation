from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os
import re

# Serve static templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../templates")

def render_template(filename: str, **context) -> HTMLResponse:
    """
    Render a template with optional context variables.
    Supports simple {{ variable }} substitution.
    """
    path = os.path.join(TEMPLATES_DIR, filename)
    
    with open(path, "r") as f:
        content = f.read()
    
    # If context is provided, do simple template variable substitution
    if context:
        for key, value in context.items():
            # Replace {{ key }} with the actual value
            pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
            content = re.sub(pattern, str(value), content)
    
    return HTMLResponse(content=content)