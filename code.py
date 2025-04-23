

import streamlit as st
import datetime
from collections import defaultdict
import requests

# ========== PAGE CONFIG (MUST BE FIRST) ==========
st.set_page_config(page_title="Family Calendar Pro", layout="centered")

# ========== CONFIGURATION ==========
DEEPSEEK_API_KEY = "sk-001b301810274203bd0735cb86d8c06a"   # Replace with your actual key
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # Verify endpoint

# ========== PREMIUM FEATURES ==========
def show_premium_popup():
    with st.popover("🔒 Premium Feature"):
        st.markdown("### 🚀 Upgrade to Premium!")
        st.write("Unlock all features including:")
        st.write("- 📅 Advanced calendar analytics")
        st.write("- 👪 Extended family management")
        st.write("- 💬 Unlimited AI chat")
        if st.button("Upgrade Now"):
            st.session_state.premium_user = True
            st.rerun()

# ========== CENTERED LOGIN PAGE ==========
def login():
    st.markdown("""
        <style>
            
            .login-title {
                color: white;
                margin-bottom: 30px;
                font-size: 36px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .stTextInput>div>div>input {
                color: white !important;
                background: rgba(255, 255, 255, 0.1) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 8px !important;
                padding: 10px 15px !important;
            }
            .login-button {
                width: 100%;
                padding: 12px;
                border-radius: 8px;
                background: linear-gradient(45deg, #6e48aa, #9d50bb);
                color: white;
                border: none;
                font-weight: bold;
                margin-top: 20px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .error-message {
                color: #ff4b4b;
                margin-top: 15px;
                font-size: 14px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Create centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
<style>
    .big-title {
        font-size: 35px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Then use it like this:
        st.markdown("<div class='big-title'> 🔐 FAMILY CALENDAR</div>", unsafe_allow_html=True)
        # Username field
        username = st.text_input("", placeholder="Username", key="username")
        
        # Password field
        password = st.text_input("", type="password", placeholder="Password", key="password")
        
        # Remember me checkbox
        st.checkbox("Remember me", key="remember_me")
        
        # Login button
        if st.button("Login", key="login_button"):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.premium_user = False
                st.session_state.chat_history = []  # Initialize chat history
                st.rerun()
            else:
                st.markdown("<div class='error-message'>Invalid username or password</div>", unsafe_allow_html=True)
        
        # Forgot password link
        st.markdown("[Forgot password?](#)", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ========== FAMILY CALENDAR CLASS ==========
class FamilyCalendar:
    def __init__(self):
        self.events = defaultdict(list)
        self.family_members = {}

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
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                upcoming_bdays.append((name, bday_this_year))
        return sorted(upcoming_bdays, key=lambda x: x[1])

# ========== BASIC CHATBOT FALLBACK ==========
class BasicChatbot:
    def get_response(self, prompt, calendar_data):
        prompt = prompt.lower()
        
        if any(word in prompt for word in ["hello", "hi", "hey"]):
            return "Hello! I'm your family calendar assistant."
        
        elif any(word in prompt for word in ["event", "meeting", "appointment"]):
            events = calendar_data.get_upcoming_events(7)
            if not events:
                return "No upcoming events in the next week."
            return "Upcoming events:\n" + "\n".join([f"- {e['title']} on {e['date']}" for e in events])
        
        elif any(word in prompt for word in ["birthday", "bday"]):
            birthdays = calendar_data.get_birthday_dates()
            if not birthdays:
                return "No upcoming birthdays."
            return "Upcoming birthdays:\n" + "\n".join([f"- {name}'s birthday on {date.strftime('%B %d')}" for name, date in birthdays])
        
        elif any(word in prompt for word in ["member", "family"]):
            members = calendar_data.get_family_members()
            if not members:
                return "No family members registered."
            return "Family members: " + ", ".join(members)
        
        return "I can help with events, birthdays, and family members. Try asking about those!"

# ========== DEEPSEEK CHATBOT ==========
class DeepSeekChatbot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.initialized = bool(api_key)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.basic_chatbot = BasicChatbot()  # Fallback

    def get_response(self, prompt, calendar_data):
        if not self.initialized:
            return self.basic_chatbot.get_response(prompt, calendar_data)
        
        try:
            context = self._build_context(calendar_data)
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": context},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            elif response.status_code == 402:  # Insufficient balance
                show_premium_popup()
                return self.basic_chatbot.get_response(prompt, calendar_data)
            else:
                return f"API Error: {response.status_code}. {self.basic_chatbot.get_response(prompt, calendar_data)}"
                
        except Exception as e:
            return f"{self.basic_chatbot.get_response(prompt, calendar_data)} [API Error: {str(e)}]"

    def _build_context(self, calendar_data):
        return f"""You're a family calendar assistant. Current context:
Family Members: {', '.join(calendar_data.get_family_members()) or 'None'}
Upcoming Events: {self._format_events(calendar_data.get_upcoming_events(7))}
Upcoming Birthdays: {self._format_birthdays(calendar_data.get_birthday_dates())}
Today: {datetime.date.today().strftime('%A, %B %d, %Y')}"""

    def _format_events(self, events):
        return "\n".join(f"- {e['title']} on {e['date']}" for e in events) if events else "None"

    def _format_birthdays(self, birthdays):
        return "\n".join(f"- {name}'s on {date.strftime('%B %d')}" for name, date in birthdays) if birthdays else "None"

# ========== MAIN APPLICATION ==========
def main_app():
    # Initialize session state variables
    if "calendar" not in st.session_state:
        st.session_state.calendar = FamilyCalendar()
    
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = DeepSeekChatbot(DEEPSEEK_API_KEY)
            if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_api_key_here":
                show_premium_popup()
        except Exception as e:
            st.error(f"Chatbot error: {str(e)}")
            st.session_state.chatbot = BasicChatbot()

    today = datetime.date.today()
    st.title(f"📅 Family Calendar {'Pro' if st.session_state.get('premium_user') else ''} - {today.strftime('%B %Y')}")
    st.markdown(f"**Today's Date:** {today.strftime('%A, %B %d, %Y')}")

    # Sidebar with premium indicator
    with st.sidebar:
        if st.session_state.get('premium_user'):
            st.success("🌟 Premium Member")
        else:
            st.warning("Free Account")
            if st.button("Upgrade to Premium"):
                show_premium_popup()

        st.header("👨‍👩‍👧‍👦 Family Members")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Add Member")
            new_member = st.text_input("Name", key="new_member")
            birthday = st.date_input("Birthday", key="new_birthday")
            if st.button("Add"):
                if new_member:
                    st.session_state.calendar.add_family_member(new_member.strip(), birthday)
                    st.success(f"Added {new_member}!")
        
        with col2:
            st.subheader("Delete Member")
            member_to_delete = st.selectbox(
                "Select member",
                st.session_state.calendar.get_family_members(),
                key="delete_member"
            )
            if st.button("Delete"):
                if st.session_state.calendar.delete_family_member(member_to_delete):
                    st.success(f"Deleted {member_to_delete}")

    # Main tabs - Add premium tab for premium users
    if st.session_state.get('premium_user'):
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "➕ Add Event", 
            "📆 View Events", 
            "👥 Family Members", 
            "🎈 Birthdays", 
            "💬 Chat Assistant"
        ])
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "➕ Add Event", 
            "📆 View Events", 
            "👥 Family Members", 
            "🎈 Birthdays", 
            "💬 Chat Assistant"
        ])

    # Tab 1: Add Event
    with tab1:
        st.subheader("Create New Event")
        with st.form("event_form"):
            title = st.text_input("Event Title")
            date = st.date_input("Date", today)
            participants = st.multiselect(
                "Participants",
                st.session_state.calendar.get_family_members()
            )
            description = st.text_area("Description")
            
            if st.form_submit_button("Add Event"):
                success, message = st.session_state.calendar.add_event(
                    title, date, participants, description
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

    # Tab 2: View Events
    with tab2:
        st.subheader("Upcoming Events")
        view_option = st.radio(
            "View options",
            ["All Upcoming", "Next 7 Days", "By Date"],
            horizontal=True
        )
        
        if view_option == "All Upcoming":
            events = st.session_state.calendar.get_events()
        elif view_option == "Next 7 Days":
            events = st.session_state.calendar.get_upcoming_events(7)
        else:
            selected_date = st.date_input("Select date", today)
            events = st.session_state.calendar.get_events(selected_date)
        
        if not events:
            st.info("No events found")
        else:
            for event in sorted(events, key=lambda x: x["date"]):
                with st.expander(f"{event['title']} - {event['date']}"):
                    st.markdown(f"**Participants:** {', '.join(event['participants'])}")
                    if event["description"]:
                        st.markdown(f"**Description:** {event['description']}")

    # Tab 3: Family Members
    with tab3:
        st.subheader("Family Members")
        members = st.session_state.calendar.get_family_members()
        if not members:
            st.info("No family members added yet")
        else:
            for member in members:
                st.markdown(f"- {member}")

    # Tab 4: Birthdays
    with tab4:
        st.subheader("Upcoming Birthdays")
        birthdays = st.session_state.calendar.get_birthday_dates()
        if not birthdays:
            st.info("No birthdays added yet")
        else:
            for name, date in birthdays:
                days_until = (date - today).days
                st.markdown(f"### {name}")
                st.markdown(f"**Date:** {date.strftime('%B %d')}")
                st.markdown(f"**Days until:** {days_until}")
                st.divider()

    # Tab 5: Chat Assistant
    with tab5:
        st.subheader("Calendar Assistant")
        st.caption("Ask me about events, birthdays, or family members")
        
        # Initialize chat history if not exists
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat messages from history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Text input
        if prompt := st.chat_input("Ask me about your family calendar..."):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.get_response(
                    prompt,
                    st.session_state.calendar
                )
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Rerun to update the display
            st.rerun()

# ========== RUN APPLICATION ==========
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
