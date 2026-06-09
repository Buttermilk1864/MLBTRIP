import streamlit as st
import json
import os

st.set_page_config(page_title="Stadium Tour Predictions", page_icon="⚾", layout="centered")

DB_FILE = "tour_predictions.json"
ADMIN_PASSWORD = "frankensox"

# Team data for logos and names
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

# Default state initialization
def initialize_db():
    if not os.path.exists(DB_FILE):
        default_data = {
            "players": ["Kenneth", "Stephanie", "Bishop", "Violet"],
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

# Generate the 10 questions dynamically for a specific game
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

db = initialize_db()

# --- Sidebar Navigation ---
st.sidebar.image(MLB_LOGO, width=100)
st.sidebar.title("Navigation")
mode = st.sidebar.radio("Go to:", ["🏆 Leaderboard", "📝 Make Predictions", "⚙️ Admin (Grade Games)"])

# --- Leaderboard Page ---
if mode == "🏆 Leaderboard":
    st.title("Tour Leaderboard")
    st.write("1 point awarded for every correct prediction.")
    
    scores = {player: 0 for player in db["players"]}
    
    for game in db["games"]:
        results = game.get("results", {})
        if results:  # Game has been graded
            for player, preds in game.get("predictions", {}).items():
                for q_id, answer in preds.items():
                    if results.get(q_id) == answer:
                        scores[player] += 1
                        
    # Sort and display
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        for rank, (player, score) in enumerate(sorted_scores, 1):
            if rank == 1:
                st.subheader(f"🥇 {player}: {score} pts")
            elif rank == 2:
                st.write(f"🥈 {player}: {score} pts")
            elif rank == 3:
                st.write(f"🥉 {player}: {score} pts")
            else:
                st.write(f"{rank}. {player}: {score} pts")

# --- Make Predictions Page ---
elif mode == "📝 Make Predictions":
    st.title("Lock In Your Picks")
    
    player_name = st.selectbox("Who is picking?", db["players"])
    game_titles = [g["title"] for g in db["games"]]
    selected_game_title = st.selectbox("Select Game", game_titles)
    
    # Find active game
    game = next(g for g in db["games"] if g["title"] == selected_game_title)
    
    # Display Logos
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.image(TEAMS[game["away"]]["logo"], width=100)
        st.caption(f"Away: {TEAMS[game['away']]['name']}")
    with col2:
        st.write("### VS")
    with col3:
        st.image(TEAMS[game["home"]]["logo"], width=100)
        st.caption(f"Home: {TEAMS[game['home']]['name']}")
        
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

# --- Admin Page ---
elif mode == "⚙️ Admin (Grade Games)":
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