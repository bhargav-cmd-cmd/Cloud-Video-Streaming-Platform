import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Video, User

# Try to import cv2 for thumbnail extraction. Fallback gracefully if not installed.
try:
    import cv2
except ImportError:
    cv2 = None

video_bp = Blueprint('video', __name__)

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov', 'mkv'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

def extract_thumbnail_from_video(video_path, thumbnail_dir):
    """
    Tries to capture a frame from the video at the 1-second mark using OpenCV.
    Saves the thumbnail as a JPEG in thumbnail_dir and returns the file name.
    """
    if not cv2:
        return None
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        # Try to capture at 1 second (1000 ms), or fallback to the beginning (0 ms)
        cap.set(cv2.CAP_PROP_POS_MSEC, 1000)
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_MSEC, 0)
            success, frame = cap.read()
            
        if success:
            thumb_filename = f"thumb_{uuid.uuid4().hex}.jpg"
            thumb_path = os.path.join(thumbnail_dir, thumb_filename)
            # Resize to standard 16:9 thumbnail size (640x360)
            resized_frame = cv2.resize(frame, (640, 360))
            cv2.imwrite(thumb_path, resized_frame)
            cap.release()
            return thumb_filename
            
        cap.release()
    except Exception as e:
        print(f"Error extracting thumbnail: {e}")
    return None

@video_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if 'video' not in request.files:
            flash('No video file selected.', 'danger')
            return redirect(url_for('video.upload'))
            
        video_file = request.files['video']
        
        if video_file.filename == '':
            flash('No video file selected.', 'danger')
            return redirect(url_for('video.upload'))
            
        if not title:
            flash('Please provide a video title.', 'danger')
            return redirect(url_for('video.upload'))
            
        if video_file and allowed_file(video_file.filename, ALLOWED_VIDEO_EXTENSIONS):
            # Secure filename and add uuid prefix to prevent collision
            ext = video_file.filename.rsplit('.', 1)[1].lower()
            unique_video_name = f"{uuid.uuid4().hex}.{ext}"
            video_path = os.path.join(current_app.config['UPLOAD_FOLDER_VIDEOS'], unique_video_name)
            
            # Ensure directories exist
            os.makedirs(current_app.config['UPLOAD_FOLDER_VIDEOS'], exist_ok=True)
            os.makedirs(current_app.config['UPLOAD_FOLDER_THUMBNAILS'], exist_ok=True)
            
            # Save the video
            video_file.save(video_path)
            
            thumbnail_filename = None
            
            # Check if custom thumbnail was uploaded
            custom_thumb = request.files.get('thumbnail')
            if custom_thumb and custom_thumb.filename != '':
                if allowed_file(custom_thumb.filename, ALLOWED_IMAGE_EXTENSIONS):
                    thumb_ext = custom_thumb.filename.rsplit('.', 1)[1].lower()
                    thumbnail_filename = f"thumb_{uuid.uuid4().hex}.{thumb_ext}"
                    thumb_path = os.path.join(current_app.config['UPLOAD_FOLDER_THUMBNAILS'], thumbnail_filename)
                    custom_thumb.save(thumb_path)
                else:
                    flash('Invalid thumbnail image format. Auto-generating instead.', 'warning')
            
            # Auto-generate thumbnail if no custom thumbnail was uploaded
            if not thumbnail_filename:
                thumbnail_filename = extract_thumbnail_from_video(video_path, current_app.config['UPLOAD_FOLDER_THUMBNAILS'])
                
            # Create video record in DB
            new_video = Video(
                title=title,
                description=description,
                filename=unique_video_name,
                thumbnail_filename=thumbnail_filename,
                user_id=current_user.id
            )
            
            db.session.add(new_video)
            db.session.commit()
            
            flash('Video uploaded successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid video format. Supported: MP4, WebM, OGG, MOV, MKV.', 'danger')
            return redirect(url_for('video.upload'))
            
    return render_template('upload.html')

@video_bp.route('/watch/<int:video_id>')
def watch(video_id):
    video = Video.query.get_or_404(video_id) if hasattr(Video.query, 'get_or_404') else Video.query.get(video_id)
    if not video:
        flash('Video not found.', 'danger')
        return redirect(url_for('main.home'))
        
    # Increment views
    video.views += 1
    db.session.commit()
    
    # Recommended videos: other videos, limit to 6
    recommended_videos = Video.query.filter(Video.id != video.id).order_by(Video.upload_date.desc()).limit(6).all()
    
    return render_template('watch.html', video=video, recommended_videos=recommended_videos)

@video_bp.route('/stream/<filename>')
def stream(filename):
    """
    Streams the video file. Flask's send_from_directory supports HTTP Range requests natively,
    enabling fast seeking/scrubbing in HTML5 video players.
    """
    return send_from_directory(current_app.config['UPLOAD_FOLDER_VIDEOS'], filename)

@video_bp.route('/thumbnail/<filename>')
def serve_thumbnail(filename):
    """
    Serves the thumbnail file.
    """
    return send_from_directory(current_app.config['UPLOAD_FOLDER_THUMBNAILS'], filename)

@video_bp.route('/video/<int:video_id>/edit', methods=['POST'])
@login_required
def edit(video_id):
    video = Video.query.get(video_id)
    if not video:
        flash('Video not found.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    if video.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Video title cannot be empty.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    video.title = title
    video.description = description
    db.session.commit()
    
    flash('Video details updated successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@video_bp.route('/video/<int:video_id>/delete', methods=['POST'])
@login_required
def delete(video_id):
    video = Video.query.get(video_id)
    if not video:
        flash('Video not found.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    if video.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    # Remove physical files
    video_path = os.path.join(current_app.config['UPLOAD_FOLDER_VIDEOS'], video.filename)
    if os.path.exists(video_path):
        try:
            os.remove(video_path)
        except Exception as e:
            print(f"Error removing video file: {e}")
            
    if video.thumbnail_filename:
        thumb_path = os.path.join(current_app.config['UPLOAD_FOLDER_THUMBNAILS'], video.thumbnail_filename)
        if os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except Exception as e:
                print(f"Error removing thumbnail file: {e}")
                
    db.session.delete(video)
    db.session.commit()
    
    flash('Video deleted successfully.', 'success')
    return redirect(url_for('main.dashboard'))
