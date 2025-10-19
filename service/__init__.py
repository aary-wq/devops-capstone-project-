import sys
from flask import Flask
from flask_talisman import Talisman
from service import config
from service.common import log_handlers
from flask_cors import CORS

# Create Flask application
app = Flask(__name__)

# Initialize Flask-Talisman with HTTPS enforcement disabled for testing
# (prevents test client requests from being redirected with HTTP 302)
talisman = Talisman(app, force_https=False)
CORS(app)
# Load configuration settings
app.config.from_object(config)

# Import routes and models after the Flask app is created
from service import routes, models  # noqa: F401 E402

# Import error handlers and CLI commands
from service.common import error_handlers, cli_commands  # noqa: F401 E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    # Initialize database tables
    models.init_db(app)
except Exception as error:  # pylint: disable=broad-except
    app.logger.critical("%s: Cannot continue", error)
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info("Service initialized!")
