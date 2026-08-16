import os
import io
import urllib.parse
import boto3
from PIL import Image

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        
        # Only process images inside uploads/ or attachments/ prefix, ignore existing thumbnails
        if not (key.startswith("attachments/") or key.startswith("uploads/")) or "thumbnails/" in key:
            continue
            
        file_ext = key.split('.')[-1].lower()
        if file_ext not in ['jpg', 'jpeg', 'png', 'webp']:
            print(f"Skipping non-image file: {key}")
            continue

        try:
            # Download image bytes directly from S3
            response = s3_client.get_object(Bucket=bucket, Key=key)
            image_content = response['Body'].read()

            # Generate Thumbnail using Pillow
            with Image.open(io.BytesIO(image_content)) as img:
                img.thumbnail((200, 200))
                out_buffer = io.BytesIO()
                
                fmt = 'PNG' if file_ext == 'png' else 'JPEG'
                img.save(out_buffer, format=fmt)
                out_buffer.seek(0)

            # Determine thumbnail target path: thumbnails/<ticket_id>/thumb_<filename>
            filename = os.path.basename(key)
            thumb_key = f"thumbnails/{filename}"

            # Write thumbnail back to S3
            s3_client.put_object(
                Bucket=bucket,
                Key=thumb_key,
                Body=out_buffer,
                ContentType=f'image/{file_ext}'
            )
            print(f"Successfully generated thumbnail: {thumb_key}")

        except Exception as e:
            print(f"Error processing {key}: {str(e)}")
            raise e