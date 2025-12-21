"""Media asset management with cloud storage integration."""

from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO
import mimetypes
import hashlib
import uuid
from PIL import Image
import io

from app.models import MediaType
from app.core.config import settings


class MediaManager:
    """Manage media assets with cloud storage support.

    Supports:
    - Local storage (development)
    - AWS S3
    - Image resizing and optimization
    - Video thumbnail generation
    - File validation
    """

    def __init__(self, storage_backend: str = "local"):
        """Initialize media manager.

        Args:
            storage_backend: "local", "s3", or "gcs"
        """
        self.storage_backend = storage_backend
        self.local_storage_path = Path("media")
        self.local_storage_path.mkdir(exist_ok=True)

        # Initialize cloud client if configured
        if storage_backend == "s3" and settings.AWS_ACCESS_KEY_ID:
            import boto3
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            self.bucket = settings.AWS_S3_BUCKET
        else:
            self.s3_client = None

    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        folder: str = "uploads",
    ) -> dict[str, Any]:
        """Upload a file to storage.

        Args:
            file: File object or bytes
            filename: Original filename
            folder: Storage folder/prefix

        Returns:
            {
                "storage_url": str,
                "file_name": str,
                "file_size": int,
                "mime_type": str,
                "media_type": MediaType,
                "width": int | None,
                "height": int | None,
                "duration": int | None,
                "thumbnail_url": str | None,
            }
        """
        # Read file content
        if hasattr(file, 'read'):
            file_content = file.read()
            file.seek(0)  # Reset for potential reuse
        else:
            file_content = file

        # Generate unique filename
        file_hash = hashlib.md5(file_content).hexdigest()[:8]
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4().hex}_{file_hash}{file_ext}"

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"

        # Determine media type
        media_type = self._get_media_type(mime_type)

        # Get file metadata
        metadata = {
            "file_name": filename,
            "file_size": len(file_content),
            "mime_type": mime_type,
            "media_type": media_type,
            "width": None,
            "height": None,
            "duration": None,
            "thumbnail_url": None,
        }

        # Extract image dimensions
        if media_type == MediaType.IMAGE:
            try:
                image = Image.open(io.BytesIO(file_content))
                metadata["width"] = image.width
                metadata["height"] = image.height
            except Exception:
                pass

        # Upload to storage
        if self.storage_backend == "s3" and self.s3_client:
            storage_url = await self._upload_to_s3(
                file_content,
                f"{folder}/{unique_filename}",
                mime_type,
            )
        else:
            storage_url = await self._upload_to_local(
                file_content,
                folder,
                unique_filename,
            )

        metadata["storage_url"] = storage_url

        # Generate thumbnail for images
        if media_type == MediaType.IMAGE:
            thumbnail_url = await self._generate_thumbnail(
                file_content,
                f"{folder}/thumbnails/{unique_filename}",
            )
            metadata["thumbnail_url"] = thumbnail_url

        return metadata

    async def _upload_to_s3(
        self,
        file_content: bytes,
        key: str,
        mime_type: str,
    ) -> str:
        """Upload file to AWS S3.

        Args:
            file_content: File bytes
            key: S3 object key
            mime_type: MIME type

        Returns:
            S3 URL
        """
        if not self.s3_client:
            raise ValueError("S3 client not configured")

        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_content,
            ContentType=mime_type,
        )

        return f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

    async def _upload_to_local(
        self,
        file_content: bytes,
        folder: str,
        filename: str,
    ) -> str:
        """Upload file to local storage.

        Args:
            file_content: File bytes
            folder: Local folder
            filename: Filename

        Returns:
            Local file path
        """
        folder_path = self.local_storage_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = folder_path / filename
        file_path.write_bytes(file_content)

        return f"/media/{folder}/{filename}"

    async def _generate_thumbnail(
        self,
        image_content: bytes,
        key: str,
        size: tuple[int, int] = (300, 300),
    ) -> str | None:
        """Generate and upload thumbnail for an image.

        Args:
            image_content: Original image bytes
            key: Storage key for thumbnail
            size: Thumbnail size (width, height)

        Returns:
            Thumbnail URL or None
        """
        try:
            image = Image.open(io.BytesIO(image_content))
            image.thumbnail(size, Image.Resampling.LANCZOS)

            # Convert to bytes
            thumb_buffer = io.BytesIO()
            image.save(thumb_buffer, format=image.format or "JPEG")
            thumb_content = thumb_buffer.getvalue()

            # Upload thumbnail
            if self.storage_backend == "s3" and self.s3_client:
                return await self._upload_to_s3(
                    thumb_content,
                    key,
                    "image/jpeg",
                )
            else:
                folder = Path(key).parent
                filename = Path(key).name
                return await self._upload_to_local(
                    thumb_content,
                    str(folder),
                    filename,
                )
        except Exception:
            return None

    async def resize_image(
        self,
        image_content: bytes,
        width: int | None = None,
        height: int | None = None,
        maintain_aspect: bool = True,
    ) -> bytes:
        """Resize an image.

        Args:
            image_content: Original image bytes
            width: Target width (optional)
            height: Target height (optional)
            maintain_aspect: Maintain aspect ratio

        Returns:
            Resized image bytes
        """
        image = Image.open(io.BytesIO(image_content))

        if maintain_aspect:
            if width and height:
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
            elif width:
                ratio = width / image.width
                height = int(image.height * ratio)
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            elif height:
                ratio = height / image.height
                width = int(image.width * ratio)
                image = image.resize((width, height), Image.Resampling.LANCZOS)
        else:
            if width and height:
                image = image.resize((width, height), Image.Resampling.LANCZOS)

        # Save to bytes
        buffer = io.BytesIO()
        image.save(buffer, format=image.format or "JPEG")
        return buffer.getvalue()

    async def optimize_image(
        self,
        image_content: bytes,
        quality: int = 85,
        max_size: int | None = None,
    ) -> bytes:
        """Optimize image for web.

        Args:
            image_content: Original image bytes
            quality: JPEG quality (1-100)
            max_size: Maximum file size in bytes

        Returns:
            Optimized image bytes
        """
        image = Image.open(io.BytesIO(image_content))

        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background

        # Optimize
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        optimized = buffer.getvalue()

        # Check size and reduce quality if needed
        if max_size and len(optimized) > max_size and quality > 60:
            return await self.optimize_image(
                image_content,
                quality=quality - 10,
                max_size=max_size,
            )

        return optimized

    async def delete_file(self, storage_url: str) -> bool:
        """Delete a file from storage.

        Args:
            storage_url: File URL

        Returns:
            True if successful
        """
        if self.storage_backend == "s3" and self.s3_client:
            # Extract key from URL
            key = storage_url.split(f"{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/")[1]
            try:
                self.s3_client.delete_object(Bucket=self.bucket, Key=key)
                return True
            except Exception:
                return False
        else:
            # Local storage
            try:
                file_path = self.local_storage_path / storage_url.lstrip("/media/")
                file_path.unlink(missing_ok=True)
                return True
            except Exception:
                return False

    def _get_media_type(self, mime_type: str) -> MediaType:
        """Determine media type from MIME type.

        Args:
            mime_type: MIME type string

        Returns:
            MediaType enum
        """
        if mime_type.startswith("image/"):
            return MediaType.IMAGE
        elif mime_type.startswith("video/"):
            return MediaType.VIDEO
        elif mime_type.startswith("audio/"):
            return MediaType.AUDIO
        else:
            return MediaType.DOCUMENT

    def validate_file(
        self,
        file_size: int,
        mime_type: str,
        platform: str | None = None,
    ) -> tuple[bool, str | None]:
        """Validate file against platform requirements.

        Args:
            file_size: File size in bytes
            mime_type: MIME type
            platform: Platform name (optional)

        Returns:
            Tuple of (is_valid, error_message)
        """
        media_type = self._get_media_type(mime_type)

        # Platform-specific limits
        limits = {
            "twitter": {
                MediaType.IMAGE: 5 * 1024 * 1024,  # 5 MB
                MediaType.VIDEO: 512 * 1024 * 1024,  # 512 MB
            },
            "instagram": {
                MediaType.IMAGE: 8 * 1024 * 1024,  # 8 MB
                MediaType.VIDEO: 100 * 1024 * 1024,  # 100 MB
            },
            "youtube": {
                MediaType.VIDEO: 256 * 1024 * 1024 * 1024,  # 256 GB
            },
            "facebook": {
                MediaType.IMAGE: 4 * 1024 * 1024,  # 4 MB
                MediaType.VIDEO: 10 * 1024 * 1024 * 1024,  # 10 GB
            },
            "linkedin": {
                MediaType.IMAGE: 5 * 1024 * 1024,  # 5 MB
                MediaType.VIDEO: 5 * 1024 * 1024 * 1024,  # 5 GB
            },
        }

        if platform and platform.lower() in limits:
            platform_limits = limits[platform.lower()]
            max_size = platform_limits.get(media_type)

            if max_size and file_size > max_size:
                return False, f"File size exceeds {platform} limit of {max_size / (1024*1024):.1f} MB"

        # General validation
        max_general_size = 1024 * 1024 * 1024  # 1 GB default max
        if file_size > max_general_size:
            return False, f"File size exceeds maximum of {max_general_size / (1024*1024):.1f} MB"

        return True, None


class BatchMediaProcessor:
    """Process multiple media files in batch."""

    def __init__(self, media_manager: MediaManager):
        """Initialize batch processor.

        Args:
            media_manager: MediaManager instance
        """
        self.media_manager = media_manager

    async def resize_batch(
        self,
        files: list[tuple[bytes, str]],
        width: int,
        height: int,
    ) -> list[bytes]:
        """Resize multiple images.

        Args:
            files: List of (file_content, filename) tuples
            width: Target width
            height: Target height

        Returns:
            List of resized image bytes
        """
        results = []
        for content, filename in files:
            resized = await self.media_manager.resize_image(
                content,
                width=width,
                height=height,
            )
            results.append(resized)

        return results

    async def optimize_batch(
        self,
        files: list[bytes],
        quality: int = 85,
    ) -> list[bytes]:
        """Optimize multiple images.

        Args:
            files: List of image bytes
            quality: JPEG quality

        Returns:
            List of optimized image bytes
        """
        results = []
        for content in files:
            optimized = await self.media_manager.optimize_image(content, quality)
            results.append(optimized)

        return results
