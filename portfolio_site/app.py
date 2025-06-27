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
import hashlib
import secrets

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

# Simple password hashing functions
def hash_password(password):
    """Create a simple hash of the password with salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256()
    hash_obj.update((password + salt).encode('utf-8'))
    return f"{salt}${hash_obj.hexdigest()}"

def verify_password(password, stored_hash):
    """Verify a password against a stored hash"""
    if not stored_hash or '$' not in stored_hash:
        return False
    salt, hash_value = stored_hash.split('$', 1)
    hash_obj = hashlib.sha256()
    hash_obj.update((password + salt).encode('utf-8'))
    return hash_obj.hexdigest() == hash_value

def get_default_password_hash():
    """Get hash for default password '1234'"""
    return hash_password('1234')

# Session management
sessions = {}  # In production, use a proper session store

def create_session():
    """Create a new admin session"""
    session_id = secrets.token_hex(32)
    sessions[session_id] = {'authenticated': True, 'created': time.time()}
    return session_id

def verify_session(session_id):
    """Verify if a session is valid"""
    if session_id not in sessions:
        return False
    session = sessions[session_id]
    # Sessions expire after 24 hours
    if time.time() - session['created'] > 86400:
        del sessions[session_id]
        return False
    return session['authenticated']

def clear_session(session_id):
    """Clear a session"""
    if session_id in sessions:
        del sessions[session_id]

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
    """Handle admin panel - requires authentication"""
    # Check authentication
    session_id = request.cookies.get('admin_session')
    if not session_id or not verify_session(session_id):
        raise web.HTTPFound('/admin/login')
    
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

async def handle_save_entries(request):
    try:
        data = await request.json()
        entries_path = Path(__file__).parent / 'data' / 'entries.json'
        with open(entries_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return web.json_response({'status': 'ok'})
    except Exception as e:
        return web.json_response({'status': 'error', 'error': str(e)}, status=500)

async def handle_admin_login(request):
    """Handle admin login"""
    try:
        data = await request.json()
        password = data.get('password', '')
        
        # Load about data to get stored password hash
        about = await load_json_data('about.json')
        stored_hash = about.get('admin_password_hash')
        
        # If no password hash exists, create one with default password '1234'
        if not stored_hash:
            stored_hash = get_default_password_hash()
            about['admin_password_hash'] = stored_hash
            about_path = Path(__file__).parent / 'data' / 'about.json'
            with open(about_path, 'w', encoding='utf-8') as f:
                json.dump(about, f, ensure_ascii=False, indent=2)
        
        if verify_password(password, stored_hash):
            session_id = create_session()
            response = web.json_response({'status': 'ok'})
            response.set_cookie('admin_session', session_id, max_age=86400, httponly=True)
            return response
        else:
            return web.json_response({'status': 'error', 'message': 'Invalid password'}, status=401)
            
    except Exception as e:
        logger.exception("Error during login")
        return web.json_response({'status': 'error', 'message': 'Login failed'}, status=500)

async def handle_change_password(request):
    """Handle password change from admin panel"""
    try:
        data = await request.json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        # Load about data
        about = await load_json_data('about.json')
        stored_hash = about.get('admin_password_hash')
        
        # Verify current password
        if not verify_password(current_password, stored_hash):
            return web.json_response({'status': 'error', 'message': 'Current password is incorrect'}, status=401)
        
        # Hash new password and save
        new_hash = hash_password(new_password)
        about['admin_password_hash'] = new_hash
        
        about_path = Path(__file__).parent / 'data' / 'about.json'
        with open(about_path, 'w', encoding='utf-8') as f:
            json.dump(about, f, ensure_ascii=False, indent=2)
        
        return web.json_response({'status': 'ok', 'message': 'Password changed successfully'})
        
    except Exception as e:
        logger.exception("Error changing password")
        return web.json_response({'status': 'error', 'message': 'Failed to change password'}, status=500)

async def handle_logout(request):
    """Handle admin logout"""
    session_id = request.cookies.get('admin_session')
    if session_id:
        clear_session(session_id)
    
    response = web.HTTPFound('/admin/login')
    response.del_cookie('admin_session')
    return response

@aiohttp_jinja2.template('admin_login.html')
async def handle_admin_login_page(request):
    """Show admin login page"""
    return {}

async def handle_test_route(request):
    """Test route to verify routing is working"""
    entry_id = request.match_info.get('entry_id', 'no_id')
    return web.Response(text=f"Test route working! Entry ID: {entry_id}")

@aiohttp_jinja2.template('entry_detail.html')
async def handle_entry_detail(request):
    entry_id = int(request.match_info['entry_id'])
    entries = await load_json_data('entries.json')
    about = await load_json_data('about.json')
    strings_all = await load_json_data('strings.json')
    lang = 'en'
    strings = strings_all.get(lang, {})
    
    # Debug logging
    logger.info(f"Requested entry_id: {entry_id}")
    logger.info(f"Available entries: {[e.get('id') for e in entries]}")
    
    # Find entry by ID instead of array index
    entry = None
    for e in entries:
        if e.get('id') == entry_id:
            entry = e
            logger.info(f"Found entry: {entry.get('title')}")
            break
    
    if entry:
        return {
            'about': about,
            'entry': entry,
            'strings': strings
        }
    else:
        logger.error(f"Entry with id {entry_id} not found")
        raise web.HTTPNotFound()

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
    app.router.add_post('/admin/save_entries', handle_save_entries)
    app.router.add_get('/entry/{entry_id}', handle_entry_detail)
    app.router.add_get('/test/{entry_id}', handle_test_route)
    app.router.add_post('/admin/login', handle_admin_login)
    app.router.add_post('/admin/change_password', handle_change_password)
    app.router.add_get('/admin/logout', handle_logout)
    app.router.add_get('/admin/login', handle_admin_login_page)
    
    return app