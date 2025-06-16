from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
import os
from qr_code import create_rainbow_qr_code
import uuid
import time
import logging

app = Flask(__name__, 
    static_folder='static',
    static_url_path='/static'
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure the static directories exist
os.makedirs('static/qrcodes', exist_ok=True)
os.makedirs('static/videos', exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/background')
def serve_background():
    try:
        return send_from_directory('static/videos', 'Background.gif')
    except Exception as e:
        logger.error(f"Error serving background: {str(e)}")
        return str(e), 500

@app.route('/test-video')
def test_video():
    try:
        video_path = os.path.join('static/videos', 'Background.mp4')
        if os.path.exists(video_path):
            return send_file(video_path, mimetype='video/mp4')
        else:
            return f"Video file not found at: {os.path.abspath(video_path)}", 404
    except Exception as e:
        logger.error(f"Error serving video: {str(e)}")
        return str(e), 500

@app.route('/static/videos/<path:filename>')
def serve_video(filename):
    try:
        video_path = os.path.join('static/videos', filename)
        if os.path.exists(video_path):
            logger.debug(f"Serving file: {video_path}")
            return send_file(
                video_path,
                mimetype='video/mp4' if filename.endswith('.mp4') else 'image/gif',
                as_attachment=False,
                conditional=True
            )
        else:
            logger.error(f"File not found: {video_path}")
            return "File not found", 404
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        return str(e), 500

# Add specific route for GIF files
@app.route('/static/videos/Background.gif')
def serve_background_gif():
    try:
        gif_path = os.path.join('static/videos', 'Background.gif')
        logger.debug(f"Attempting to serve GIF from: {gif_path}")
        if os.path.exists(gif_path):
            return send_file(
                gif_path,
                mimetype='image/gif',
                as_attachment=False,
                conditional=True
            )
        else:
            logger.error(f"GIF file not found at: {gif_path}")
            return "GIF not found", 404
    except Exception as e:
        logger.error(f"Error serving GIF: {str(e)}")
        return str(e), 500

@app.route('/generate', methods=['POST'])
def generate_qr():
    try:
        url = request.form.get('url')
        logo_url = request.form.get('logo') or None
        
        logger.debug(f"Received request - URL: {url}, Logo URL: {logo_url}")
        
        if not url:
            logger.error("No URL provided")
            return jsonify({'error': 'URL is required'}), 400

        # Generate unique filename
        filename = f"{base_name}.png"
        filepath = os.path.join('static/qrcodes', filename)
        
        logger.debug(f"Generating QR code at path: {filepath}")

        # Generate QR code
        try:
            create_rainbow_qr_code(url, filepath, logo_url)
            logger.debug("QR code generated successfully")
        except Exception as qr_error:
            logger.error(f"Error generating QR code: {str(qr_error)}")
            return jsonify({'error': f'Failed to generate QR code: {str(qr_error)}'}), 500

        # Verify the file was created
        if not os.path.exists(filepath):
            logger.error("QR code file was not created")
            return jsonify({'error': 'Failed to save QR code'}), 500

        return jsonify({
            'success': True,
            'qrcode_url': f'/static/qrcodes/{filename}'         
        })

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Clean up old QR codes periodically
@app.before_request
def cleanup_old_qrcodes():
    try:
        qrcode_dir = os.path.join('static', 'qrcodes')
        if os.path.exists(qrcode_dir):
            for file in os.listdir(qrcode_dir):
                file_path = os.path.join(qrcode_dir, file)
                # Remove files older than 1 hour
                if os.path.getmtime(file_path) < (time.time() - 3600):
                    os.remove(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up QR codes: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=5000) 