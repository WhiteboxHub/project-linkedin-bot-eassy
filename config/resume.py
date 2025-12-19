
# # from personals import *
# # import json


# # ###################################################### CONFIGURE YOUR RESUME HERE ######################################################

# # # Default resume path for uploads  
# # # Your resume file:
# # default_resume_path = "modules/resumes/swarnalatha_resume.pdf"      # Your resume stored in the same folder


# # '''
# # YOU DON'T HAVE TO EDIT THIS FILE, IF YOU ADDED YOUR DEFAULT RESUME.
# # This file will auto-generate fields required for headline, name, and user identity.
# # '''

# # # Auto-generate your resume headline JSON (used internally by tool)
# # resume_headline = {
# #     "first_name": first_name,         # From personals.py
# #     "middle_name": middle_name,       # From personals.py
# #     "last_name": last_name,           # From personals.py
# #     "phone": phone_number,
# #     "location": current_city if current_city else "Frisco, Texas, USA",
# #     "headline": linkedin_headline,
# #     "linkedin": linkedIn,
# #     "skills": [
# #         "Python", "AI/ML Engineering", "Data Science", "NLP", "LangChain", 
# #         "Generative AI", "AWS", "Large Language Models (LLMs)", "RAG Pipelines"
# #     ]
# # }

# # resume_headline_json = json.dumps(resume_headline, indent=4)




# from personals import *
# import json


# ###################################################### CONFIGURE YOUR RESUME HERE ######################################################

# # Default resume path for uploads  
# # Your resume file:
# # default_resume_path = "modules/resumes/vijayalakshmi_resume.pdf"      # Your resume stored in the same folder
# default_resume_path = "modules/resumes/sujatha_akkala.pdf" 

# '''
# YOU DON'T HAVE TO EDIT THIS FILE, IF YOU ADDED YOUR DEFAULT RESUME.
# This file will auto-generate fields required for headline, name, and user identity.
# '''

# # Auto-generate your resume headline JSON (used internally by tool)
# resume_headline = {
#     "first_name": first_name,               # From personals.py
#     "middle_name": middle_name,             # From personals.py
#     "last_name": last_name,                 # From personals.py
#     "phone": phone_number,
#     "location": current_city if current_city else "Mountain House, CA, USA",
#     "headline": linkedin_headline,
#     "linkedin": linkedIn,
#     "skills": [
#         "Python", 
#         "Machine Learning", 
#         "AI/ML Engineering", 
#         "Generative AI", 
#         "LangGraph",
#         "LangChain", 
#         "LLMs", 
#         "RAG Pipelines",
#         "NLP",
#         "Vector Databases (Milvus, Chroma)",
#         "AWS Bedrock",
#         "AWS Sagemaker",
#         "FastAPI",
#         "MLOps",
#         "Docker", 
#         "Kubernetes"
#     ]
# }

# # Convert to JSON string for other modules if needed
# resume_headline_json = json.dumps(resume_headline, indent=4)





from yaml import *
import json


###################################################### CONFIGURE YOUR RESUME HERE ######################################################

# Default resume path for uploads  
# Your resume file:
default_resume_path = "modules/resumes/sunil_resume.pdf"      # Your resume stored in the same folder


# '''
# YOU DON'T HAVE TO EDIT THIS FILE, IF YOU ADDED YOUR DEFAULT RESUME.
# This file will auto-generate fields required for headline, name, and user identity.
# '''

# # Auto-generate your resume headline JSON (used internally by tool)
# resume_headline = {
#     "first_name": first_name,         # From personals.py
#     "middle_name": middle_name,       # From personals.py
#     "last_name": last_name,           # From personals.py
#     "phone": phone_number,
#     "location": current_city if current_city else "Tirupati, Andhra Pradesh, India",
#     "headline": linkedin_headline,
#     "linkedin": linkedIn,
#     "skills": [
#         "Python", "Machine Learning", "Data Analysis", "NumPy", "Pandas",
#         "Cybersecurity", "Threat Detection"
#     ]
# }

# # Convert to JSON string for other modules if needed
# resume_headline_json = json.dumps(resume_headline, indent=4)



# ############################################################################################################
# '''
# THANK YOU for using this tool 😊! Wishing you the best in your job hunt 🙌🏻!

# Sharing is caring! If you found this tool helpful, please share it with your peers 🥺. 
# Your support keeps this project alive.

# Gratefully yours 🙏🏻,
# Sunil Poli
# '''
# ############################################################################################################



import json

# Delay evaluation – this function builds the resume headline AFTER variables exist
def build_resume_headline():
    # Use globals dynamically after YAML mapping is loaded
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

    # Return both object and JSON string
    return data, json.dumps(data, indent=4)


# Build only when called (AFTER load_candidate())
resume_headline, resume_headline_json = build_resume_headline()

############################################################################################################
'''
THANK YOU for using this tool 😊! Wishing you the best in your job hunt 🙌🏻!

Sharing is caring! If you found this tool helpful, please share it with your peers 🥺. 
Your support keeps this project alive.

Gratefully yours 🙏🏻,
Sunil Poli
'''
############################################################################################################
