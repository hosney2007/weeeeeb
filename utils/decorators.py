from functools import wraps
from flask import abort
from flask_login import current_user
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app
import uuid
import os

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def school_student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != "school_student":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
        



ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def validate_image(file):
    """
    Runs the same checks save_image used to run internally (extension,
    mimetype, and that the bytes are actually a decodable image), without
    writing anything to disk. Used by every upload path (local disk or
    Supabase) so an invalid file can never skip validation just because
    Supabase happens to be configured.

    Returns the lowercase file extension on success, or raises ValueError
    with a user-facing message. Leaves the file stream reset to position 0
    so the caller can read/save it afterwards.
    """
    if not file or file.filename == "":
        return None

    # الامتداد
    if "." not in file.filename:
        raise ValueError("Invalid file extension.")
    extension = file.filename.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid file extension.")

    if file.mimetype not in [
        "image/png",
        "image/jpeg",
        "image/webp"
    ]:
        raise ValueError("Invalid image type.")

    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)
    except Exception:
        raise ValueError("Invalid image.")

    return extension


def save_image(file, folder, extension=None):
    """
    Saves an already-uploaded image to local disk. If `extension` isn't
    passed in (i.e. the caller hasn't already run validate_image), this
    validates the file itself first.
    """
    if extension is None:
        extension = validate_image(file)
        if extension is None:
            return None

    filename = f"{uuid.uuid4()}.{extension}"

    save_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        folder,
        filename
    )

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)

    return f"{folder}/{filename}"


ALLOWED_SHEET_EXTENSIONS = {"pdf", "doc", "docx", "ppt", "pptx", "png", "jpg", "jpeg"}

def save_sheet_file(file, folder="school_sheets"):

    if not file or file.filename == "":
        return None

    if "." not in file.filename:
        raise ValueError("Invalid file extension.")
    extension = file.filename.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_SHEET_EXTENSIONS:
        raise ValueError("Invalid file extension.")

    filename = f"{uuid.uuid4()}.{extension}"

    folder_path = os.path.join(current_app.config["UPLOAD_FOLDER"], folder)
    os.makedirs(folder_path, exist_ok=True)

    save_path = os.path.join(folder_path, filename)
    file.save(save_path)

    return f"{folder}/{filename}"