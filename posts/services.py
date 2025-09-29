import os
import tempfile
from io import BytesIO
from PIL import Image
from moviepy import VideoFileClip

from supabase import create_client
from storage3.exceptions import StorageApiError

from django.conf import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def upload_to_supabase(file):
    """
    Uploads a file (image or video) to Supabase storage.
    - Compresses images.
    - Creates video thumbnails & extracts duration.
    Returns: (file_url, file_size, duration, thumbnail_url)
    """
    bucket = "post-images"
    folder = "uploads"
    file_ext = file.name.split(".")[-1]
    file_name = f"{folder}/{file.name}"

    
    file.seek(0)
    file_content = file.read()
    file_size = len(file_content)

    duration = None
    thumbnail_url = None

    # ----------------- VIDEO HANDLING -----------------
    if "video" in file.content_type:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        clip = VideoFileClip(tmp_path)
        duration = clip.duration

    
        try:
            with open(tmp_path, "rb") as f:
                supabase.storage.from_(bucket).upload(file_name, f, {"upsert": "true"})
        except StorageApiError as e:
            raise Exception(f"Video upload failed: {e.message}")

        
        thumb_path = tmp_path.replace(f".{file_ext}", "_thumb.jpg")
        clip.save_frame(thumb_path, t=1.0)
        thumb_name = f"{folder}/thumbnails/{file.name}.jpg"

        try:
            with open(thumb_path, "rb") as thumb_file:
                supabase.storage.from_(bucket).upload(thumb_name, thumb_file, {"upsert": "true"})
        except StorageApiError as e:
            raise Exception(f"Thumbnail upload failed: {e.message}")

        
        file_url = supabase.storage.from_(bucket).get_public_url(file_name)
        thumbnail_url = supabase.storage.from_(bucket).get_public_url(thumb_name)

        
        clip.close()
        os.remove(tmp_path)
        os.remove(thumb_path)

    # ----------------- IMAGE HANDLING -----------------
    elif "image" in file.content_type:
        img = Image.open(BytesIO(file_content))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", optimize=True, quality=95)
        compressed_content = buffer.getvalue()

        try:
            supabase.storage.from_(bucket).upload(file_name, compressed_content, {"upsert": "true"})
        except StorageApiError as e:
            raise Exception(f"Image upload failed: {e.message}")

        file_url = supabase.storage.from_(bucket).get_public_url(file_name)

    else:
        raise Exception(f"Unsupported file type: {file.content_type}")

    return file_url, file_size, duration, thumbnail_url
