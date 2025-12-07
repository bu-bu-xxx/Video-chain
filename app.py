"""
Video Chain Web Interface - Flask application for video generation
"""
import os
import json
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from video_chain import VideoChainWorkflow

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global workflow instance
workflow = None


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate_video():
    """
    API endpoint to generate video
    Expects:
        - description: text description (required)
        - image: reference image file (optional)
        - segments: number of segments (optional, default 3)
        - size: video size (optional, default "1280x720")
        - duration: duration per segment (optional, default 4)
    """
    global workflow
    
    try:
        # Initialize workflow if not already done
        if workflow is None:
            workflow = VideoChainWorkflow()
        
        # Get form data
        description = request.form.get('description')
        if not description:
            return jsonify({'error': '请提供视频描述'}), 400
        
        segments = int(request.form.get('segments', 3))
        size = request.form.get('size', '1280x720')
        duration = int(request.form.get('duration', 4))
        
        # Handle reference image if provided
        reference_image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                filename = f"{int(time.time())}_{filename}"
                reference_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(reference_image_path)
        
        # Create unique output directory for this request
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], f"video_{int(time.time())}")
        
        # Run the workflow
        print(f"Starting workflow with description: {description}")
        final_video = workflow.run_workflow(
            user_description=description,
            reference_image_path=reference_image_path,
            num_segments=segments,
            size=size,
            seconds_per_segment=duration,
            output_dir=output_dir
        )
        
        if final_video and os.path.exists(final_video):
            # Return relative path for download
            relative_path = os.path.relpath(final_video, app.config['OUTPUT_FOLDER'])
            return jsonify({
                'success': True,
                'video_path': relative_path,
                'download_url': f'/api/download/{relative_path}'
            })
        else:
            return jsonify({'error': '视频生成失败'}), 500
            
    except ValueError as e:
        return jsonify({'error': f'配置错误: {str(e)}'}), 500
    except Exception as e:
        print(f"Error in generate_video: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成视频时出错: {str(e)}'}), 500


@app.route('/api/download/<path:video_path>')
def download_video(video_path):
    """Download generated video"""
    try:
        # Prevent path traversal attacks
        full_path = os.path.abspath(os.path.join(app.config['OUTPUT_FOLDER'], video_path))
        output_folder_abs = os.path.abspath(app.config['OUTPUT_FOLDER'])
        
        # Ensure the resolved path is within the output folder
        if not full_path.startswith(output_folder_abs):
            return jsonify({'error': '无效的文件路径'}), 400
        
        if os.path.exists(full_path):
            return send_file(full_path, as_attachment=True)
        else:
            return jsonify({'error': '视频文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status')
def status():
    """Check API status"""
    try:
        api_key = os.getenv('AIHUBMIX_API_KEY')
        return jsonify({
            'status': 'ok',
            'api_key_set': bool(api_key)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    # Run the Flask app
    print("启动视频链Web界面...")
    print("访问 http://127.0.0.1:5000 打开界面")
    # Use debug=False for production, or set via environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
