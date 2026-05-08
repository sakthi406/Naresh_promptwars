import streamlit as st
import traceback
import logging
import time
from typing import Optional
from models.trip_model import TripRequest, ItineraryResponse
from services.planner_service import create_or_adapt_itinerary
from services.maps_service import get_google_maps_search_url
from utils.validators import validate_complete_form
from utils.sanitizers import sanitize_destination, sanitize_food_prefs
from utils.error_handler import handle_api_error, log_user_action, log_performance_metric, handle_streamlit_error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Tripify",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1a1a2e !important;
}
section[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #16213e !important;
    border: 1px solid #0f3460 !important;
    border-radius: 6px !important;
    color: #fff !important;
}
section[data-testid="stSidebar"] label {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #888 !important;
}

/* Button */
div.stFormSubmitButton > button, div.stButton > button {
    background: #e94560 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
    padding: 0.6rem !important;
}
div.stFormSubmitButton > button:hover, div.stButton > button:hover {
    background: #c73652 !important;
}

/* Activity card */
.act {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-left: 4px solid #e94560;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.act-time { font-size: 0.72rem; color: #999; font-weight: 600; text-transform: uppercase; }
.act-title { font-size: 1rem; font-weight: 700; color: #1a1a2e; margin: 3px 0; }
.act-title a { color: #1a1a2e; text-decoration: none; }
.act-title a:hover { color: #e94560; }
.act-desc { font-size: 0.85rem; color: #555; margin-bottom: 6px; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; }
.tag { font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 12px; }
.tc { background: #fff8e1; color: #856404; }
.ta { background: #e3f2fd; color: #0d47a1; }

/* Fallback */
.fb {
    background: #fff3f0;
    border-left: 3px solid #e94560;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 6px;
    font-size: 0.83rem;
    color: #555;
}
.fb strong { color: #e94560; }
.fb a { color: #c73652; font-weight: 600; text-decoration: none; }

/* Reason card */
.rc {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 14px 16px;
    height: 100%;
}
.rc h4 { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.07em; color: #999; margin: 0 0 6px; }
.rc p  { font-size: 0.87rem; color: #333; line-height: 1.6; margin: 0; }

.divider { border: none; border-top: 1px solid #eee; margin: 16px 0; }
</style>
""", unsafe_allow_html=True)

# Session state
for k, v in [("itinerary", None), ("current_request", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

@handle_streamlit_error
def generate_plan(request_data: dict, replanning_trigger: Optional[str] = None) -> None:
    """Generate or adapt travel itinerary with enhanced error handling and validation."""
    start_time = time.time()
    
    try:
        # Log user action
        action = f"Generate itinerary for {request_data.get('destination', 'Unknown')}"
        if replanning_trigger:
            action += f" (trigger: {replanning_trigger})"
        log_user_action(action)
        
        # Enhanced validation
        is_valid, errors = validate_complete_form(request_data)
        
        if not is_valid:
            for error in errors:
                st.error(f"⚠️ {error}")
            logger.warning(f"Validation failed: {errors}")
            return
            
        # Sanitize inputs
        sanitized_dest = sanitize_destination(request_data["destination"])
        sanitized_food = sanitize_food_prefs(request_data["food_prefs"])
        
        # Update request data with sanitized inputs
        sanitized_request = request_data.copy()
        sanitized_request["destination"] = sanitized_dest
        sanitized_request["food_prefs"] = sanitized_food
        
        prev = st.session_state.itinerary.model_dump() if st.session_state.itinerary else None
        req = TripRequest(
            destination=sanitized_dest,
            budget=sanitized_request["budget"],
            num_days=sanitized_request["num_days"],
            group_type=sanitized_request["group_type"],
            trip_style=sanitized_request["trip_style"],
            accessibility=sanitized_request["accessibility"],
            food_prefs=sanitized_food,
            crowd_tolerance=sanitized_request["crowd_tolerance"],
            weather_pref=sanitized_request["weather_pref"],
            previous_itinerary=prev,
            replanning_trigger=replanning_trigger,
        )
        st.session_state.current_request = sanitized_request
        
        with st.spinner("🧠 Building your itinerary…"):
            st.session_state.itinerary = create_or_adapt_itinerary(req)
            
            # Log performance
            elapsed_time = time.time() - start_time
            log_performance_metric("itinerary_generation", elapsed_time)
            
            logger.info(f"Successfully generated itinerary for {sanitized_dest} in {elapsed_time:.2f}s")
            st.success("✅ Itinerary generated successfully!")
            
    except ValueError as ve:
        error_msg = handle_api_error(ve)
        st.error(f"⚠️ {error_msg}")
        logger.warning(f"Validation error: {ve}")
    except KeyError as ke:
        st.error(f"⚠️ Missing required field: {str(ke)}")
        logger.error(f"Key error: {ke}")
    except Exception as e:
        error_msg = handle_api_error(e)
        st.error(f"⚠️ {error_msg}")
        with st.expander("Debug Info"):
            st.code(traceback.format_exc())
        logger.error(f"Unexpected error: {e}")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✈️ Tripify")
    st.markdown("<p style='color:#888;font-size:.82rem;margin-top:-.4rem'>AI Travel Planner</p>", unsafe_allow_html=True)
    st.markdown("---")
    with st.form("travel_form"):
        dest = st.text_input(
            "📍 Destination", 
            placeholder="Goa, Paris, Tokyo…",
            help="Enter your travel destination (letters, spaces, hyphens, apostrophes only)",
            max_chars=100
        )
        budget = st.selectbox(
            "💰 Budget", 
            ["Budget", "Moderate", "Luxury", "No Limit"],
            help="Select your budget range",
            index=1
        )
        days = st.number_input(
            "📅 Days", 
            min_value=1, 
            max_value=14, 
            value=3,
            help="Number of days for your trip (1-14)"
        )
        group = st.selectbox(
            "👥 Group", 
            ["Solo", "Couple", "Family with Kids", "Friends Group", "Seniors"],
            help="Who are you traveling with?",
            index=1
        )
        style = st.selectbox(
            "🎭 Style", 
            ["Relaxed", "Action-Packed", "Cultural Deep-Dive", "Nature Focus"],
            help="What type of trip do you prefer?",
            index=0
        )
        acc = st.selectbox(
            "♿ Accessibility", 
            ["None", "Low Walking", "Wheelchair Accessible", "Stroller Friendly"],
            help="Accessibility requirements",
            index=0
        )
        food = st.text_input(
            "🍽️ Food Prefs", 
            placeholder="Vegan, Halal…",
            help="Dietary preferences or restrictions (optional)",
            max_chars=200
        )
        crowd = st.selectbox(
            "🧍 Crowds", 
            ["High (Don't mind)", "Moderate", "Low (Avoid crowds)"],
            help="Crowd tolerance level",
            index=1
        )
        wthr = st.selectbox(
            "🌤️ Weather", 
            ["Any", "Prefer Indoor if Hot/Rainy", "Love Outdoors Regardless"],
            help="Weather preferences",
            index=0
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button(
            "✨ Generate Itinerary", 
            use_container_width=True,
            help="Generate your personalized travel itinerary"
        )
        
        if submitted:
            generate_plan({
                "destination": dest,
                "budget": budget,
                "num_days": days,
                "group_type": group,
                "trip_style": style,
                "accessibility": acc,
                "food_prefs": food,
                "crowd_tolerance": crowd,
                "weather_pref": wthr
            })

# ── MAIN ──────────────────────────────────────────────────────────────────────
st.title("✈️ Adaptive Travel Intelligence Engine")
st.caption("AI-powered itineraries that adapt to weather, budget shifts, and real-world changes.")
st.divider()

if not st.session_state.itinerary:
    c1,c2,c3 = st.columns(3)
    for col,icon,title,desc in [
        (c1,"🧠","Smart Planning","AI detects your persona and builds a tailored day-by-day plan."),
        (c2,"⚡","Dynamic Replanning","Rain? Budget cut? One tap adapts your whole schedule."),
        (c3,"🛡️","Proactive Fallbacks","Every day ships with backup options for anything."),
    ]:
        col.info(f"**{icon} {title}**\n\n{desc}")
    st.markdown("\n👈 Enter your preferences in the sidebar to get started.")
else:
    itin: ItineraryResponse = st.session_state.itinerary
    dest_label = st.session_state.current_request.get("destination","")

    st.success(f"**🧭 {itin.traveler_persona}** &nbsp;|&nbsp; 📍 {dest_label} &nbsp;|&nbsp; 💸 {itin.total_cost_estimate} &nbsp;|&nbsp; 📅 {len(itin.days)} days")

    tab1, tab2, tab3 = st.tabs(["🗺️ Itinerary", "🧠 AI Reasoning", "⚡ Replan"])

    with tab1:
        for day in itin.days:
            st.markdown(f"### Day {day.day_number} — {day.theme}")
            for act in day.activities:
                url = get_google_maps_search_url(f"{act.title} {dest_label}")
                st.markdown(f"""
                <div class="act" role="article" aria-labelledby="act-{day.day_number}-{act.time.replace(':', '-')}" tabindex="0">
                  <div class="act-time" id="act-{day.day_number}-{act.time.replace(':', '-')}">⏰ {act.time}</div>
                  <div class="act-title"><a href="{url}" target="_blank" rel="noopener noreferrer" aria-label="Search for {act.title} on Google Maps">{act.title} ↗</a></div>
                  <div class="act-desc">{act.description}</div>
                  <div class="tags">
                    <span class="tag tc" aria-label="Cost estimate: {act.cost_estimate}">💰 {act.cost_estimate}</span>
                    <span class="tag ta" aria-label="Accessibility: {act.accessibility_notes}">♿ {act.accessibility_notes}</span>
                  </div>
                </div>""", unsafe_allow_html=True)

            if day.fallback_plans:
                st.markdown("**🛡️ Fallbacks:**")
                for fb in day.fallback_plans:
                    fb_url = get_google_maps_search_url(f"{fb.alternative_activity.title} {dest_label}")
                    st.markdown(f"""<div class="fb" role="complementary" aria-labelledby="fallback-{day.day_number}-{fb.alternative_activity.title.replace(' ', '-')}" tabindex="0">
                      <strong id="fallback-{day.day_number}-{fb.alternative_activity.title.replace(' ', '-')}">If {fb.trigger_condition}:</strong>
                      <a href="{fb_url}" target="_blank" rel="noopener noreferrer" aria-label="Search for {fb.alternative_activity.title} on Google Maps">{fb.alternative_activity.title}</a>
                      — {fb.alternative_activity.description}
                    </div>""", unsafe_allow_html=True)
            st.markdown('<hr class="divider">', unsafe_allow_html=True)

    with tab2:
        de = itin.decision_engine
        c1,c2 = st.columns(2)
        c1.markdown(f'<div class="rc" role="complementary" aria-labelledby="recommendations" tabindex="0"><h4 id="recommendations">💡 Recommendations</h4><p>{de.recommendation_reasoning}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="rc" role="complementary" aria-labelledby="accessibility" tabindex="0"><h4 id="accessibility">♿ Accessibility</h4><p>{de.accessibility_reasoning}</p></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        c3,c4 = st.columns(2)
        c3.markdown(f'<div class="rc" role="complementary" aria-labelledby="crowds" tabindex="0"><h4 id="crowds">🧍 Crowds</h4><p>{de.crowd_optimization_logic}</p></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="rc" role="complementary" aria-labelledby="budget" tabindex="0"><h4 id="budget">💸 Budget</h4><p>{de.budget_balancing_logic}</p></div>', unsafe_allow_html=True)
        if de.adaptation_summary:
            st.info(f"🔄 **Adaptation:** {de.adaptation_summary}")

    with tab3:
        st.markdown("**Simulate a real-world change — AI adapts your plan instantly:**")
        c1,c2,c3 = st.columns(3)
        triggers = [("🌧️ Heavy Rain","Heavy Rain Started"),("🚶 Less Walking","Reduce Walking"),
                    ("📉 Budget Cut","Budget Reduced"),("👨‍👩‍👧 Family Mode","Add Family-Friendly Activities"),
                    ("🤫 Avoid Crowds","Avoid Crowded Areas"),("🌡️ Too Hot","Too Hot Outside")]
        for i,(label,val) in enumerate(triggers):
            if [c1,c2,c3][i%3].button(
                label, 
                use_container_width=True, 
                key=f"trigger_{i}",
                help=f"Simulate: {val}",
                type="secondary"
            ):
                log_user_action(f"Triggered replanning: {val}")
                generate_plan(st.session_state.current_request, replanning_trigger=val)
                st.rerun()