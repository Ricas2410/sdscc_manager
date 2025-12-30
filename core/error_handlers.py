"""
Custom error handlers for SDSCC application.
"""

from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)


def custom_500_handler(request):
    """Custom 500 error handler that provides better feedback for upload errors."""
    
    # Check if this might be an upload-related error
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    referer = request.META.get('HTTP_REFERER', '')
    
    # If the referer contains member edit or add, it's likely an upload error
    if 'member' in referer and ('edit' in referer or 'add' in referer):
        logger.error(f"500 error on member form, likely upload issue. Referer: {referer}")
        
        return HttpResponse(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Form Submission Error</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #e74c3c; margin-bottom: 20px; }
                    .error-list { background: #fdf2f2; padding: 15px; border-radius: 5px; margin: 20px 0; }
                    .btn { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }
                    .btn-secondary { background: #95a5a6; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚠️ Form Submission Failed</h1>
                    <p><strong>The form could not be processed due to a file upload issue.</strong></p>
                    
                    <div class="error-list">
                        <h3>Possible Causes:</h3>
                        <ul>
                            <li>📁 Profile picture file is too large (maximum 5MB)</li>
                            <li>🌐 Poor internet connection during upload</li>
                            <li>📱 Invalid image format (please use JPG, PNG, or GIF)</li>
                            <li>⏱️ Upload timeout</li>
                        </ul>
                    </div>
                    
                    <h3>Recommended Solutions:</h3>
                    <ol>
                        <li>Try uploading a smaller profile picture (under 1MB recommended)</li>
                        <li>Check your internet connection and try again</li>
                        <li>Use a standard image format (JPG, PNG)</li>
                        <li>If the problem persists, try without uploading a profile picture first</li>
                    </ol>
                    
                    <div style="margin-top: 30px;">
                        <a href="javascript:history.back()" class="btn">← Go Back to Form</a>
                        <a href="/members/list/" class="btn btn-secondary">Member List</a>
                    </div>
                    
                    <p style="margin-top: 30px; font-size: 12px; color: #666;">
                        If this problem continues, please contact your system administrator.
                    </p>
                </div>
            </body>
            </html>
            """,
            status=500
        )
    
    # Default 500 handler for other errors
    return HttpResponse(
        """
        <!DOCTYPE html>
        <html>
        <head><title>Server Error</title></head>
        <body>
            <h1>Server Error</h1>
            <p>An unexpected error occurred. Please try again.</p>
            <button onclick="history.back()">Go Back</button>
        </body>
        </html>
        """,
        status=500
    )


def custom_400_handler(request, exception):
    """Custom 400 error handler."""
    return HttpResponse(
        """
        <!DOCTYPE html>
        <html>
        <head><title>Bad Request</title></head>
        <body>
            <h1>Bad Request</h1>
            <p>The request was invalid. Please try again.</p>
            <button onclick="history.back()">Go Back</button>
        </body>
        </html>
        """,
        status=400
    )


def custom_413_handler(request):
    """Custom 413 (Request Entity Too Large) error handler."""
    return HttpResponse(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>File Too Large</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #e74c3c; }
                .btn { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📁 File Too Large</h1>
                <p><strong>The file you uploaded exceeds the maximum allowed size of 5MB.</strong></p>
                <p>Please choose a smaller image file and try again.</p>
                <br>
                <a href="javascript:history.back()" class="btn">← Go Back</a>
            </div>
        </body>
        </html>
        """,
        status=413
    )
