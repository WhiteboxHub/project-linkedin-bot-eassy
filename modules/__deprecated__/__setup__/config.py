# '''
# Author:     Sai Vignesh Golla
# LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

# Copyright (C) 2024 Sai Vignesh Golla

# License:    GNU Affero General Public License
#             https://www.gnu.org/licenses/agpl-3.0.en.html
            
# GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

# '''


# ############### OLD CONFIG FILE - FOR REFERENCE FOR DEVELOPERS - DO NOT USE #################



# ###################################################### CONFIGURE YOUR TOOLS HERE ######################################################
  
# # >>>>>>>>>>> Global Settings <<<<<<<<<<<

# # Directory and name of the files where history of applied jobs is saved (Sentence after the last "/" will be considered as the file name).
# file_name = "all excels/all_applied_applications_history.csv"
# failed_file_name = "all excels/all_failed_applications_history.csv"
# logs_folder_path = "logs/"

# # Set the maximum amount of time allowed to wait between each click in secs
# click_gap = 0                      # Enter max allowed secs to wait approximately. (Only Non Negative Integers Eg: 0,1,2,3,....)

# # If you want to see Chrome running then set run_in_background as False (May reduce performance). 
# run_in_background = False          # True or False, Note: True or False are case-sensitive ,   If True, this will make pause_at_failed_question, pause_before_submit and run_in_background as False

# # If you want to disable extensions then set disable_extensions as True (Better for performance)
# disable_extensions = True          # True or False, Note: True or False are case-sensitive

# # Run in safe mode. Set this true if chrome is taking too long to open or if you have multiple profiles in browser. This will open chrome in guest profile!
# safe_mode = True                 # True or False, Note: True or False are case-sensitive

# # Do you want scrolling to be smooth or instantaneous? (Can reduce performance if True)
# smooth_scroll = False              # True or False, Note: True or False are case-sensitive

# # If enabled (True), the program would keep your screen active and prevent PC from sleeping. Instead you could disable this feature (set it to false) and adjust your PC sleep settings to Never Sleep or a preferred time. 
# keep_screen_awake = True           # True or False, Note: True or False are case-sensitive (Note: Will temporarily deactivate when any application dialog boxes are present (Eg: Pause before submit, Help needed for a question..))

# # Run in undetected mode to bypass anti-bot protections (Preview Feature, UNSTABLE. Recommended to leave it as False)
# undetected_mode = True             # True or False, Note: True or False are case-sensitive
# # Now called as stealth_mode

# # Use ChatGPT for resume building (Experimental Feature can break the application. Recommended to leave it as False) 
# use_resume_generator = False       # True or False, Note: True or False are case-sensitive ,   This feature may only work with 'undetected_mode' = True. As ChatGPT website is hosted by CloudFlare which is protected by Anti-bot protections!



# # ----------------------------------------------  AUTO APPLIER  ---------------------------------------------- #

# # Login Credentials for LinkedIn
# username = "username@example.com"  # Enter your username in the quotes
# password = "example_password"      # Enter your password in the quotes

# # These Sentences are Searched in LinkedIn
# # Enter your search terms inside '[ ]' with quotes ' "searching title" ' for each search followed by comma ', ' Eg: ["Software Engineer", "Software Developer", "Selenium Developer"]
# search_terms = ["Software Engineer", "Software Developer", "Python Developer", "Selenium Developer", "React Developer", "Java Developer", "Front End Developer", "Full Stack Developer", "Web Developer", "Nodejs Developer"]

# # Search location, this will be filled in "City, state, or zip code" search box. If left empty as "", tool will not fill it.
# search_location = ""               # Some valid examples: "", "United States", "India", "Chicago, Illinois, United States", "90001, Los Angeles, California, United States", "Bengaluru, Karnataka, India", etc.


# # >>>>>>>>>>> Job Search Filters <<<<<<<<<<<
# ''' 
# You could set your preferences or leave them as empty to not select options except for 'True or False' options. Below are some valid examples for leaving them empty:

# question_1 = ""                    # answer1, answer2, answer3, etc.
# question_2 = []                    # (multiple select)
# question_3 = []                    # (dynamic multiple select)

# '''

# sort_by = ""                       # "Most recent", "Most relevant" or ("" to not select) 
# date_posted = "Past month"         # "Any time", "Past month", "Past week", "Past 24 hours" or ("" to not select)
# salary = ""                        # "$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+"

# easy_apply_only = True             # True or False, Note: True or False are case-sensitive

# experience_level = []              # (multiple select) "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"
# job_type = []                      # (multiple select) "Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"
# on_site = []                       # (multiple select) "On-site", "Remote", "Hybrid"

# companies = []                     # (dynamic multiple select) make sure the name you type in list exactly matches with the company name you're looking for, including capitals. 
#                                    # Eg: "7-eleven", "Google","X, the moonshot factory","YouTube","CapitalG","Adometry (acquired by Google)","Meta","Apple","Byte Dance","Netflix", "Snowflake","Mineral.ai","Microsoft","JP Morgan","Barclays","Visa","American Express", "Snap Inc", "JPMorgan Chase & Co.", "Tata Consultancy Services", "Recruiting from Scratch", "Epic", and so on...
# location = []                      # (dynamic multiple select)
# industry = []                      # (dynamic multiple select)
# job_function = []                  # (dynamic multiple select)
# job_titles = []                    # (dynamic multiple select)
# benefits = []                      # (dynamic multiple select)
# commitments = []                   # (dynamic multiple select)

# under_10_applicants = False        # True or False, Note: True or False are case-sensitive
# in_your_network = False            # True or False, Note: True or False are case-sensitive
# fair_chance_employer = False       # True or False, Note: True or False are case-sensitive



# # >>>>>>>>>>> Easy Apply Questions & Inputs <<<<<<<<<<<

# # Phone number (required), make sure it's valid.
# phone_number = "9876543210"        # Enter your 10 digit number in quotes Eg: "9876543210"

# # Give an relative or absolute path of your default resume to be uploaded. If file in not found, will continue using your previously uploaded resume in LinkedIn.
# default_resume_path = "all resumes/default/resume.pdf"      # (In Development)

# # What do you want to answer for questions that ask about years of experience you have, this is different from current_experience? 
# years_of_experience = "5"          # A number in quotes Eg: "0","1","2","3","4", etc.

# # Do you need visa sponsorship now or in future?
# require_visa = "No"               # "Yes" or "No"

# # What is the status of your citizenship? # If left empty as "", tool will not answer the question. However, note that some companies make it compulsory to be answered
# # Valid options are: "U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer", "Non-citizen allowed to work for current employer", "Non-citizen seeking work authorization", "Canadian Citizen/Permanent Resident" or "Other"
# us_citizenship = "U.S. Citizen/Permanent Resident"


# # What is the link to your portfolio website, leave it empty as "", if you want to leave this question unanswered
# website = "https://github.com/GodsScion"                       # "www.example.bio" or "" and so on....

# # What to enter in your desired salary question, only enter in numbers inside quotes as some companies only allow numbers
# desired_salary = "120000"          # "80000", "90000", "100000" or "120000" and so on....

# # Example question: "On a scale of 1-10 how much experience do you have building web or mobile applications? 1 being very little or only in school, 10 being that you have built and launched applications to real users"
# confidence_level = "8"             # Any number between "1" to "10" including 1 and 10, put it in quotes ""

# current_city = ""                  # If left empty will fill in location of jobs location.

# ## SOME ANNOYING QUESTIONS BY COMPANIES 🫠 ##
# # Address, not so common question but some job applications make it required!
# street = "123 Main Street"
# state = "STATE"
# zipcode = "12345"
# country = "Will Let You Know When Established"

# first_name = "Sai"                 # Your first name in quotes Eg: "First", "Sai"
# middle_name = "Vignesh"            # Your name in quotes Eg: "Middle", "Vignesh", ""
# last_name = "Golla"                # Your last name in quotes Eg: "Last", "Golla"

# # Your LinkedIn headline in quotes Eg: "Software Engineer @ Google, Masters in Computer Science", "Recent Grad Student @ MIT, Computer Science"
# headline = "Headline"

# # Your summary in quotes, use \n to add line breaks
# summary = "Summary"

# # Your cover letter in quotes, use \n to add line breaks
# cover_letter = "Cover Letter"

# # Name of your most recent employer
# recent_employer = "Not Applicable" # "", "Lala Company", "Google", "Snowflake", "Databricks"

# ## US Equal Opportunity questions
# # What is your ethnicity or race? If left empty as "", tool will not answer the question. However, note that some companies make it compulsory to be answered
# ethnicity = "Decline"              # "Decline", "Hispanic/Latino", "American Indian or Alaska Native", "Asian", "Black or African American", "Native Hawaiian or Other Pacific Islander", "White", "Other"

# # How do you identify yourself? If left empty as "", tool will not answer the question. However, note that some companies make compulsory to be answered
# gender = "Decline"                 # "Male", "Female", "Other", "Decline" or ""

# # Are you physically disabled or have a history/record of having a disability? If left empty as "", tool will not answer the question. However, note that some companies make it compulsory to be answered
# disability_status = "Decline"      # "Yes", "No", "Decline"

# veteran_status = "Decline"         # "Yes", "No", "Decline"
# ##



# # >>>>>>>>>>> LinkedIn Settings <<<<<<<<<<<

# # Do you want to randomize the search order for search_terms?
# randomize_search_order = False     # True of False

# # Do you want to overwrite previous answers?
# overwrite_previous_answers = False # True or False, Note: True or False are case-sensitive


# ## Skip irrelevant jobs
# # Avoid applying to these companies, and companies with these bad words in their 'About Company' section...
# # about_company_bad_words = ["Crossover", "Staffing", "Recruiting", "Jobot"]       # (dynamic multiple search) or leave empty as []. Ex: ["Staffing", "Recruiting", "Name of Company you don't want to apply to"]
# about_company_bad_words = []

# # Skip checking for `about_company_bad_words` for these companies if they have these good words in their 'About Company' section... [Exceptions, For example, I want to apply to "Robert Half" although it's a staffing company]
# about_company_good_words = []      # (dynamic multiple search) or leave empty as []. Ex: ["Robert Half", "Dice"]


# # Avoid applying to these companies if they have these bad words in their 'Job Description' section...  (In development)
# bad_words = ["US Citizen","USA Citizen","No C2C", "No Corp2Corp", ".NET", "Embedded Programming", "PHP", "Ruby"]                     # (dynamic multiple search) or leave empty as []. Case Insensitive. Ex: ["word_1", "phrase 1", "word word", "polygraph", "US Citizenship", "Security Clearance"]

# # Do you have an active Security Clearance? (True for Yes and False for No)
# security_clearance = False         # True or False, Note: True or False are case-sensitive

# # Do you have a Masters degree? (True for Yes and False for No). If True, the tool will apply to jobs containing the word 'master' in their job description and if it's experience required <= current_experience + 2 and current_experience is not set as -1. 
# did_masters = True                 # True or False, Note: True or False are case-sensitive

# # Avoid applying to jobs if their required experience is above your current_experience. (Set value as -1 if you want to apply to all ignoring their required experience...)
# current_experience = 5             # Integers > -2 (Ex: -1, 0, 1, 2, 3, 4...)
# ##


# ## Allow Manual Inputs
# # Should the tool pause before every submit application during easy apply to let you check the information?
# pause_before_submit = True         # True or False, Note: True or False are case-sensitive
# '''
# Note: Will be treated as False if `run_in_background = True`
# '''

# # Should the tool pause if it needs help in answering questions during easy apply?
# # Note: If set as False will answer randomly...
# pause_at_failed_question = True    # True or False, Note: True or False are case-sensitive
# '''
# Note: Will be treated as False if `run_in_background = True`
# '''
# ##

# # Keep the External Application tabs open? (Note: RECOMMENDED TO LEAVE IT AS TRUE, if you set it false, be sure to CLOSE ALL TABS BEFORE CLOSING THE BROWSER!!!)
# close_tabs = True                  # True or False, Note: True or False are case-sensitive

# # After how many number of applications in current search should the bot switch to next search? 
# switch_number = 30                 # Only numbers greater than 0... Don't put in quotes

# ## Upcoming features (In Development)
# # Send connection requests to HR's
# connect_hr = True                  # True or False, Note: True or False are case-sensitive

# # What message do you want to send during connection request? (Max. 200 Characters)
# connect_request_message = ""       # Leave Empty to send connection request without personalized invitation (recommended to leave it empty, since you only get 10 per month without LinkedIn Premium*)

# # Do you want the program to run continuously until you stop it? (Beta)
# run_non_stop = False               # True or False, Note: True or False are case-sensitive
# '''
# Note: Will be treated as False if `run_in_background = True`
# '''
# alternate_sortby = True            # True or False, Note: True or False are case-sensitive
# cycle_date_posted = True           # True or False, Note: True or False are case-sensitive
# stop_date_cycle_at_24hr = True     # True or False, Note: True or False are case-sensitive
# ##




# # ----------------------------------------------  RESUME GENERATOR (Experimental & In Development)  ---------------------------------------------- #

# # Login Credentials for ChatGPT
# chatGPT_username = "username@example.com"
# chatGPT_password = "example_password"

# chatGPT_resume_chat_title = "Resume review and feedback."

# # Give the path to the folder where all the generated resumes are to be stored
# generated_resume_path = "all resumes/"
















# ############################################################################################################
# '''
# THANK YOU for using my tool 😊! Wishing you the best in your job hunt 🙌🏻!

# Sharing is caring! If you found this tool helpful, please share it with your peers 🥺. Your support keeps this project alive.

# Support my work on <PATREON_LINK>. Together, we can help more job seekers.

# As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact.

# Your support, whether through donations big or small or simply spreading the word, means the world to me and helps keep this project alive and thriving.

# Gratefully yours 🙏🏻,
# Sai Vignesh Golla
# '''
# ############################################################################################################






############### UPDATED CONFIG — BASED ON SWARNA’S DETAILS #################

# >>>>>>>>>>> Global Settings <<<<<<<<<<<

# file_name = "all excels/all_applied_applications_history.csv"
# failed_file_name = "all excels/all_failed_applications_history.csv"
# logs_folder_path = "logs/"

# click_gap = 0
# run_in_background = False
# disable_extensions = True
# safe_mode = False            # YOU SAID: safe_mode = False
# smooth_scroll = False
# keep_screen_awake = True
# undetected_mode = True
# use_resume_generator = False

# # ----------------------------------------------  AUTO APPLIER  ---------------------------------------------- #

# # 🔐 Login Credentials
# username = "swarna.mp01@gmail.com"
# password = "ABC1@100"

# # 🎯 Search Job Titles
# search_terms = [
#     "ML Engineer",
#     "Gen AI Engineer",
#     "LLM Engineer"
# ]

# # 📍 Locations
# # "City, State" OR "Remote"
# search_location = ""   # Bot will select filters below instead

# # >>>>>>>>>>> Job Search Filters <<<<<<<<<<<

# sort_by = ""
# date_posted = "Past month"
# salary = "160000"   # You said salary: 160,000

# easy_apply_only = True

# experience_level = [
#     "Entry level",
#     "Associate",
#     "Mid-Senior level",
#     "Director",
#     "Executive",
#     "Internship"
# ]

# job_type = ["Full-time"]
# on_site = [
#     "On-site",
#     "Remote",
#     "Hybrid"
# ]

# # Skip these companies
# companies = []
# location = []
# industry = []
# job_function = []
# job_titles = []
# benefits = []
# commitments = []

# under_10_applicants = False
# in_your_network = False
# fair_chance_employer = False

# # >>>>>>>>>>> Easy Apply Questions <<<<<<<<<<<

# phone_number = "1 (510) 427-2514" 

# default_resume_path = "Resumes/swarnalatha.pdf"
# years_of_experience = "5"
# require_visa = "No"
# us_citizenship = ""
# website = ""

# desired_salary = "160000"  # Rounded to 160k
# confidence_level = "8"
# current_city = ""

# street = ""
# state = ""
# zipcode = ""
# country = ""

# first_name = "Swarnalatha"
# middle_name = ""
# last_name = " "

# headline = "Machine Learning & Generative AI Engineer"
# summary = "Experienced in Machine Learning, LLMs, and Gen AI applications."
# cover_letter = ""

# recent_employer = ""

# ethnicity = "Decline"
# gender = "Female"
# disability_status = "Decline"
# veteran_status = "Decline"

# # >>>>>>>>>>> LinkedIn Settings <<<<<<<<<<<

# randomize_search_order = False
# overwrite_previous_answers = False

# about_company_bad_words = []
# about_company_good_words = []

# bad_words = ["US Citizen","USA Citizen","No C2C", "No Corp2Corp", ".NET", "Embedded Programming", "PHP", "Ruby"]

# security_clearance = False
# did_masters = True
# current_experience = 5

# pause_before_submit = True
# pause_at_failed_question = True

# close_tabs = True
# switch_number = 30

# connect_hr = True
# connect_request_message = ""

# run_non_stop = False
# alternate_sortby = True
# cycle_date_posted = True
# stop_date_cycle_at_24hr = True

# # >>>>>>>>>>> Resume Generator <<<<<<<<<<<

# chatGPT_username = "username@example.com"
# chatGPT_password = "example_password"
# chatGPT_resume_chat_title = "Resume review and feedback."
# generated_resume_path = "all resumes/"

# # >>>>>>>>>>> Output File <<<<<<<<<<<

# output_filename = ["I:/IP-Codebases/LinkedInAutomation/OUTPUT.csv"]

# # >>>>>>>>>>> Blacklist <<<<<<<<<<<

# blacklist = [
#     "Gainwell Technologies",
#     "CIGNA Health Insurance",
#     "UHG",
#     "AMEX"
# ]




# ----------------------------------------------  FILE PATHS & LOGGING  ---------------------------------------------- #

# file_name = "all excels/all_applied_applications_history.csv"
# failed_file_name = "all excels/all_failed_applications_history.csv"
# logs_folder_path = "logs/"

# click_gap = 0
# run_in_background = False
# disable_extensions = True
# safe_mode = False
# smooth_scroll = False
# keep_screen_awake = True
# undetected_mode = True
# use_resume_generator = False


# # ----------------------------------------------  LOGIN CREDENTIALS  ---------------------------------------------- #

# username = "swarna.mp01@gmail.com"
# password = "YOUR_PASSWORD_HERE"   # ← Replace manually on your machine only


# # ----------------------------------------------  JOB SEARCH SETTINGS  ---------------------------------------------- #

# search_terms = [
#     "ML Engineer",
#     "Gen AI Engineer",
#     "LLM Engineer"
# ]

# search_location = ""   # Bot will choose from filters

# sort_by = ""
# date_posted = "Past month"
# salary = "160000"

# easy_apply_only = True

# experience_level = [
#     "Entry level",
#     "Associate",
#     "Mid-Senior level",
#     "Director",
#     "Executive",
#     "Internship"
# ]

# job_type = ["Full-time"]

# on_site = [
#     "On-site",
#     "Remote",
#     "Hybrid"
# ]

# companies = []
# location = []
# industry = []
# job_function = []
# job_titles = []
# benefits = []
# commitments = []

# under_10_applicants = False
# in_your_network = False
# fair_chance_employer = False


# # ----------------------------------------------  EASY APPLY QUESTIONS  ---------------------------------------------- #

# phone_number = "1 (510) 427-2514"

# default_resume_path = "Resumes/swarnalatha.pdf"
# years_of_experience = "5"
# require_visa = "No"
# us_citizenship = ""
# website = ""

# desired_salary = "160000"
# confidence_level = "8"
# current_city = ""

# street = ""
# state = ""
# zipcode = ""
# country = ""

# first_name = "Swarnalatha"
# middle_name = ""
# last_name = ""

# headline = "Machine Learning & Generative AI Engineer"
# summary = "Experienced in Machine Learning, LLMs, and Gen AI applications."
# cover_letter = ""

# recent_employer = ""

# ethnicity = "Decline"
# gender = "Female"
# disability_status = "Decline"
# veteran_status = "Decline"


# # ----------------------------------------------  LINKEDIN AUTOMATION BEHAVIOR  ---------------------------------------------- #

# randomize_search_order = False
# overwrite_previous_answers = False

# about_company_bad_words = []
# about_company_good_words = []

# bad_words = [
#     "US Citizen",
#     "USA Citizen",
#     "No C2C",
#     "No Corp2Corp",
#     ".NET",
#     "Embedded Programming",
#     "PHP",
#     "Ruby"
# ]

# security_clearance = False
# did_masters = True
# current_experience = 5

# pause_before_submit = True
# pause_at_failed_question = True

# close_tabs = True
# switch_number = 30

# connect_hr = True
# connect_request_message = ""

# run_non_stop = False
# alternate_sortby = True
# cycle_date_posted = True
# stop_date_cycle_at_24hr = True


# # ----------------------------------------------  RESUME GENERATOR (OPTIONAL)  ---------------------------------------------- #

# chatGPT_username = "username@example.com"
# chatGPT_password = "example_password"
# chatGPT_resume_chat_title = "Resume review and feedback."
# generated_resume_path = "all resumes/"


# # ----------------------------------------------  OUTPUT SETTINGS  ---------------------------------------------- #

# output_filename = ["I:/IP-Codebases/LinkedInAutomation/OUTPUT.csv"]


# # ----------------------------------------------  BLACKLIST COMPANIES  ---------------------------------------------- #

# blacklist = [
#     "Gainwell Technologies",
#     "CIGNA Health Insurance",
#     "UHG",
#     "AMEX"
# ]



# ----------------------------------------------  FILE PATHS & LOGGING  ---------------------------------------------- #

file_name = "all excels/all_applied_applications_history.csv"
failed_file_name = "all excels/all_failed_applications_history.csv"
logs_folder_path = "logs/"

click_gap = 0
run_in_background = False
disable_extensions = True
safe_mode = False
smooth_scroll = False
keep_screen_awake = True
undetected_mode = True
use_resume_generator = False


# ----------------------------------------------  LOGIN CREDENTIALS  ---------------------------------------------- #

username = "viji05189@gmail.com"
password = "KarSaptMang@4"     # Replace locally with:  KarSaptMang@4


# ----------------------------------------------  JOB SEARCH SETTINGS  ---------------------------------------------- #

search_terms = [
    "Machine Learning Engineer",
    "Gen AI"
]

search_location = ""   # filters will handle location

sort_by = ""
date_posted = "Past month"

salary = "150000"      # Annual salary expectation
rate = "70"            # Hourly rate (if asked)

easy_apply_only = True

experience_level = [
    "Entry level",
    "Associate",
    "Mid-Senior level",
    "Director",
    "Executive",
    "Internship"
]

job_type = ["Full-time"]

on_site = [
    "On-site",
    "Remote",
    "Hybrid"
]

companies = []
location = []
industry = []
job_function = []
job_titles = []
benefits = []
commitments = []

under_10_applicants = False
in_your_network = False
fair_chance_employer = False


# ----------------------------------------------  EASY APPLY QUESTIONS  ---------------------------------------------- #

phone_number = "510-648-1296"

default_resume_path = "Resumes/Vijayalakshmi.pdf"

years_of_experience = "5"       # If you want a different number, tell me
require_visa = ""
us_citizenship = ""
website = ""

desired_salary = "150000"
confidence_level = "8"
current_city = ""

street = ""
state = ""
zipcode = ""
country = ""

# Name
first_name = "Vijayalakshmi"
middle_name = ""
last_name = ""               # If you have last name, tell me

headline = "Machine Learning & Gen AI Engineer"
summary = "Experienced in Machine Learning, NLP, and Generative AI."
cover_letter = ""

recent_employer = ""

ethnicity = "Decline"
gender = "Female"
disability_status = "Decline"
veteran_status = "Decline"


# ----------------------------------------------  LINKEDIN AUTOMATION BEHAVIOR  ---------------------------------------------- #

randomize_search_order = False
overwrite_previous_answers = False

about_company_bad_words = []
about_company_good_words = []

bad_words = [
    "US Citizen",
    "USA Citizen",
    "No C2C",
    "No Corp2Corp",
    ".NET",
    "Embedded Programming",
    "PHP",
    "Ruby"
]

security_clearance = False
did_masters = True
current_experience = 5

pause_before_submit = True
pause_at_failed_question = True

close_tabs = True
switch_number = 30

connect_hr = True
connect_request_message = ""

run_non_stop = False
alternate_sortby = True
cycle_date_posted = True
stop_date_cycle_at_24hr = True


# ----------------------------------------------  RESUME GENERATOR (OPTIONAL)  ---------------------------------------------- #

chatGPT_username = "username@example.com"
chatGPT_password = "example_password"
chatGPT_resume_chat_title = "Resume review and feedback."
generated_resume_path = "all resumes/"


# ----------------------------------------------  OUTPUT SETTINGS  ---------------------------------------------- #

output_filename = ["I:/IP-Codebases/LinkedInAutomation/OUTPUT.csv"]


# ----------------------------------------------  BLACKLIST COMPANIES  ---------------------------------------------- #

blacklist = [
    "Lucid Motors",
    "Jitterbit.Inc"
]
