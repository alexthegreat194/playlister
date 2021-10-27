from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient()
db = client.Playlister
playlists = db.playlists

@app.route('/')
def playlists_index():
    """Show all playlists."""
    return render_template('playlists_index.html', playlists=playlists.find())

if __name__ == '__main__':
    app.run(debug=True)
