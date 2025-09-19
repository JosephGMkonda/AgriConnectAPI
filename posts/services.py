import os
from moviepy import VideoFileClip
from PIL import Image
from io import BytesIO
from supabase import create_client
import tempfile

from django.conf import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def upload_to_supabase(file):
    """
    Uploads a file (image/video) to Supabase storage, creates thumbnails for videos,
    and returns file_url, file_size, duration, thumbnail_url
    """
    print(f"Uploading file: {file.name}, type: {file.content_type}") 
    bucket = "post-images"
    folder = "uploads"


    file_ext = file.name.split(".")[-1]
    file_name = f"{folder}/{file.name}"

    
    file.seek(0)


    file_content = file.read()

    
    res = supabase.storage.from_(bucket).upload(file_name, file_content, {"upsert": True})
    if res.get("error"):
        raise Exception(res["error"]["message"])

    file_url_data = supabase.storage.from_(bucket).get_public_url(file_name)
    file_url = file_url_data.get("publicUrl") or file_url_data.get("public_url")


    size = len(file_content)

    duration = None
    thumbnail_url = None

    if "video" in file.content_type:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        clip = VideoFileClip(tmp_path)
        duration = clip.duration

        
        thumb_path = tmp_path.replace(f".{file_ext}", "_thumb.jpg")
        clip.save_frame(thumb_path, t=1.0)

        
        thumb_name = f"{folder}/thumbnails/{file.name}.jpg"
        with open(thumb_path, "rb") as thumb_file:
            supabase.storage.from_(bucket).upload(thumb_name, thumb_file, {"upsert": True})
        thumb_url_data = supabase.storage.from_(bucket).get_public_url(thumb_name)
        thumbnail_url = thumb_url_data.get("publicUrl") or thumb_url_data.get("public_url")

        
        clip.close()
        os.remove(tmp_path)
        os.remove(thumb_path)

    elif "image" in file.content_type:
        
        img = Image.open(BytesIO(file_content))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", optimize=True, quality=70)
        compressed_file = buffer.getvalue()

        
        supabase.storage.from_(bucket).upload(file_name, compressed_file, {"upsert": True})
        file_url_data = supabase.storage.from_(bucket).get_public_url(file_name)
        file_url = file_url_data.get("publicUrl") or file_url_data.get("public_url")
        print("File URL:", file_url)

    return file_url, size, duration, thumbnail_url
