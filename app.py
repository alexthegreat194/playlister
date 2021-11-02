from flask import Flask, render_template, request, redirect, url_for
import os
from pymongo import MongoClient
# Add this with the rest of your import statements
from bson.objectid import ObjectId

def video_url_creator(id_lst):
    videos = []
    for vid_id in id_lst:
        # We know that embedded YouTube videos always have this format
        video = 'https://youtube.com/embed/' + vid_id
        videos.append(video)
    return videos


app = Flask(__name__)

# host = os.environ.get('MONGODB_URI', 'mongodb+srv://cluster0.2lvxa.mongodb.net/Cluster0')
db_username = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASS')
# client = MongoClient(host=host)
client = MongoClient(f"mongodb+srv://{db_username}:{db_password}@cluster0.2lvxa.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = client.Playlister
playlists = db.playlists
comments = db.comments

@app.route('/')
def playlists_index():
    """Show all playlists."""
    return render_template('playlists_index.html', playlists=playlists.find())

@app.route('/playlists/new')
def playlists_new():
    """Create a new playlist."""
    playlist = {
        'title': "",
        'description': "",
        'videos': "",
        'video_ids': ""
    }
    return render_template('playlists_new.html', playlist=playlist)

# Note the methods parameter that explicitly tells the route that this is a POST
@app.route('/playlists', methods=['POST'])
def playlists_submit():
    """Submit a new playlist."""
    # Grab the video IDs and make a list out of them
    video_ids = request.form.get('video_ids').split()
    # call our helper function to create the list of links
    videos = video_url_creator(video_ids)
    playlist = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'videos': videos,
        'video_ids': video_ids
    }
    playlists.insert_one(playlist)
    return redirect(url_for('playlists_index'))

@app.route('/playlists/<playlist_id>', methods=['POST'])
def playlists_update(playlist_id):
    """Submit an edited playlist."""
    video_ids = request.form.get('video_ids').split()
    videos = video_url_creator(video_ids)
    # create our updated playlist
    updated_playlist = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'videos': videos,
        'video_ids': video_ids
    }
    # set the former playlist to the new one we just updated/edited
    playlists.update_one(
        {'_id': ObjectId(playlist_id)},
        {'$set': updated_playlist})
    # take us back to the playlist's show page
    return redirect(url_for('playlists_show', playlist_id=playlist_id))

@app.route('/playlists/<playlist_id>/edit')
def playlists_edit(playlist_id):
    """Show the edit form for a playlist."""
    playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
    # Add the title parameter here
    return render_template('playlists_edit.html', playlist=playlist, title='Edit Playlist')

@app.route('/playlists/<playlist_id>')  
def playlists_show(playlist_id):
    """Show a single playlist."""
    playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
    playlist_comments = comments.find({'playlist_id': playlist_id})
    return render_template('playlists_show.html', playlist=playlist, comments=playlist_comments)

@app.route('/playlists/<playlist_id>/delete', methods=['POST'])
def playlists_delete(playlist_id):
    """Delete one playlist."""
    playlists.delete_one({'_id': ObjectId(playlist_id)})
    return redirect(url_for('playlists_index'))

@app.route('/playlists/comments', methods=['POST'])
def comments_new():
    """Submit a new comment."""
    playlist_id = request.form.get("playlist_id")
    comment = {
        "title":request.form.get("title"),
        "content":request.form.get("content"),
        "playlist_id":playlist_id
    }
    comments.insert_one(comment)
    return redirect(url_for(f"playlists_show", playlist_id=playlist_id))

@app.route('/playlists/comments/<comment_id>/delete', methods=["POST"])
def comments_delete(comment_id):
    """Delete a comment"""
    comment = comments.find_one({'_id': ObjectId(comment_id)})
    playlist_id = comment['playlist_id']
    comments.delete_one(comment)
    return redirect(url_for('playlists_show', playlist_id=playlist_id))

if __name__ == '__main__':
    app.run(debug=True)
