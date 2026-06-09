import streamlit as st
import json
import os
import base64
from PIL import Image
import io

# -- 1. PAGE CONFIG & BRUTE FORCE UI HIDING --
st.set_page_config(page_title="Family Tour Predictions", page_icon="⚾", layout="centered")

# Surgical strike to hide Fork, Deploy, Star, and the "Developer" Crown/User icons
# while preserving the left-side hamburger menu.
hide_streamlit_style = """
<style>
    /* Hide the right-side icons in the toolbar */
    [data-testid="stHeaderActions"] {
        display: none !important;
    }
    
    /* Make the header background transparent */
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Hide the 'Made with Streamlit' footer */
    footer {
        display: none !important;
    }

    /* Hide the Viewer Badges (Crown and User) entirely, using !important to override */
    .viewerBadge_container {display: none !important;}
    .viewerBadge_link {display: none !important;}
    #viewerBadge_container_pb {display: none !important;}

    /* Styling for the clickable profile images on landing */
    .profile-img-container {
        cursor: pointer;
        transition: transform 0.2s;
        text-align: center;
    }
    .profile-img-container:hover {
        transform: scale(1.05);
    }
    .profile-img {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 5px solid #0056b3;
    }
    /* Styling for the default placeholder initials */
    .initials-avatar {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background-color: #0056b3;
        color: white;
        font-size: 80px;
        font-weight: bold;
        line-height: 150px;
        text-align: center;
        display: inline-block;
        border: 5px solid #fff;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

DB_FILE = "tour_predictions_v2.json"
ADMIN_PASSWORD = "frankensox"

# MLB & Team Data
TEAMS = {
    "PIT": {"name": "Pirates", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/pit.png"},
    "LAD": {"name": "Dodgers", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/lad.png"},
    "WSH": {"name": "Nationals", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/wsh.png"},
    "SEA": {"name": "Mariners", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/sea.png"},
    "BAL": {"name": "Orioles", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/bal.png"},
    "SD":  {"name": "Padres", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/sd.png"},
    "PHI": {"name": "Phillies", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/phi.png"},
    "MIA": {"name": "Marlins", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/mia.png"},
    "NYY": {"name": "Yankees", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/nyy.png"},
    "CWS": {"name": "White Sox", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/cws.png"},
    "BOS": {"name": "Red Sox", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/bos.png"},
    "TOR": {"name": "Blue Jays", "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/scoreboard/tor.png"}
}
MLB_LOGO = "https://upload.wikimedia.org/wikipedia/commons/a/a6/Major_League_Baseball_logo.svg"

# -- 2. HELPER FUNCTIONS FOR IMAGES & STATE --

def initialize_db():
    if not os.path.exists(DB_FILE):
        default_data = {
            "players": {
                "Kenneth": {"avatar_b64": None},
                "Stephanie": {"avatar_b64": None},
                "Bishop": {"avatar_b64": None},
                "Violet": {"avatar_b64": None}
            },
            "games": [
                {"id": 0, "title": "Day 2: PNC Park", "away": "LAD", "home": "PIT", "predictions": {}, "results": {}},
                {"id": 1, "title": "Day 4: Nationals Park", "away": "SEA", "home": "WSH", "predictions": {}, "results": {}},
                {"id": 2, "title": "Day 5: Camden Yards", "away": "SD", "home": "BAL", "predictions": {}, "results": {}},
                {"id": 3, "title": "Day 7: Citizens Bank Park", "away": "MIA", "home": "PHI", "predictions": {}, "results": {}},
                {"id": 4, "title": "Day 8: Yankee Stadium", "away": "CWS", "home": "NYY", "predictions": {}, "results": {}},
                {"id": 5, "title": "Day 9: Fenway Park", "away": "TOR", "home": "BOS", "predictions": {}, "results": {}}
            ]
        }
        save_db(default_data)
        return default_data
    else:
        with open(DB_FILE, "r") as f:
            return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def process_uploaded_image(uploaded_file):
    # Resize and compress to keep the JSON file size reasonable
    img = Image.open(uploaded_file)
    # Convert to RGB just in case it's a PNG with alpha channel (can mess with jpeg saving)
    if img.mode in ('RGBA', 'LA'):
        background = Image.new(img.mode[:-1], img.size, '#fff')
        background.paste(img, img.split()[-1])
        img = background
    img = img.resize((300, 300))  
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=80)
    return base64.b64encode(buffered.getvalue()).decode()

def get_next_game_idx(db):
    # Find the first game that hasn't been graded yet
    for idx, game in enumerate(db["games"]):
        if not game.get("results"):
            return idx
    return 0 # Default to first game if all are graded

def get_questions(away_abbr, home_abbr):
    # Dynamic questions derived from earlier context
    away = TEAMS[away_abbr]["name"]
    home = TEAMS[home_abbr]["name"]
    return [
        {"id": "q1", "text": "Who will win the game?", "options": [away, home]},
        {"id": "q2", "text": "Which team will score the first run?", "options": [away, home, "Shutout"]},
        {"id": "q3", "text": "How many total runs will be scored?", "options": ["0-5", "6-9", "10-13", "14+"]},
        {"id": "q4", "text": "How many total home runs will be hit?", "options": ["0", "1-2", "3-4", "5+"]},
        {"id": "q5", "text": "Which team will record more hits?", "options": [away, home, "Tie"]},
        {"id": "q6", "text": "Will there be a stolen base?", "options": ["Yes", "No"]},
        {"id": "q7", "text": "Will either team commit a fielding error?", "options": ["Yes", "No"]},
        {"id": "q8", "text": "Will there be a replay review challenge?", "options": ["Yes", "No"]},
        {"id": "q9", "text": f"Will the {home} starting pitcher last 6 full innings?", "options": ["Yes", "No"]},
        {"id": "q10", "text": "How long will the game last?", "options": ["Under 2.5 Hours", "Over 2.5 Hours"]}
    ]

# -- 3. INITIALIZE STATE --

db = initialize_db()

# Track which player was clicked and if we are on the landing or predict page
if "current_player" not in st.session_state:
    st.session_state.current_player = None
if "stage" not in st.session_state:
    st.session_state.stage = "landing" # stage can be 'landing' or 'predicting'

# Sidebar - now just used for Admin mode
st.sidebar.image(MLB_LOGO, width=100)
st.sidebar.title("Navigation")
admin_mode = st.sidebar.checkbox("⚙️ Admin (Grade Games)")

# Function to handle profile clicks via query parameters
def handle_nav():
    # If ?player=Name is in the URL, that image was clicked
    clicked_player = st.query_params.get("player")
    if clicked_player and clicked_player in db["players"]:
        st.session_state.current_player = clicked_player
        st.session_state.stage = "predicting"
        # Clear params so refreshing the page doesn't keep resubmitting the selection
        st.query_params.clear()

handle_nav()

# -- 4. MAIN APP LOGIC --

# --- ADMIN PAGE (MODIFIED) ---
if admin_mode:
    st.title("Post-Game Grading")
    pwd = st.text_input("Admin Password", type="password")
    
    if pwd == ADMIN_PASSWORD:
        game_titles = [g["title"] for g in db["games"]]
        selected_game_title = st.selectbox("Select Game to Grade", game_titles)
        game = next(g for g in db["games"] if g["title"] == selected_game_title)
        
        questions = get_questions(game["away"], game["home"])
        existing_results = game.get("results", {})
        
        st.write("Enter the actual outcomes of the game below:")
        
        with st.form(key=f"grade_form_{game['id']}"):
            actual_results = {}
            for q in questions:
                # Set index to their previous choice if it exists
                default_idx = q["options"].index(existing_results[q["id"]]) if q["id"] in existing_results else 0
                actual_results[q["id"]] = st.radio(f"Actual: {q['text']}", q["options"], index=default_idx)
                
            if st.form_submit_button("Lock In Results"):
                game["results"] = actual_results
                save_db(db)
                st.success("Results saved! The leaderboard has been updated.")
    elif pwd:
        st.error("Incorrect password")

# --- PREDICTING PAGE ---
elif st.session_state.stage == "predicting":
    if st.button("⬅️ Back to Landing Page"):
        st.session_state.stage = "landing"
        st.session_state.current_player = None
        st.rerun()

    player_name = st.session_state.current_player
    st.title(f"Lock In Your Picks, {player_name}!")
    
    # Automatically determine the next relevant game
    next_game_idx = get_next_game_idx(db)
    game_titles = [g["title"] for g in db["games"]]
    selected_game_title = st.selectbox("Select Game", game_titles, index=next_game_idx)
    
    # Find active game
    game = next(g for g in db["games"] if g["title"] == selected_game_title)
    
    # Display Matchup
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.image(TEAMS[game["away"]]["logo"], width=80)
        st.caption(TEAMS[game['away']]['name'])
    with col2:
        st.write("### VS")
    with col3:
        st.image(TEAMS[game["home"]]["logo"], width=80)
        st.caption(TEAMS[game['home']]['name'])
    st.write("---")
    
    if game.get("results"):
        st.warning("This game has already been graded! No more predictions allowed.")
    else:
        questions = get_questions(game["away"], game["home"])
        
        # Load existing predictions if they want to edit before the game
        existing_preds = game["predictions"].get(player_name, {})
        
        with st.form(key=f"predict_form_{game['id']}"):
            user_picks = {}
            for q in questions:
                # Set index to their previous choice if it exists
                default_idx = q["options"].index(existing_preds[q["id"]]) if q["id"] in existing_preds else 0
                user_picks[q["id"]] = st.radio(q["text"], q["options"], index=default_idx)
                
            submit = st.form_submit_button("Save Predictions")
            if submit:
                game["predictions"][player_name] = user_picks
                save_db(db)
                st.success(f"Predictions saved for {player_name}!")

# --- LANDING PAGE (DEFAULT) ---
else:
    st.image(MLB_LOGO, width=80)
    st.title("Family Stadium Tour")
    st.write("Welcome to the prediction challenge! Click your picture to predict the next game.")
    st.write("---")

    # Display 4 columns for players
    cols = st.columns(4)
    
    # Sort names alphabetically just for consistent ordering
    player_names = ["Kenneth", "Stephanie", "Bishop", "Violet"]
    
    for idx, player_name in enumerate(player_names):
        p_data = db["players"][player_name]
        with cols[idx]:
            # Generate the image HTML
            if p_data["avatar_b64"]:
                # Use uploaded base64 image
                img_html = f'<img src="data:image/jpeg;base64,{p_data["avatar_b64"]}" class="profile-img"/>'
            else:
                # Use dynamic initial placeholder if no image uploaded
                initial = player_name[0]
                img_html = f'<div class="initials-avatar">{initial}</div>'

            # Wrap the image in a clickable container that sets the query param
            st.markdown(f"""
                <div class="profile-img-container">
                    <a href="?player={player_name}">
                        {img_html}
                    </a>
                    <h3>{player_name}</h3>
                </div>
            """, unsafe_allow_html=True)
            
    st.write("---")
    # Expander to allow adding images
    with st.expander("👤 Edit Profiles (Upload Images)"):
        selected_p = st.selectbox("Who are you updating?", player_names)
        uploaded_file = st.file_uploader(f"Choose image for {selected_p}", type=['jpg','png','jpeg'])
        
        if uploaded_file:
            st.image(uploaded_file, caption="Preview", width=100)
            if st.button("Update Profile Picture"):
                # Process, compress, and save b64 to JSON
                b64_string = process_uploaded_image(uploaded_file)
                db["players"][selected_p]["avatar_b64"] = b64_string
                save_db(db)
                st.success("Profile updated! Refreshing page...")
                st.rerun()

    st.write("---")
    # Mini Leaderboard on landing page
    st.write("### Current Leaderboard")
    scores = {player: 0 for player in db["players"]}
    for game in db["games"]:
        results = game.get("results", {})
        if results:
            for player, preds in game.get("predictions", {}).items():
                if player in scores: # Ensure only active 4 are counted
                    for q_id, answer in preds.items():
                        if results.get(q_id) == answer:
                            scores[player] += 1
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for rank, (player, score) in enumerate(sorted_scores, 1):
        st.write(f"**{rank}. {player}**: {score} pts")
