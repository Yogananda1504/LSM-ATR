# ...existing code...

# Initialize Flask app
app = Flask(__name__)

# Add this line for Vercel deployment
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ...existing code...

# Change the last lines to this:
if __name__ == '__main__':
    app.run()
