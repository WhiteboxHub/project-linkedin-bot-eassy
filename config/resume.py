from yaml import *
import json

######################################################
# CONFIGURE YOUR RESUME HERE
######################################################

# Default resume path for uploads
default_resume_path = "modules/resumes/sunil_resume.pdf"

######################################################
# RESUME HEADLINE BUILDER
######################################################

import json

def build_resume_headline():
    """Build resume headline AFTER variables exist."""
    data = {
        "first_name": globals().get("first_name", ""),
        "middle_name": globals().get("middle_name", ""),
        "last_name": globals().get("last_name", ""),
        "phone": globals().get("phone_number", ""),
        "location": globals().get("current_city", "") or "Tirupati, Andhra Pradesh, India",
        "headline": globals().get("linkedin_headline", ""),
        "linkedin": globals().get("linkedIn", ""),
        "skills": [
            "Python", "Machine Learning", "Data Analysis",
            "NumPy", "Pandas", "Cybersecurity", "Threat Detection"
        ]
    }

    return data, json.dumps(data, indent=4)

# Build only when called (AFTER load_candidate())
resume_headline, resume_headline_json = build_resume_headline()

######################################################
# THANK YOU for using this tool 😊!
# Wishing you the best in your job hunt 🙌🏻!
# Sharing is caring!
# Gratefully yours 🙏🏻,
# Sunil Poli
######################################################
