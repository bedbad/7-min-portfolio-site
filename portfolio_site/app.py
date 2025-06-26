import aiohttp
from aiohttp import web
import aiohttp_jinja2
import jinja2
import logging
from logging.handlers import RotatingFileHandler
import json
import os
from pathlib import Path
import itertools
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def load_json_data(filename):
    """Load JSON data from the data directory"""
    try:
        data_path = Path(__file__).parent / 'data' / filename
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return {}

async def handle_index(request):
    """Handle the main portfolio page"""
    try:
        # Load all JSON data
        about = await load_json_data('about.json')
        entries = await load_json_data('entries.json')
        strings_all = await load_json_data('strings.json')
        lang = 'en'  # In the future, this could be dynamic
        strings = strings_all.get(lang, {})

        # Sort entries by date (descending)
        def get_date(item):
            return item.get('date', '0000-00-00')
        entries_sorted = sorted(entries, key=get_date, reverse=True)

        # Prepare context for template
        context = {
            'about': about,
            'entries': entries_sorted,
            'strings': strings
        }
        
        # Render template with context
        response = aiohttp_jinja2.render_template('index.html', request, context)
        return response
        
    except Exception as e:
        logger.exception("Error rendering portfolio page")
        return web.Response(text=f"Error loading portfolio: {str(e)}", status=500)

async def handle_submit(request):
    """Handle resume request form submission"""
    try:
        if request.content_type.startswith("application/json"):
            data = await request.json()
            email = data.get('email', '')
            who = data.get('who', '')
            regarding = data.get('regarding', '')
        else:
            data = await request.post()
            email = data.get('email', '')
            who = data.get('who', '')
            regarding = data.get('regarding', '')

        logger.info(f"POST data: {data}")

        if not email or not who or not regarding:
            return web.json_response({
                'message': 'All fields are required.'
            }, status=400)

        logger.info(f"Received resume request from: {email}, who: {who}, regarding: {regarding}")

        return web.json_response({
            'message': f'Thank you, {who}! We will send the resume to {email} regarding "{regarding}" shortly.'
        })
    except Exception as e:
        logger.exception("Error processing request")
        return web.json_response({
            'message': f'An error occurred while processing your request: {str(e)}'
        }, status=500)

@aiohttp_jinja2.template('admin.html')
async def handle_admin(request):
    about = await load_json_data('about.json')
    entries = await load_json_data('entries.json')
    strings = await load_json_data('strings.json')
    return {
        'about': about,
        'entries': entries,
        'strings': strings
    }

async def handle_save_about(request):
    try:
        data = await request.json()
        about_path = Path(__file__).parent / 'data' / 'about.json'
        with open(about_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return web.json_response({'status': 'ok'})
    except Exception as e:
        return web.json_response({'status': 'error', 'error': str(e)}, status=500)

@aiohttp_jinja2.template('entry_detail.html')
async def handle_entry_detail(request):
    entry_id = int(request.match_info['entry_id'])
    entries = await load_json_data('entries.json')
    about = await load_json_data('about.json')
    strings_all = await load_json_data('strings.json')
    lang = 'en'
    strings = strings_all.get(lang, {})
    if 0 <= entry_id < len(entries):
        entry = entries[entry_id]
    else:
        raise web.HTTPNotFound()
    return {
        'about': about,
        'entry': entry,
        'strings': strings
    }

def create_app():
    app = web.Application()
    
    # Setup Jinja2 template engine
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(str(Path(__file__).parent / 'templates'))
    )
    
    # Add static file serving
    app.router.add_static('/static', path=str(Path(__file__).parent / 'static'), name='static')
    
    # Add routes
    app.router.add_get('/', handle_index)
    app.router.add_post('/submit', handle_submit)
    app.router.add_get('/admin', handle_admin)
    app.router.add_post('/admin/save_about', handle_save_about)
    app.router.add_get('/entry/{entry_id}', handle_entry_detail)
    
    return app