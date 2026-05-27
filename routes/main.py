from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db, Video, User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    query = request.args.get('q', '').strip()
    if query:
        # Search by title or description (case-insensitive)
        videos = Video.query.filter(
            (Video.title.ilike(f'%{query}%')) | 
            (Video.description.ilike(f'%{query}%'))
        ).order_by(Video.upload_date.desc()).all()
    else:
        videos = Video.query.order_by(Video.upload_date.desc()).all()
        
    return render_template('home.html', videos=videos, search_query=query)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch videos uploaded by current logged in user
    user_videos = Video.query.filter_by(user_id=current_user.id).order_by(Video.upload_date.desc()).all()
    
    # Calculate stats
    total_videos = len(user_videos)
    total_views = sum(video.views for video in user_videos)
    avg_views = round(total_views / total_videos, 1) if total_videos > 0 else 0.0
    
    stats = {
        'total_videos': total_videos,
        'total_views': total_views,
        'avg_views': avg_views
    }
    
    return render_template('dashboard.html', videos=user_videos, stats=stats)
