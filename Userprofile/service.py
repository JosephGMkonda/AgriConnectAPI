from io import BytesIO
from PIL import Image
from supabase import create_client
from storage3.exceptions import StorageApiError
from django.conf import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def upload_profile_avatar(file):
    """
    Uploads and compresses a user avatar image to Supabase storage.
    Returns: file_url (public URL), file_size
    """
    bucket = "user-avatars"  
    folder = "avatars"
    file_ext = file.name.split(".")[-1]
    file_name = f"{folder}/{file.name}"

    
    file.seek(0)
    file_content = file.read()
    file_size = len(file_content)

    
    img = Image.open(BytesIO(file_content))
    buffer = BytesIO()
    img.save(buffer, format="JPEG", optimize=True, quality=95)
    compressed_content = buffer.getvalue()

    try:
        supabase.storage.from_(bucket).upload(file_name, compressed_content, {"upsert": "true"})
    except StorageApiError as e:
        raise Exception(f"Avatar upload failed: {e.message}")

    file_url = supabase.storage.from_(bucket).get_public_url(file_name)

    return file_url, file_size
