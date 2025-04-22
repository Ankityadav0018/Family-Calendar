import streamlit as st
import datetime
from collections import defaultdict

# --- Login Page ---
def login():
    st.markdown("""
        <style>
            body {
                background: url('https://www.w3schools.com/w3images/forest.jpg') no-repeat center center fixed;
                background-size: cover;
                color: white;
                font-family: 'Arial', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .login-form {
                background-color: rgba(0, 0, 0, 0.5);
                padding: 20px;
                border-radius: 10px;
                width: 400px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            }

            .login-form input {
                width: 80%;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                border: none;
                font-size: 16px;
            }

            .login-form button {
                background-color: #4CAF50;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                border: none;
                font-size: 18px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }

            .login-form button:hover {
                background-color: #45a049;
            }

            .login-form h2 {
                margin-bottom: 20px;
                font-size: 28px;
            }

            .login-form p {
                font-size: 14px;
                color: #ddd;
            }

            .login-form a {
                color: #4CAF50;
                text-decoration: none;
            }

            .login-form a:hover {
                text-decoration: underline;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-form'>", unsafe_allow_html=True)
    st.markdown("<h2>🔐 Family Calendar Login</h2>", unsafe_allow_html=True)

    username = st.text_input("Username", key="username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", key="password", placeholder="Enter your password")

    if st.button("Login"):
        # You can replace this with a proper auth system
        if username == "admin" and password == "password":
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()  # Prevents the rest of the app from loading


# --- Backend Class ---
class FamilyCalendar:
    def __init__(self):
        self.events = defaultdict(list)
        self.family_members = {}  # Store members as dict with name and birthday

    def add_family_member(self, name, birthday=None):
        self.family_members[name] = birthday

    def delete_family_member(self, name):
        if name in self.family_members:
            del self.family_members[name]
            return True
        return False

    def add_event(self, title, date, participants, description=""):
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        invalid_members = [p for p in participants if p not in self.family_members]
        if invalid_members:
            return False, f"Invalid participants: {', '.join(invalid_members)}"

        event = {
            "title": title,
            "date": date,
            "participants": participants,
            "description": description
        }

        self.events[date].append(event)
        return True, f"Event '{title}' added for {date}!"

    def get_events(self, date=None):
        if date:
            return self.events.get(date, [])
        today = datetime.date.today()
        upcoming = []
        for d in sorted(self.events.keys()):
            if d >= today:
                upcoming.extend(self.events[d])
        return upcoming

    def get_family_members(self):
        return sorted(self.family_members.keys())

    def get_upcoming_events(self, days=7):
        today = datetime.date.today()
        end = today + datetime.timedelta(days=days)
        upcoming = []
        for d in sorted(self.events.keys()):
            if today <= d <= end:
                upcoming.extend(self.events[d])
        return upcoming

    def get_birthday_dates(self):
        today = datetime.date.today()
        upcoming_bdays = []
        for name, bday in self.family_members.items():
            if bday:
                bday_this_year = bday.replace(year=today.year)
                # If birthday already passed, show next year's birthday
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                upcoming_bdays.append((name, bday_this_year))
        return sorted(upcoming_bdays, key=lambda x: x[1])

# --- App UI ---
today = datetime.date.today()
st.set_page_config(page_title="Family Calendar", layout="centered")
st.title(f"📅 {today.strftime('%d %B')} – Family Calendar")

# Display current date
st.markdown(f"**📅 Today's Date:** {today.strftime('%A, %B %d, %Y')}")

# Dark Mode Toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

st.sidebar.markdown("---")
if st.sidebar.checkbox("🌙 Dark Mode"):
    st.session_state.dark_mode = True
else:
    st.session_state.dark_mode = False

if st.session_state.dark_mode:
    st.markdown("""<style>body { background-color: #1e1e1e; color: #f0f0f0; }</style>""", unsafe_allow_html=True)

if "calendar" not in st.session_state:
    st.session_state.calendar = FamilyCalendar()

calendar = st.session_state.calendar

# --- Sidebar: Add Family Member ---
with st.sidebar:
    st.header("👨‍👩‍👧‍👦 Add Family Member")
    new_member = st.text_input("Name")
    birthday = st.date_input("Birthday ", min_value=datetime.date(1900, 1, 1))
    if st.button("Add Member") and new_member:
        calendar.add_family_member(new_member.strip(), birthday)
        st.success(f"{new_member} added!")

    # --- Delete Family Member ---
    st.header("❌ Delete Family Member")
    member_to_delete = st.selectbox("Select Member to Delete", calendar.get_family_members())
    if st.button("Delete Member"):
        if calendar.delete_family_member(member_to_delete):
            st.success(f"Member '{member_to_delete}' deleted!")
        else:
            st.error("Error: Member not found.")

# --- Tabs for Navigation ---
tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Event", "📆 View Events", "👥 View Members", "🎈 Birthdays"])

# --- Add Event ---
with tab1:
    st.subheader("Add New Event")
    title = st.text_input("Event Title")
    date = st.date_input("Date", datetime.date.today())
    participants = st.multiselect("Participants", calendar.get_family_members())
    description = st.text_area("Description (optional)")

    if st.button("Add Event"):
        success, msg = calendar.add_event(title, date, participants, description)
        if success:
            st.success(msg)
        else:
            st.error(msg)

# --- View Events ---
with tab2:
    st.subheader("View Events")
    view_mode = st.radio("Show", ["All Upcoming", "Specific Date", "Next 7 Days"])
    if view_mode == "All Upcoming":
        events = calendar.get_events()
    elif view_mode == "Specific Date":
        specific_date = st.date_input("Pick a Date")
        events = calendar.get_events(specific_date)
    else:
        events = calendar.get_upcoming_events()

    if not events:
        st.info("No events found.")
    else:
        for e in sorted(events, key=lambda x: x["date"]):
            st.markdown(f"### {e['title']} ({e['date']})")
            st.markdown(f"**Participants**: {', '.join(e['participants'])}")
            if e["description"]:
                st.markdown(f"**Description**: {e['description']}")
            st.markdown("---")

# --- View Members ---
with tab3:
    st.subheader("Family Members")
    members = calendar.get_family_members()
    if members:
        st.markdown("**Registered Members:**")
        for m in members:
            st.write(f"- {m}")
    else:
        st.info("No family members registered yet.")

# --- Birthdays ---
with tab4:
    st.subheader("Upcoming Birthdays")
    birthdays = calendar.get_birthday_dates()
    if birthdays:
        for name, bday in birthdays:
            st.markdown(f"### {name} - Birthday: {bday.strftime('%B %d, %Y')}")
    else:
        st.info("No upcoming birthdays.")

