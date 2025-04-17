import streamlit as st
import datetime
from collections import defaultdict

# --- Backend Class ---
class FamilyCalendar:
    def __init__(self):
        self.events = defaultdict(list)
        self.family_members = set()

    def add_family_member(self, name):
        self.family_members.add(name)

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
        return sorted(self.family_members)

    def get_upcoming_events(self, days=7):
        today = datetime.date.today()
        end = today + datetime.timedelta(days=days)
        upcoming = []
        for d in sorted(self.events.keys()):
            if today <= d <= end:
                upcoming.extend(self.events[d])
        return upcoming

# --- App UI ---
st.set_page_config(page_title="Family Calendar", layout="centered")
st.title("📅 Family Calendar")

if "calendar" not in st.session_state:
    st.session_state.calendar = FamilyCalendar()

calendar = st.session_state.calendar

# --- Sidebar: Add Family Member ---
with st.sidebar:
    st.header("👨‍👩‍👧‍👦 Add Family Member")
    new_member = st.text_input("Name")
    if st.button("Add Member") and new_member:
        calendar.add_family_member(new_member.strip())
        st.success(f"{new_member} added!")

# --- Tabs for Navigation ---
tab1, tab2, tab3 = st.tabs(["➕ Add Event", "📆 View Events", "👥 View Members"])

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
        st.info("No members added yet.")

