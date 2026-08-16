"""
Predefined replies for common greetings and FAQs.

Matching logic lives in chatbot.py. This file only stores the data.
"""

GREETING_REPLY = (
    "Hello! I'm SmartAssist, your AI assistant. "
    "Ask me about our services, working hours, or any general question."
)

HELP_REPLY = (
    "I can help with greetings, FAQs, and general questions. "
    "Try asking about working hours, contact details, or services. "
    "If I don't have a saved answer, I'll use AI to help you."
)

THANKS_REPLY = "You're welcome! If you have another question, I'm happy to help."

BYE_REPLY = "Goodbye! Have a great day. Come back anytime if you need help."

HOURS_REPLY = (
    "Our working hours are Monday to Friday, 9:00 AM to 6:00 PM IST. "
    "We're closed on weekends and public holidays."
)

CONTACT_REPLY = (
    "You can reach the SmartAssist team at support@smartassist.ai "
    "or visit our help desk during working hours."
)

SERVICES_REPLY = (
    "SmartAssist can answer frequently asked questions, handle greetings, "
    "and use AI to help with general topics such as technology, learning, "
    "and everyday queries."
)

ABOUT_REPLY = (
    "I'm SmartAssist, a demo AI chatbot built with React and FastAPI. "
    "I use saved answers for common questions and an AI API for everything else."
)

AI_FALLBACK_REPLY = (
    "Sorry, I couldn't process that question right now. Please try again later."
)

MISSING_API_KEY_REPLY = (
    "I don't have a saved answer for that, and the AI service is not configured yet. "
    "Please add an AI_API_KEY in the backend .env file, or ask about working hours, "
    "contact, services, or help."
)

# Phrases checked first (more specific FAQs before short greetings).
FAQ_RULES = [
    {
        "category": "working_hours",
        "keywords": [
            "working hours",
            "office hours",
            "work hours",
            "opening hours",
            "what time",
            "timings",
            "timing",
            "when are you open",
            "when do you work",
            "available hours",
            "business hours",
        ],
        "reply": HOURS_REPLY,
    },
    {
        "category": "contact",
        "keywords": [
            "contact",
            "reach you",
            "get in touch",
            "how can i contact",
            "how do i contact",
            "contact you",
        ],
        "reply": CONTACT_REPLY,
    },
    {
        "category": "services",
        "keywords": [
            "services",
            "what do you provide",
            "what can you do",
            "what do you offer",
            "what services",
        ],
        "reply": SERVICES_REPLY,
    },
    {
        "category": "about",
        "keywords": [
            "about the chatbot",
            "about smartassist",
            "about you",
            "who are you",
            "what are you",
            "your name",
            "what is smartassist",
        ],
        "reply": ABOUT_REPLY,
    },
    {
        "category": "thanks",
        "keywords": [
            "thank you",
            "thanks",
            "thx",
            "appreciate it",
            "thank u",
        ],
        "reply": THANKS_REPLY,
    },
    {
        "category": "bye",
        "keywords": [
            "goodbye",
            "good bye",
            "bye",
            "see you",
        ],
        "reply": BYE_REPLY,
    },
    {
        "category": "help",
        "keywords": [
            "help",
            "how does this work",
            "what can you help",
            "i need help",
        ],
        "reply": HELP_REPLY,
    },
]

GREETING_PHRASES = [
    "good morning",
    "good afternoon",
    "good evening",
    "hello",
    "hey",
    "hi",
    "greetings",
]

# Extra words that can appear with a greeting without turning it into a real question.
GREETING_FILLERS = {
    "there",
    "smartassist",
    "assistant",
    "bot",
    "again",
    "everyone",
    "all",
    "team",
    "friend",
    "please",
}
