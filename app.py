import streamlit as st
import json
import os

# -- 1. PAGE CONFIG & UI HIDING --
st.set_page_config(page_title="Family Tour Predictions", page_icon="⚾", layout="centered")

hide_streamlit_style = """
<style>
    /* Hide Streamlit UI elements */
    [data-testid="stHeaderActions"] { display: none !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    footer { display: none !important; }
    .viewerBadge_container {display: none !important;}
    .viewerBadge_link {display: none !important;}
    #viewerBadge_container_pb {display: none !important;}

    /* NEW FLEXBOX GRID FOR MOBILE */
    .avatar-grid {
        display: flex;
        flex-direction: row;
        justify-content: space-around;
        align-items: center;
        flex-wrap: wrap; /* Allows wrapping on extremely tiny screens */
        margin-bottom: 20px;
    }
    .profile-img-container {
        cursor: pointer;
        transition: transform 0.2s;
        text-align: center;
        width: 80px; /* Tighter container */
    }
    .profile-img-container:hover {
        transform: scale(1.05);
    }
    .profile-img {
        width: 75px; /* Shrunk for mobile */
        height: 75px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #0056b3;
        background-color: white;
    }
    .initials-avatar {
        width: 75px; 
        height: 75px;
        border-radius: 50%;
        background-color: #0056b3;
        color: white;
        font-size: 35px; /* Smaller font to fit */
        font-weight: bold;
        line-height: 70px;
        text-align: center;
        display: inline-block;
        border: 3px solid #fff;
    }
    .profile-name {
        margin-top: 5px;
        font-size: 14px;
        font-weight: 600;
        color: inherit;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

DB_FILE = "tour_predictions_v3.json"
ADMIN_PASSWORD = "frankensox"

# -- 2. CARTOON ROSTER (25 Characters) --
CARTOONS = {
    "Mickey Mouse": "https://upload.wikimedia.org/wikipedia/en/d/d4/Mickey_Mouse.png",
    "Minnie Mouse": "https://upload.wikimedia.org/wikipedia/en/6/67/Minnie_Mouse.png",
    "Bugs Bunny": "https://upload.wikimedia.org/wikipedia/en/1/17/Bugs_Bunny.svg",
    "Daffy Duck": "https://upload.wikimedia.org/wikipedia/en/f/f4/Daffy_Duck.svg",
    "Betty Boop": "https://upload.wikimedia.org/wikipedia/en/7/7b/Betty_Boop.png",
    "Popeye": "https://upload.wikimedia.org/wikipedia/en/0/00/Popeye_the_Sailor.png",
    "Olive Oyl": "https://upload.wikimedia.org/wikipedia/en/7/7d/Olive_Oyl.png",
    "Homer Simpson": "https://upload.wikimedia.org/wikipedia/en/0/02/Homer_Simpson_2006.png",
    "Marge Simpson": "https://upload.wikimedia.org/wikipedia/en/0/0b/Marge_Simpson.png",
    "SpongeBob": "https://upload.wikimedia.org/wikipedia/en/3/3b/SpongeBob_SquarePants_character.svg",
    "Sandy Cheeks": "https://upload.wikimedia.org/wikipedia/en/a/a0/Sandy_Cheeks.svg",
    "Scooby-Doo": "https://upload.wikimedia.org/wikipedia/en/5/53/Scooby-Doo.png",
    "Velma Dinkley": "https://upload.wikimedia.org/wikipedia/en/9/9d/Velma_Dinkley.png",
    "Fred Flintstone": "https://upload.wikimedia.org/wikipedia/en/a/ad/Fred_Flintstone.png",
    "Wilma Flintstone": "https://upload.wikimedia.org/wikipedia/en/4/43/Wilma_Flintstone.png",
    "Tom (Cat)": "https://upload.wikimedia.org/wikipedia/en/f/f6/Tom_Tom_and_Jerry.png",
    "Jerry (Mouse)": "https://upload.wikimedia.org/wikipedia/en/2/2f/Jerry_Mouse.png",
    "Snoopy": "https://upload.wikimedia.org/wikipedia/en/5/53/Snoopy_Peanuts.png",
    "Lucy van Pelt": "https://upload.wikimedia.org/wikipedia/en/e/e9/Lucy_van_Pelt.png",
    "Charlie Brown": "https://upload.wikimedia.org/wikipedia/en/2/22/Charlie_Brown.png",
    "Dexter": "https://upload.wikimedia.org/wikipedia/en/1/1a/Dexter_from_Dexter%27s_Laboratory.png",
    "Dee Dee": "https://upload.wikimedia.org/wikipedia/en/0/03/Dee_Dee_from_Dexter%27s_Laboratory.png",
    "Garfield": "https://upload.wikimedia.org/wikipedia/en/b/bc/Garfield_the_Cat.svg",
    "Lisa Simpson": "https://upload.wikimedia.org/wikipedia/en/e/ec/Lisa_Simpson.png",
    "Pink Panther": "https://upload.wikimedia.org/wikipedia/en/9/91/Pink_Panther.png"
}

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

# -- 3. HELPER FUNCTIONS FOR DB & STATE --
def initialize_db():
    if not os.path.exists(DB_FILE):
        default_data = {
            "players": {
                "Kenneth": {"avatar_url": None},
                "Stephanie": {"avatar_url": None},
                "Bishop": {"avatar_url": None},
                "Violet": {"avatar_url": None}
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

def get_next_game_idx(db):
    for idx, game in enumerate(db["games"]):
        if not game.get("results"):
            return idx
    return 0 

def get_questions(away_abbr, home_abbr):
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

# -- 4. INITIALIZE STATE --
db = initialize_db()

if "current_player" not in st.session_state:
    st.session_state.current_player = None
if "stage" not in st.session_state:
    st.session_state.stage = "landing" 

st.sidebar.image(MLB_LOGO, width=100)
st.sidebar.title("Navigation")
admin_mode = st.sidebar.checkbox("⚙️ Admin (Grade Games)")

def handle_nav():
    clicked_player = st.query_params.get("player")
    if clicked_player and clicked_player in db["players"]:
        st.session_state.current_player = clicked_player
        st.session_state.stage = "predicting"
        st.query_params.clear()

handle_nav()

# -- 5. MAIN APP LOGIC --

# --- ADMIN PAGE ---
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
    
    next_game_idx = get_next_game_idx(db)
    game_titles = [g["title"] for g in db["games"]]
    selected_game_title = st.selectbox("Select Game", game_titles, index=next_game_idx)
    game = next(g for g in db["games"] if g["title"] == selected_game_title)
    
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
        existing_preds = game["predictions"].get(player_name, {})
        
        with st.form(key=f"predict_form_{game['id']}"):
            user_picks = {}
            for q in questions:
                default_idx = q["options"].index(existing_preds[q["id"]]) if q["id"] in existing_preds else 0
                user_picks[q["id"]] = st.radio(q["text"], q["options"], index=default_idx)
                
            if st.form_submit_button("Save Predictions"):
                game["predictions"][player_name] = user_picks
                save_db(db)
                st.success(f"Predictions saved for {player_name}!")

# --- LANDING PAGE ---
else:
    st.image(MLB_LOGO, width=60)
    st.title("Family Stadium Tour")
    st.write("Welcome to the prediction challenge! Click your picture to predict the next game.")
    st.write("---")

    player_names = ["Kenneth", "Stephanie", "Bishop", "Violet"]
    
    # Build the HTML flexbox grid string for mobile alignment
    grid_html = '<div class="avatar-grid">'
    
    for player_name in player_names:
        p_data = db["players"][player_name]
        
        if p_data.get("avatar_url"):
            img_html = f'<img src="{p_data["avatar_url"]}" class="profile-img"/>'
        else:
            initial = player_name[0]
            img_html = f'<div class="initials-avatar">{initial}</div>'

        grid_html += f"""
            <div class="profile-img-container">
                <a href="?player={player_name}" style="text-decoration: none; color: inherit;">
                    {img_html}
                    <div class="profile-name">{player_name}</div>
                </a>
            </div>
        """
        
    grid_html += '</div>'
    
    # Render the entire grid at once
    st.markdown(grid_html, unsafe_allow_html=True)
            
    st.write("---")
    
    # Avatar Selector
    with st.expander("👤 Choose Your Avatar"):
        selected_p = st.selectbox("Who are you updating?", player_names)
        
        character_names = list(CARTOONS.keys())
        selected_character = st.selectbox("Select a Character", character_names)
        
        st.image(CARTOONS[selected_character], width=100, caption=f"Preview: {selected_character}")
        
        if st.button("Save Avatar"):
            db["players"][selected_p]["avatar_url"] = CARTOONS[selected_character]
            save_db(db)
            st.success(f"Avatar updated for {selected_p}! Refreshing...")
            st.rerun()

    st.write("---")
    
    # Mini Leaderboard
    st.write("### Current Leaderboard")
    scores = {player: 0 for player in db["players"]}
    for game in db["games"]:
        results = game.get("results", {})
        if results:
            for player, preds in game.get("predictions", {}).items():
                if player in scores:
                    for q_id, answer in preds.items():
                        if results.get(q_id) == answer:
                            scores[player] += 1
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for rank, (player, score) in enumerate(sorted_scores, 1):
        st.write(f"**{rank}. {player}**: {score} pts")
