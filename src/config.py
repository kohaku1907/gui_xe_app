import os

# Ensure resources directory exists
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
if not os.path.exists(RESOURCES_DIR):
    os.makedirs(RESOURCES_DIR)

# Database configuration
DB_PATH = os.path.join(RESOURCES_DIR, 'gui_xe.db')

# Application settings
APP_NAME = "Gaming Parking System"
APP_VERSION = "1.0.0"

# UI Settings
FONT_FAMILY = "Arial"
FONT_SIZE = 16
TITLE_FONT_SIZE = 28

# Ticket Settings
TICKET_TITLE = "GAMING PARKING"
TICKET_SUBTITLE = "GIỮ XE MIỄN PHÍ" 