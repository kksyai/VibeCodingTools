from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
import re
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="VibeCoding Tools API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "resources.json")

ZAI_API_KEY = os.getenv("ZAI_API_KEY", "")

categories_map = {
    "ai-models": ["AI", "LLM", "API", "model", "OpenAI", "Claude", "Gemini", "GLM"],
    "ai-editors": ["editor", "IDE", "cursor", "coding", "agent", "bot", "assistant", "Monica", "Claude Code"],
    "skills-mcp": ["MCP", "skill", "Beads", "context", "agent"],
    "deploy": ["deploy", "hosting", "Vercel", "Railway", "Render", "Supabase", "serverless", "cloud"],
    "design": ["design", "UI", "Canva", "Dribbble", "Figma", "UI/UX", "interface", "style"],
    "docs": ["docs", "documentation", "React", "Tailwind", "framework", "guide", "reference", "Telegram"],
    "utils": ["tool", "utility", "productivity", "screenshot", "note", "capture", "record", "converter"]
}

class ResourceData(BaseModel):
    url: str
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None

class ClassificationResult(BaseModel):
    url: str
    name: str
    description: str
    icon: str
    category: str

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"version": "1.0", "categories": {}}

def save_data(data):
    data["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def fetch_url_info(url: str):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, follow_redirects=True)
            
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            title = None
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            
            description = None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            return {
                "title": title,
                "description": description,
                "domain": url.split('/')[2]
            }
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    
    return None

def get_favicon_url(domain: str):
    return f"https://www.google.com/s2/favicons?sz=64&domain={domain}"

def classify_resource(url: str, title: str = "", description: str = "") -> str:
    text = f"{url} {title} {description}".lower()
    
    scores = {}
    for category, keywords in categories_map.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in text:
                score += 1
        scores[category] = score
    
    best_category = max(scores, key=scores.get)
    
    if scores[best_category] == 0:
        best_category = "utils"
    
    return best_category

async def translate_to_russian(text: str) -> str:
    """Truncate text to 100 characters, keep Russian descriptions"""
    if not text:
        return text
    
    # Check if text is already in Russian (has Cyrillic characters)
    if any(ord(char) >= 1040 and ord(char) <= 1103 for char in text):
        # Already in Russian, just truncate
        if len(text) > 100:
            return text[:97] + "..."
        return text
    
    # Not in Russian, truncate English text
    if len(text) > 100:
        return text[:97] + "..."
    
    return text

async def ai_classify(url: str, title: str, description: str) -> str:
    """AI-powered classification (placeholder for future implementation)"""
    return classify_resource(url, title, description)

@app.get("/api/resources")
async def get_resources():
    data = load_data()
    return data

@app.post("/api/classify")
async def classify_endpoint(resource: ResourceData):
    url_info = await fetch_url_info(resource.url)
    
    if url_info:
        name = resource.name or url_info.get("title", "")
        description = resource.description or url_info.get("description", "")
        icon = resource.icon or get_favicon_url(url_info.get("domain", ""))
        domain = url_info.get("domain", "")
    else:
        name = resource.name or ""
        description = resource.description or ""
        icon = resource.icon or get_favicon_url(resource.url.split('/')[2] if len(resource.url.split('/')) > 2 else "")
        domain = resource.url.split('/')[2] if len(resource.url.split('/')) > 2 else ""
    
    if not name:
        domain_name = domain.replace('www.', '').split('.')[0].capitalize()
        name = domain_name
    
    if not description:
        description = "Ресурс для разработки"
    
    description = await translate_to_russian(description)
    
    category = resource.category or classify_resource(resource.url, name, description)
    
    return {
        "url": resource.url,
        "name": name,
        "description": description,
        "icon": icon,
        "category": category
    }

@app.post("/api/resources")
async def add_resource(resource: ResourceData):
    data = load_data()
    
    if not resource.category:
        url_info = await fetch_url_info(resource.url)
        if url_info:
            name = resource.name or url_info.get("title", "")
            description = resource.description or url_info.get("description", "")
        else:
            name = resource.name or ""
            description = resource.description or ""
        
        category = classify_resource(resource.url, name, description)
    else:
        category = resource.category
    
    url_info = await fetch_url_info(resource.url)
    if url_info:
        name = resource.name or url_info.get("title", "")
        description = resource.description or url_info.get("description", "")
        icon = resource.icon or get_favicon_url(url_info.get("domain", ""))
    else:
        name = resource.name or ""
        description = resource.description or ""
        icon = resource.icon or get_favicon_url(resource.url.split('/')[2] if len(resource.url.split('/')) > 2 else "")
    
    if not name:
        domain = resource.url.split('/')[2] if len(resource.url.split('/')) > 2 else ""
        domain_name = domain.replace('www.', '').split('.')[0].capitalize()
        name = domain_name
    
    if not description:
        description = "Ресурс для разработки"
    
    description = await translate_to_russian(description)
    
    if len(description) > 100:
        description = description[:97] + "..."
    
    resource_id = name.lower().replace(" ", "-").replace(".", "").replace("/", "")
    
    new_resource = {
        "id": resource_id,
        "name": name,
        "url": resource.url,
        "description": description,
        "icon": icon
    }
    
    if category in data["categories"]:
        existing_ids = [tool["id"] for tool in data["categories"][category]["tools"]]
        if resource_id in existing_ids:
            raise HTTPException(status_code=400, detail="Ресурс с таким ID уже существует")
        
        data["categories"][category]["tools"].append(new_resource)
    else:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    save_data(data)
    
    return {"message": "Ресурс добавлен", "resource": new_resource}

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
