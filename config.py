import os
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        import secrets
        SECRET_KEY = secrets.token_hex(32)
        print(
            "⚠️  WARNING: SECRET_KEY environment variable is not set. "
            "Using a random key generated at startup (sessions will invalidate on restart). "
            "Set the SECRET_KEY env var before deploying to production."
        )
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads" )
    # Reject request bodies over 10MB (protects against disk-filling / bandwidth abuse
    # via unbounded file uploads on payment images, sheets, thumbnails, etc.)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///database.db")
    # Some providers still expose the legacy postgres:// scheme.
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://" + SQLALCHEMY_DATABASE_URI[len("postgres://"):]
    # Hostinger (and most hosts) give a plain mysql:// URL; SQLAlchemy needs a
    # driver name in the scheme, so default it to PyMySQL if none was given.
    if SQLALCHEMY_DATABASE_URI.startswith("mysql://"):
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://" + SQLALCHEMY_DATABASE_URI[len("mysql://"):]
    if SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
        print(
            "⚠️  WARNING: Running on SQLite. This is fine for local development, "
            "but on a real deployment set DATABASE_URL to your Hostinger MySQL "
            "database instead (see .env.example) so data isn't lost or shared "
            "incorrectly between app restarts/workers."
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = ("ma0332897@gmail.com")
    MAIL_PASSWORD= ("qqcyupvnevpxyusj")
    MAIL_DEFAULT_SENDER= "ma0332897@gmail.com"
    # Where "new order" emails go (course/book purchases, new bookings).
    # Defaults to the same inbox used to send mail if not set separately.
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", MAIL_USERNAME)

    # Payment details shown on the recorded-course payment page. Set these
    # via env vars for the real account details before deploying — the
    # fallback values below are placeholders only.
    VODAFONE_CASH_NUMBER = os.getenv("VODAFONE_CASH_NUMBER", "01012345678")
    INSTAPAY_ID = os.getenv("INSTAPAY_ID", "mohamedhosney@instapay")