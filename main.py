import aiohttp
from aiohttp import web
import logging
from logging.handlers import RotatingFileHandler

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

# HTML template for the form
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Resume Request</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }
        .form-container {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        input[type="email"] {
            width: 100%;
            padding: 8px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #0056b3;
        }
        .message {
            margin-top: 20px;
            padding: 10px;
            border-radius: 4px;
        }
        .success {
            background: #d4edda;
            color: #155724;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>Request Resume</h1>
        <p>Enter your email address below and we'll send you the resume.</p>
        <form method="POST" action="/submit">
            <input type="email" name="email" placeholder="Enter your email" required>
            <button type="submit">Send Resume</button>
        </form>
        <div id="message"></div>
    </div>
    <script>
        document.querySelector('form').addEventListener('submit', function(e) {
            e.preventDefault();
            const form = this;
            const messageDiv = document.getElementById('message');
            
            fetch('/submit', {
                method: 'POST',
                body: new FormData(form)
            })
            .then(response => response.json())
            .then(data => {
                messageDiv.textContent = data.message;
                messageDiv.className = 'message success';
                form.reset();
            })
            .catch(error => {
                messageDiv.textContent = 'An error occurred. Please try again.';
                messageDiv.className = 'message error';
            });
        });
    </script>
</body>
</html>
"""

async def handle_index(request):
    return web.Response(text=HTML, content_type='text/html')

async def handle_submit(request):
    try:
        data = await request.post()
        email = data.get('email', '')
        
        if not email:
            return web.json_response({
                'message': 'Email is required'
            }, status=400)
        
        # Here you would implement the email sending logic
        logger.info(f"Received resume request from: {email}")
        
        return web.json_response({
            'message': f'Thank you! We will send the resume to {email} shortly.'
        })
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return web.json_response({
            'message': 'An error occurred while processing your request'
        }, status=500)

def create_app():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_post('/submit', handle_submit)
    return app

app = create_app()

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000) 