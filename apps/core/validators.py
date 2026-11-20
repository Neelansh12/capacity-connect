import os
from django.core.exceptions import ValidationError

ALLOWED_RESOURCE_EXTENSIONS = {
    '.pdf', '.ppt', '.pptx', '.doc', '.docx', '.xls', '.xlsx', 
    '.csv', '.txt', '.zip', '.mp4', '.png', '.jpg', '.jpeg'
}

ALLOWED_AVATAR_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.webp'
}

DANGEROUS_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.sh', '.php', '.phtml', '.js', 
    '.vbs', '.py', '.cgi', '.html', '.htm', '.svg', '.jar', '.war'
}

MAX_RESOURCE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_AVATAR_SIZE = 5 * 1024 * 1024     # 5MB


def validate_resource_file(file_obj):
    """
    Validates uploaded learning & trainer resource files:
    - Enforces maximum file size limit
    - Checks file extension against safe whitelist
    - Checks for dangerous script/executable extensions
    - Inspects file headers (magic bytes) to prevent extension spoofing
    """
    if not file_obj:
        return

    # Check file size
    if file_obj.size > MAX_RESOURCE_SIZE:
        raise ValidationError(f"File size exceeds maximum allowed limit of 50 MB (uploaded: {file_obj.size / (1024*1024):.1f} MB).")

    # Check extension
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext in DANGEROUS_EXTENSIONS:
        raise ValidationError(f"File type '{ext}' is prohibited for security reasons.")
    if ext not in ALLOWED_RESOURCE_EXTENSIONS:
        raise ValidationError(f"Unsupported file format '{ext}'. Allowed formats: PDF, PPT/PPTX, DOC/DOCX, XLS/XLSX, CSV, TXT, ZIP, MP4, PNG, JPG.")

    # Inspect magic bytes / file header
    file_obj.seek(0)
    header = file_obj.read(16)
    file_obj.seek(0)

    if ext == '.pdf' and not header.startswith(b'%PDF'):
        raise ValidationError("Invalid PDF file structure. The uploaded file does not match a valid PDF format.")
    elif ext in ('.docx', '.pptx', '.xlsx', '.zip') and not header.startswith(b'PK\x03\x04'):
        raise ValidationError(f"Invalid package format for '{ext}'. File header does not match expected container.")
    elif ext in ('.jpg', '.jpeg') and not header.startswith(b'\xff\xd8\xff'):
        raise ValidationError("Invalid JPEG image format.")
    elif ext == '.png' and not header.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValidationError("Invalid PNG image format.")
    elif ext in ('.csv', '.txt') and b'\x00' in header:
        raise ValidationError("Binary or corrupted data detected in text file.")


def validate_avatar_image(file_obj):
    """
    Validates user avatar / profile image uploads:
    - Enforces maximum 5MB size limit
    - Restricts to JPG, PNG, WEBP
    - Validates image header magic bytes
    """
    if not file_obj:
        return

    if file_obj.size > MAX_AVATAR_SIZE:
        raise ValidationError(f"Avatar image exceeds maximum allowed limit of 5 MB.")

    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_AVATAR_EXTENSIONS:
        raise ValidationError(f"Invalid image format '{ext}'. Allowed formats: JPG, PNG, WEBP.")

    file_obj.seek(0)
    header = file_obj.read(16)
    file_obj.seek(0)

    if ext in ('.jpg', '.jpeg') and not header.startswith(b'\xff\xd8\xff'):
        raise ValidationError("Uploaded file is not a valid JPEG image.")
    elif ext == '.png' and not header.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValidationError("Uploaded file is not a valid PNG image.")
    elif ext == '.webp' and not (header.startswith(b'RIFF') and b'WEBP' in header[:16]):
        raise ValidationError("Uploaded file is not a valid WEBP image.")

