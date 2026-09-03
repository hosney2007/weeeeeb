import os
import uuid
from flask import url_for, flash
from werkzeug.utils import secure_filename
from supabase import create_client
from utils.decorators import save_image, validate_image

COURSE_BUCKET = "image"


def get_supabase():
    """Returns a Supabase client, or None if the env vars aren't configured."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def upload_course_image(image, folder="courses"):
    """
    Uploads an image to Supabase storage and returns its public URL.
    Falls back to saving it locally under /static/uploads if Supabase
    isn't configured. Returns None if there's no image to upload.
    """
    if not image or not image.filename:
        return None

    # Same extension/mimetype/"is this really an image" checks run
    # regardless of where the file ends up (Supabase or local disk).
    try:
        extension = validate_image(image)
    except ValueError as e:
        flash(str(e), "danger")
        return None

    storage = get_supabase()
    if storage:
        filename = secure_filename(image.filename)
        file_path = f"{folder}/{uuid.uuid4()}_{filename}"
        try:
            storage.storage.from_(COURSE_BUCKET).upload(
                file_path, image.read(), {"content-type": image.content_type}
            )
            return storage.storage.from_(COURSE_BUCKET).get_public_url(file_path)
        except Exception:
            flash("Image upload failed, please try again.", "danger")
            return None

    image.seek(0)
    try:
        relative = save_image(image, folder, extension=extension)
    except ValueError as e:
        # لو الملف مش صورة صحيحة، منمنعش الادمن يكمل من غير ما نديله رسالة واضحة
        flash(str(e), "danger")
        return None
    return url_for("static", filename=f"uploads/{relative}") if relative else None
