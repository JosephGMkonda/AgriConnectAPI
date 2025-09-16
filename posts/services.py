import os
from moviepy import VideoFileClip
from PIL import Image
from io import BytesIO
from supabase import create_client
import tempfile


from django.conf import settings
from supabase import create_client, Client

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)





def upload_to_supabase(file):
    bucket = "post-images"
    folder = "uploads"

    file_ext = file.name.split(".")[-1]
    file_name = f"{folder}/{file.name}"

    
    res = supabase.storage.from_(bucket).upload(file_name, file.read(), {"upsert": True})
    if res.get("error"):
        raise Exception(res["error"]["message"])
    public_url = supabase.storage.from_(bucket).get_public_url(file_name)

    
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    duration = None
    thumbnail_url = None

    if "video" in file.content_type:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        clip = VideoFileClip(tmp_path)
        duration = clip.duration

        
        thumb_path = tmp_path.replace(f".{file_ext}", "_thumb.jpg")
        clip.save_frame(thumb_path, t=1.0)

        thumb_name = f"{folder}/thumbs/{file.name}.jpg"
        with open(thumb_path, "rb") as thumb_file:
            supabase.storage.from_(bucket).upload(thumb_name, thumb_file, {"upsert": True})
        thumbnail_url = supabase.storage.from_(bucket).get_public_url(thumb_name)

    elif "image" in file.content_type:
        
        img = Image.open(file)
        buffer = BytesIO()
        img.save(buffer, format="JPEG", optimize=True, quality=70)
        compressed_file = BytesIO(buffer.getvalue())

        supabase.storage.from_(bucket).upload(file_name, compressed_file, {"upsert": True})
        public_url = supabase.storage.from_(bucket).get_public_url(file_name)

    return public_url, size, duration, thumbnail_url
