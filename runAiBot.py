
# Imports
import os
import csv
import re
import json
import pyautogui
import requests
from time import sleep
from random import choice, shuffle, randint
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver

# Load environment variables from .env file
load_dotenv()

# Set CSV field size limit to prevent field size errors
csv.field_size_limit(1000000)

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException, ElementNotInteractableException, WebDriverException, StaleElementReferenceException

# Replace all config imports with the loader
from config.loader import load_candidate, extract_variables

from modules.open_chrome import *
from modules.helpers import *
from modules.clickers_and_finders import *
from modules.validator import validate_config
from modules.ai.openaiConnections import ai_create_openai_client, ai_extract_skills, ai_answer_question, ai_close_openai_client
from modules.ai.deepseekConnections import deepseek_create_client, deepseek_extract_skills, deepseek_answer_question
from modules.ai.geminiConnections import gemini_create_client, gemini_extract_skills, gemini_answer_question
from modules.filtering import *

from typing import Literal


pyautogui.FAILSAFE = False
# if use_resume_generator:    from resume_generator import is_logged_in_GPT, login_GPT, open_resume_chat, create_custom_resume


#< Global Variables and logics

# Load configuration from YAML
try:
    cfg = load_candidate()
    # Extract all variables from config
    globals().update(extract_variables(cfg))
except Exception as e:
    pyautogui.alert(f"Failed to load configuration: {e}", "Configuration Error")
    raise e

if run_in_background == True:
    pause_at_failed_question = False
    pause_before_submit = False
    run_non_stop = False

first_name = first_name.strip()
middle_name = middle_name.strip()
last_name = last_name.strip()
full_name = first_name + " " + middle_name + " " + last_name if middle_name else first_name + " " + last_name

# API Configuration (Dynamic fallback to full_name)
API_OPERATOR_NAME = os.environ.get("API_OPERATOR_NAME") or full_name


useNewResume = True
randomly_answered_questions = set()

tabs_count = 1
easy_applied_count = 0
external_jobs_count = 0
failed_count = 0
skip_count = 0
dailyEasyApplyLimitReached = False
pending_activity_logs = []


#< Count persistence functions

COUNTS_FILE = "output/counts.json"

def load_counts():
    """Load persistent counts for all candidates from JSON file."""
    try:
        with open(COUNTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_counts(counts_data):
    """Save persistent counts for all candidates to JSON file."""
    try:
        make_directories(["output"])
        with open(COUNTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(counts_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print_lg(f"Failed to save counts: {e}")

def get_candidate_counts(candidate_name, counts_data):
    """Get counts for a specific candidate, initialize if not exists. Reset if new day."""
    if candidate_name not in counts_data:
        counts_data[candidate_name] = {
            "easy_applied": 0,
            "external": 0,
            "failed": 0,
            "skipped": 0,
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # Check for daily reset
    data = counts_data[candidate_name]
    last_updated_str = data.get("last_updated", "")
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # If last_updated is empty or from a previous day
    # Note: last_updated_str is "YYYY-MM-DD HH:MM:SS" so startswith matches date part
    if not last_updated_str.startswith(today_str):
        print_lg(f"🔄 New Day Detected for {candidate_name}: Resetting daily counts to 0.")
        data["easy_applied"] = 0
        data["external"] = 0
        data["failed"] = 0
        data["skipped"] = 0
        data["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # We need to save this reset immediately so it persists even if bot crashes
        save_counts(counts_data)
        
    return data

def update_candidate_count(candidate_name, count_type, counts_data):
    """Update a specific count for a candidate and save."""
    counts = get_candidate_counts(candidate_name, counts_data)
    counts[count_type] += 1
    counts["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_counts(counts_data)

#< Website API integration
# Load from environment variables
# Website API Configuration
WBL_API_URL = os.environ.get("WBL_API_URL", "https://api.whitebox-learning.com/api")
SECRET_KEY = os.environ.get("SECRET_KEY", "")
API_EMAIL = os.environ.get("API_EMAIL", "")
API_PASSWORD = os.environ.get("API_PASSWORD", "")
API_TOKEN = os.environ.get("WEBSITE_API_TOKEN", "")


# Cache file for API token (matching reference code format)
API_TOKEN_CACHE_FILE = "data/.api_token.json"

def get_api_token(force_refresh=False):
    """
    Get API token - first check cache, then authenticate with email/password if needed.
    """
    global API_TOKEN
    
    # If force refresh requested, clear existing token and cache
    if force_refresh:
        print_lg("Force refreshing API token...")
        API_TOKEN = ""
        if os.path.exists(API_TOKEN_CACHE_FILE):
            try:
                os.remove(API_TOKEN_CACHE_FILE)
                print_lg("Cleared cached token file.")
            except Exception as e:
                print_lg(f"Could not remove cache file: {e}")
    
    # If already have token in memory, use it
    if API_TOKEN:
        return API_TOKEN
    
    # Check cache file first
    if os.path.exists(API_TOKEN_CACHE_FILE):
        try:
            with open(API_TOKEN_CACHE_FILE, 'r') as f:
                cached = json.load(f)
                token = cached.get('access_token')
                if token:
                    expiry_ts = cached.get('expiry_ts')
                    if expiry_ts and int(expiry_ts) < int(datetime.now().timestamp()):
                        print_lg("Cached API token has expired; re-authenticating...")
                    else:
                        print_lg(f"Using cached API token from {API_TOKEN_CACHE_FILE}")
                        API_TOKEN = token
                        return token
        except Exception as e:
            print_lg(f"Error reading cached token: {e}")

    
    # Authenticate using email/password if provided
    if API_EMAIL and API_PASSWORD:
        print_lg("Attempting to authenticate with website...")
        try:
            # Use correct endpoint and OAuth2 form data
            login_url = f"{WBL_API_URL}/login"
            
            # OAuth2 form data (not JSON!)
            form_data = {
                "username": API_EMAIL,
                "password": API_PASSWORD,
                "grant_type": "password"
            }
            
            response = requests.post(login_url, data=form_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                
                if token:
                    # Get expiry if available
                    expires_in = data.get('expires_in')
                    expiry_ts = None
                    if isinstance(expires_in, (int, float)):
                        expiry_ts = int(datetime.now().timestamp()) + int(expires_in)
                    
                    # Cache the token in correct format
                    os.makedirs("data", exist_ok=True)
                    with open(API_TOKEN_CACHE_FILE, 'w') as f:
                        json.dump({
                            "access_token": token,
                            "expiry_ts": expiry_ts
                        }, f, indent=2)
                    
                    API_TOKEN = token
                    print_lg("✅ Successfully authenticated and cached API token!")
                    return token
                else:
                    print_lg(f"Login response didn't contain access_token: {data}")
            else:
                print_lg(f"Authentication failed with status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print_lg(f"Authentication error: {e}")
    
    return ""

# Cache for the dynamically fetched IDs
_CACHED_JOB_TYPE_ID = None
_CACHED_CANDIDATE_ID = None

# Get API token at startup (auto-authenticate if needed)
API_TOKEN = get_api_token()

# For backward compatibility with existing code that uses WEBSITE_URL
WEBSITE_URL = WBL_API_URL

def get_job_type_id():
    """Dynamically find OR CREATE a Job Type ID to use for logging."""
    global _CACHED_JOB_TYPE_ID
    if _CACHED_JOB_TYPE_ID is not None:
        return _CACHED_JOB_TYPE_ID

    if not API_TOKEN: return 1  # Fallback if no token

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "X-Secret-Key": SECRET_KEY,
        "Content-Type": "application/json"
    }

    try:
        # 1. Try to find existing job type
        url_get = f"{WEBSITE_URL.rstrip('/')}/job-types"
        response = requests.get(url_get, headers=headers, timeout=10)
        
        if response.status_code == 401:
             print_lg("Token rejected (401) in get_job_type_id. Refreshing...")
             get_api_token(force_refresh=True)
             headers["Authorization"] = f"Bearer {API_TOKEN}"
             response = requests.get(url_get, headers=headers, timeout=10)

        if response.status_code == 200:

            data = response.json()
            jobs = data if isinstance(data, list) else data.get("data", [])
            for job in jobs:
                if "bot linkedin easy apply" in str(job.get("name", "")).lower():
                    _CACHED_JOB_TYPE_ID = job["id"]
                    print_lg(f"Found existing Job Type: {job.get('name')} (ID: {_CACHED_JOB_TYPE_ID})")
                    return _CACHED_JOB_TYPE_ID
                # Fallback to generic linkedin search if specific name not found in this loop iteration (wait, strict search better?)
                # Actually, let's just prioritizing exact match or strict containment
            
            # Second pass: generic 'linkedin' search
            for job in jobs:
                 if "linkedin" in str(job.get("name", "")).lower() and _CACHED_JOB_TYPE_ID is None:
                    _CACHED_JOB_TYPE_ID = job["id"]
                    print_lg(f"Found generic Job Type: {job.get('name')} (ID: {_CACHED_JOB_TYPE_ID})")
                    return _CACHED_JOB_TYPE_ID

            # If we are here, no "LinkedIn" job exists. We should create one.
            print_lg("No 'LinkedIn' job type found. Attempting to create one automatically...")

            # 2. Need an employee ID for the job owner (required field)
            try:
                emp_url = f"{WEBSITE_URL.rstrip('/')}/employees"
                emp_resp = requests.get(emp_url, headers=headers, timeout=10)
                owner_id = 1 # Default fallback
                if emp_resp.status_code == 200:
                    emps = emp_resp.json()
                    emps_list = emps if isinstance(emps, list) else emps.get("data", [])
                    if emps_list:
                        # Pick the first active employee
                        owner_id = emps_list[0]["id"]
            except:
                owner_id = 1

            # 3. Create the Job Type
            create_url = f"{WEBSITE_URL.rstrip('/')}/job-types"
            new_job_payload = {
                "unique_id": f"LNK-{datetime.now().strftime('%Y%m')}",
                "name": "Bot Linkedin Easy Apply", # UPDATED NAME
                "job_owner_id": owner_id,
                "description": "Automatically created by LinkedIn Bot to track applications.",
                "notes": "Auto-generated"
            }
            
            create_resp = requests.post(create_url, json=new_job_payload, headers=headers, timeout=10)
            if create_resp.status_code in [200, 201]:
                new_job = create_resp.json()
                _CACHED_JOB_TYPE_ID = new_job["id"]
                print_lg(f"Successfully CACHED new Job Type: {new_job.get('name')} (ID: {_CACHED_JOB_TYPE_ID})")
                return _CACHED_JOB_TYPE_ID
            else:
                print_lg(f"Failed to auto-create job type: {create_resp.text}")

            # 4. If creation failed, just use the first existing one as fallback
            if jobs:
                _CACHED_JOB_TYPE_ID = jobs[0]["id"]
                print_lg(f"Fallback: Using first available Job Type: {jobs[0].get('name')} (ID: {_CACHED_JOB_TYPE_ID})")
                return _CACHED_JOB_TYPE_ID

    except Exception as e:
        print_lg(f"Error in dynamic job ID fetch: {e}")
    
    return 1

def get_candidate_id():
    """Dynamically find a Candidate ID to use for logging using name, email, and phone, with pagination support."""
    global _CACHED_CANDIDATE_ID
    if _CACHED_CANDIDATE_ID is not None:
        return _CACHED_CANDIDATE_ID

    if not API_TOKEN: return None

    try:
        base_url = f"{WEBSITE_URL.rstrip('/')}/candidates"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        target_full_name = full_name.strip().lower()
        target_email = email.strip().lower()
        target_phone_digits = re.sub(r'\D', '', phone_number)

        # 1. Try DIRECT SEARCH by email first (high efficiency)
        try:
            search_url = f"{base_url}?search={target_email}"
            search_resp = requests.get(search_url, headers=headers, timeout=10)
            if search_resp.status_code == 200:
                s_data = search_resp.json()
                s_candidates = s_data if isinstance(s_data, list) else s_data.get("data", [])
                for cand in s_candidates:
                    if str(cand.get('email', '')).strip().lower() == target_email:
                        _CACHED_CANDIDATE_ID = cand["id"]
                        print_lg(f"✅ Found Candidate via Direct Search! (ID: {_CACHED_CANDIDATE_ID})")
                        return _CACHED_CANDIDATE_ID
        except: pass

        # 2. PAGINATED SEARCH (Tiered Matching)
        page = 1
        max_pages = 10 # Search up to 1000 candidates
        all_candidates_checked = 0
        
        while page <= max_pages:
            url = f"{base_url}?page={page}&limit=100"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 401:
                 get_api_token(force_refresh=True)
                 headers["Authorization"] = f"Bearer {API_TOKEN}"
                 response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                break

            raw_data = response.json()
            candidates = raw_data if isinstance(raw_data, list) else raw_data.get("data", [])
            
            if not candidates:
                break
                
            all_candidates_checked += len(candidates)
            print_lg(f"🔍 Searching page {page} ({len(candidates)} candidates)...")

            # Tiered matching within this page
            # a. Exact Email
            for cand in candidates:
                c_email = str(cand.get('email', '') or '').strip().lower()
                if c_email and c_email == target_email:
                    _CACHED_CANDIDATE_ID = cand["id"]
                    print_lg(f"✅ Email Match found! Using Candidate: {cand.get('full_name')} (ID: {_CACHED_CANDIDATE_ID})")
                    return _CACHED_CANDIDATE_ID

            # b. Exact Phone
            if target_phone_digits:
                for cand in candidates:
                    c_phone = str(cand.get('phone', '') or cand.get('phone_number', '') or cand.get('mobile', '') or '').strip()
                    c_phone_digits = re.sub(r'\D', '', c_phone)
                    if c_phone_digits and c_phone_digits == target_phone_digits:
                        _CACHED_CANDIDATE_ID = cand["id"]
                        print_lg(f"✅ Phone Match found! Using Candidate: {cand.get('full_name')} (ID: {_CACHED_CANDIDATE_ID})")
                        return _CACHED_CANDIDATE_ID

            # c. Exact Name
            for cand in candidates:
                c_full_name = str(cand.get('full_name', '') or '').strip().lower()
                if c_full_name == target_full_name:
                    _CACHED_CANDIDATE_ID = cand["id"]
                    print_lg(f"✅ Full Name Match found! Using Candidate: {cand.get('full_name')} (ID: {_CACHED_CANDIDATE_ID})")
                    return _CACHED_CANDIDATE_ID

            # d. Partial Name (Fuzzy)
            for cand in candidates:
                c_full_name = str(cand.get('full_name', '') or '').strip().lower()
                # Check for Sujata vs Sujatha
                if target_full_name and c_full_name:
                    if target_full_name in c_full_name or c_full_name in target_full_name:
                        _CACHED_CANDIDATE_ID = cand["id"]
                        print_lg(f"✅ Partial Name Match found! Using Candidate: {cand.get('full_name')} (ID: {_CACHED_CANDIDATE_ID})")
                        return _CACHED_CANDIDATE_ID
            
            # If we found less than 100, we're at the end
            if len(candidates) < 100:
                break
            page += 1

        print_lg(f"⚠️ Warning: No match found for '{target_full_name}' among {all_candidates_checked} profiles.")
        return None
                
    except Exception as e:
        print_lg(f"Could not fetch candidates: {e}")
    
    return None

def get_csv_summary(candidate_name, today_only=False):
    """Read the candidate's CSV and return a string of applications."""
    try:
        csv_path = f'output/{candidate_name}.csv'
        if not os.path.exists(csv_path):
            return "No local CSV history found."
            
        summary_lines = []
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        with open(csv_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts = row.get('Timestamp', '')
                # Filter for today if requested
                if today_only and not ts.startswith(today_str):
                    continue
                    
                line = f"{ts},{row.get('JobID')},{row.get('Job Title')},{row.get('Company')},{row.get('Attempted')},{row.get('Result')}"
                summary_lines.append(line)
        
        if not summary_lines:
            return f"No applications {'today' if today_only else 'found'}."
            
        return "\n".join(summary_lines)
    except Exception as e:
        return f"Error reading CSV history: {e}"


_CACHED_EMPLOYEE_ID = None
def get_employee_id():
    """Find the ID for the Employee (dynamic operator name)."""

    global _CACHED_EMPLOYEE_ID
    if _CACHED_EMPLOYEE_ID is not None:
        return _CACHED_EMPLOYEE_ID

    if not API_TOKEN: return None

    try:
        url = f"{WEBSITE_URL.rstrip('/')}/candidates"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 401:
             print_lg("Token rejected (401) in get_employee_id. Refreshing...")
             get_api_token(force_refresh=True)
             headers["Authorization"] = f"Bearer {API_TOKEN}"
             response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:

            data = response.json()
            candidates = data if isinstance(data, list) else data.get("data", [])
            
            # Look for operator specifically
            for cand in candidates:
                c_full = f"{cand.get('first_name', '')} {cand.get('last_name', '')}".lower()
                if API_OPERATOR_NAME.lower() in c_full:
                    _CACHED_EMPLOYEE_ID = cand["id"]

                    print_lg(f"✅ Employee Match found! ID: {_CACHED_EMPLOYEE_ID}")
                    return _CACHED_EMPLOYEE_ID
                    
    except Exception as e:
        print_lg(f"Could not fetch employee ID: {e}")
    
    return None

def verify_integration():
    """Run a quick connection test at startup and sync current counts."""
    print("--------------------------------------------------")
    print("🔍 INTEGRATION CHECK: Connecting to website...")
    try:
        if not API_TOKEN:
            print("❌ Error: API_TOKEN is missing!")
            return

        # We verify connection by resolving the IDs (which makes API calls)
        jid = get_job_type_id()
        cid = get_candidate_id()
        
        if jid and cid:
            eid = get_employee_id()
            print(f"✅ CONNECTION SUCCESSFUL: Linked to Website!")
            print(f"   - Job ID linked: {jid}")
            print(f"   - Candidate ID linked: {cid}")
            print(f"   - Employee ID linked: {eid}")
            
            # Smart Sync: Send the current count from local storage to website immediately
            print("   ℹ️ Syncing current counts and CSV history to dashboard...")
            c_data = load_counts()
            c_name = first_name.lower()
            c_counts = get_candidate_counts(c_name, c_data)
            
            current_total = c_counts.get("easy_applied", 0) + c_counts.get("external", 0)
            
            # Get ONLY today's CSV history for the dashboard log
            csv_summary = get_csv_summary(c_name, today_only=True)

            
            # Pass full CSV summary 
            send_activity_log(jid, datetime.now(), current_total, notes=csv_summary)
            
            print("   👉 Bot is ready and synced.")
        else:
            print(f"❌ CONNECTION FAILED: Could not fetch Job or Candidate IDs.")
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
    print("--------------------------------------------------\n")

# verify_integration() placeholder moved below send_activity_log

def send_activity_log(job_id_unused, activity_date, activity_count=1, notes="", retry_count=0):
    """
    Send activity log to website API (sync daily).
    """
    global API_TOKEN
    if not API_TOKEN:
        API_TOKEN = get_api_token()
        if not API_TOKEN:
            print_lg("No API token configured, skipping website log.")
            return

    # Check for IDs if they aren't cached yet
    real_job_id = get_job_type_id()
    real_candidate_id = get_candidate_id()
    real_employee_id = get_employee_id()
    
    if not real_job_id or not real_candidate_id:
        print_lg(f"⚠️ Skipping website sync: Missing Job ID ({real_job_id}) or Candidate ID ({real_candidate_id})")
        return


    base_url = f"{WEBSITE_URL.rstrip('/')}/job_activity_logs"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    # Use dynamic IDs
    real_job_id = get_job_type_id()
    real_candidate_id = get_candidate_id()
    real_employee_id = get_employee_id() # Added for Employee column
    
    # Ensure activity_date is a datetime/date object or string
    # Argument hint says 'activity_date' comes from datetime.now().date() usually
    if hasattr(activity_date, 'strftime'):
        date_str = activity_date.strftime('%Y-%m-%d')
    else:
        date_str = str(activity_date)

    print_lg(f"Syncing w/ website... (Job: {real_job_id}, Cand: {real_candidate_id}, Emp: {real_employee_id}, Date: {date_str})")

    try:
        # 1. GET: Check if record exists for today
        search_params = {
            "candidate_id": real_candidate_id,
            "job_id": real_job_id,
            "activity_date": date_str
        }
        
        check_resp = requests.get(base_url, params=search_params, headers=headers, timeout=10)
        existing_id = None
        existing_notes = ""
        
        if check_resp.status_code == 200:
            results = check_resp.json()
            if isinstance(results, dict):
                results = results.get('data', [])
            
            # Look for exact date and candidate match
            for log in results:
                # Use str() to be safe against different types
                if str(log.get('activity_date')) == date_str and \
                   (str(log.get('candidate_id')) == str(real_candidate_id) or str(log.get('candidate_name')) == full_name):
                    existing_id = log['id']
                    existing_notes = log.get('notes', '')
                    break

        # Prepare cumulative Notes: Smart deduplicating merge
        if existing_id and existing_notes:
            new_lines = [l.strip() for l in notes.split("\n") if l.strip()]
            old_lines = [l.strip() for l in existing_notes.split("\n") if l.strip()]
            
            # Combine and deduplicate while preserving "newest at top" order
            merged = []
            seen = set()
            for line in new_lines + old_lines:
                # Use sub-string check for rows to avoid minor timestamp-only duplicates if possible? 
                # Actually exact match is safer for CSV rows.
                if line not in seen:
                    merged.append(line)
                    seen.add(line)
            updated_notes = "\n".join(merged)
        else:
            updated_notes = notes

        if existing_id:
            # 2. PUT (Update)
            put_url = f"{base_url}/{existing_id}"
            payload = {
                "job_id": real_job_id,
                "candidate_id": real_candidate_id,
                "candidate_name": full_name,
                "employee_id": real_employee_id,
                "employee_name": API_OPERATOR_NAME,
                "activity_date": date_str,

                "activity_count": activity_count, 
                "notes": updated_notes
            }
            resp = requests.put(put_url, json=payload, headers=headers, timeout=10)
            
            if resp.status_code == 401 and retry_count == 0:
                print_lg("Token rejected (401). Retrying with fresh token...")
                API_TOKEN = get_api_token(force_refresh=True)
                return send_activity_log(job_id_unused, activity_date, activity_count, notes, retry_count=1)

            if resp.status_code in [200, 201, 204]:

                print_lg(f"✅ WEBSITE SYNC: Updated existing log (ID: {existing_id}) to count: {activity_count}")
            else:
                 print_lg(f"❌ WEBSITE ERROR: Failed to update log via PUT. Status: {resp.status_code} | {resp.text}")


        else:
            # 3. POST (Create)
            payload = {
                "job_id": real_job_id,
                "candidate_id": real_candidate_id,
                "candidate_name": full_name,
                "employee_id": real_employee_id,
                "employee_name": "Sunil Poli",
                "activity_date": date_str,
                "activity_count": activity_count,
                "notes": notes
            }
            resp = requests.post(base_url, json=payload, headers=headers, timeout=10)
            
            if resp.status_code == 401 and retry_count == 0:
                print_lg("Token rejected (401). Retrying with fresh token...")
                API_TOKEN = get_api_token(force_refresh=True)
                return send_activity_log(job_id_unused, activity_date, activity_count, notes, retry_count=1)

            if resp.status_code in [200, 201]:

                print_lg(f"✅ WEBSITE SYNC: Created NEW log for today. Count: {activity_count}")
            else:
                 print_lg(f"❌ WEBSITE ERROR: Failed to POST. Status: {resp.status_code} | {resp.text}")

    except Exception as e:
        print_lg(f"❌ NETWORK ERROR: Could not talk to website: {e}")

# Run verify at startup (moved here to avoid NameError: send_activity_log)
verify_integration()

def sync_bulk_activity_logs():
    """Combined all pending entries from global buffer and syncs to website."""
    global pending_activity_logs
    if not pending_activity_logs:
        return

    print_lg(f"🔄 Bulk syncing {len(pending_activity_logs)} logs to website dashboard...")
    
    # Calculate current total count (using persistent counts)
    c_data = load_counts()
    c_name = first_name.lower()
    c_counts = get_candidate_counts(c_name, c_data)
    current_total = c_counts.get("easy_applied", 0) + c_counts.get("external", 0)

    # Join all pending logs with newline
    bulk_notes = "\n".join(pending_activity_logs)
    
    # Send to website
    send_activity_log(get_job_type_id(), datetime.now(), current_total, notes=bulk_notes)
    
    # Clear buffer on success (assuming send_activity_log handles errors gracefully)
    pending_activity_logs = []

#>

re_experience = re.compile(r'[(]?\s*(\d+)\s*[)]?\s*[-to]*\s*\d*[+]*\s*year[s]?', re.IGNORECASE)

desired_salary_lakhs = str(round(desired_salary / 100000, 2))
desired_salary_monthly = str(round(desired_salary/12, 2))
desired_salary = str(desired_salary)

current_ctc_lakhs = str(round(current_ctc / 100000, 2))
current_ctc_monthly = str(round(current_ctc/12, 2))
current_ctc = str(current_ctc)

notice_period_months = str(notice_period//30)
notice_period_weeks = str(notice_period//7)
notice_period = str(notice_period)

aiClient = None
##> ------ Dheeraj Deshwal : dheeraj9811 Email:dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Feature ------
about_company_for_ai = None # TODO extract about company for AI
##<

#>


#< Login Functions
def is_logged_in_LN() -> bool:
    '''
    Function to check if user is logged-in in LinkedIn
    * Returns: `True` if user is logged-in or `False` if not
    '''
    if driver.current_url == "https://www.linkedin.com/feed/": return True
    if try_linkText(driver, "Sign in"): return False
    if try_xp(driver, '//button[@type="submit" and contains(text(), "Sign in")]'):  return False
    if try_linkText(driver, "Join now"): return False
    print_lg("Didn't find Sign in link, so assuming user is logged in!")
    return True


def login_LN() -> None:
    '''
    Function to login for LinkedIn
    * Tries to login using given `username` and `password` from YAML config
    * If failed, tries to login using saved LinkedIn profile button if available
    * If both failed, asks user to login manually
    '''
    # Find the username and password fields and fill them with user credentials
    driver.get("https://www.linkedin.com/login")
    try:
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        try:
            text_input_by_ID(driver, "username", username, 1)
        except Exception as e:
            print_lg("Couldn't find username field.")
            # print_lg(e)
        try:
            text_input_by_ID(driver, "password", password, 1)
        except Exception as e:
            print_lg("Couldn't find password field.")
            # print_lg(e)
        # Find the login submit button and click it
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
    except Exception as e1:
        try:
            profile_button = find_by_class(driver, "profile__details")
            profile_button.click()
        except Exception as e2:
            # print_lg(e1, e2)
            print_lg("Couldn't Login!")

    try:
        # Wait until successful redirect, indicating successful login
        wait.until(EC.url_to_be("https://www.linkedin.com/feed/")) # wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space(.)="Start a post"]')))
        return print_lg("Login successful!")
    except Exception as e:
        print_lg("Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!")
        # print_lg(e)
        manual_login_retry(is_logged_in_LN, 2)
#>



# Moved to modules/filtering.py



# Other filtering functions also moved to modules/filtering.py




def external_apply(pagination_element: WebElement, job_id: str, job_link: str, resume: str, date_listed, application_link: str, screenshot_name: str) -> tuple[bool, str, int]:
    '''
    Function to open new tab and save external job application links
    '''
    global tabs_count, dailyEasyApplyLimitReached
    if easy_apply_only:
        try:
            if "exceeded the daily application limit" in driver.find_element(By.CLASS_NAME, "artdeco-inline-feedback__message").text: dailyEasyApplyLimitReached = True
        except: pass
        print_lg("Easy apply failed I guess!")
        if pagination_element != None: return True, application_link, tabs_count
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, ".//button[contains(@class,'jobs-apply-button') and contains(@class, 'artdeco-button--3')]"))).click() # './/button[contains(span, "Apply") and not(span[contains(@class, "disabled")])]'
        wait_span_click(driver, "Continue", 1, True, False)
        windows = driver.window_handles
        tabs_count = len(windows)
        driver.switch_to.window(windows[-1])
        application_link = driver.current_url
        print_lg('Got the external application link "{}"'.format(application_link))
        if close_tabs and driver.current_window_handle != linkedIn_tab: driver.close()
        driver.switch_to.window(linkedIn_tab)
        return False, application_link, tabs_count
    except Exception as e:
        # print_lg(e)
        print_lg("Failed to apply!")
        failed_job(job_id, job_link, resume, date_listed, "Probably didn't find Apply button or unable to switch tabs.", e, application_link, screenshot_name)
        global failed_count
        failed_count += 1
        return True, application_link, tabs_count



def follow_company(modal: WebDriver) -> None:
    '''
    Function to follow or un-follow easy applied companies based om `follow_companies`
    '''
    try:
        follow_checkbox_input = try_xp(modal, ".//input[@id='follow-company-checkbox' and @type='checkbox']", False)
        if follow_checkbox_input and follow_checkbox_input.is_selected() != follow_companies:
            try_xp(modal, ".//label[@for='follow-company-checkbox']")
    except Exception as e:
        print_lg("Failed to update follow companies checkbox!", e)
    


#< Failed attempts logging
# In runAiBot.py, replace the existing failed_job function with this one

def failed_job(job_id: str, title: str, company: str, job_link: str, resume: str, date_listed, reason: str, exception: Exception, application_link: str, screenshot_name: str) -> None:
    '''
    Function to log failed or skipped job applications to the candidate-specific CSV file.
    The new format is: Timestamp | JobID | Job Title | Company | Attempted | Result
    '''
    try:
        # --- NEW: Define the new CSV format and file path ---
        candidate_name = f"{first_name.lower()}"
        output_dir = 'output'
        csv_path = f'{output_dir}/{candidate_name}.csv'
        
        fieldnames = ['Timestamp', 'JobID', 'Job Title', 'Company', 'Attempted', 'Result']
        
        make_directories([output_dir])
        
        # New Entry
        new_row = {
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'JobID': truncate_for_csv(job_id),
            'Job Title': truncate_for_csv(title),
            'Company': truncate_for_csv(company),
            'Attempted': 'N/A', 
            'Result': f'Failed: {reason}'
        }

        # Read existing rows to prepend
        existing_rows = []
        if os.path.exists(csv_path):
            with open(csv_path, mode='r', newline='', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                existing_rows = list(reader)

        # Write header + new_row + existing_rows (Newest First)
        with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(new_row)
            writer.writerows(existing_rows)
        
        print_lg(f"❌ Logged failure to '{candidate_name}.csv' for job: {title} at {company}")
        
        # Queue failure for bulk sync to website
        csv_line = f"{new_row['Timestamp']},{job_id},{title},{company},Attempted: {application_link},Result: Failed: {reason}"
        pending_activity_logs.append(csv_line)

    except Exception as e:

        print_lg("Failed to update the new candidate CSV file for failed job!", e)


def screenshot(driver: WebDriver, job_id: str, failedAt: str) -> str:
    '''
    Function to to take screenshot for debugging
    - Returns screenshot name as String
    '''
    screenshot_name = "{} - {} - {}.png".format( job_id, failedAt, str(datetime.now()) )
    path = logs_folder_path+"/screenshots/"+screenshot_name.replace(":",".")
    # special_chars = {'*', '"', '\\', '<', '>', ':', '|', '?'}
    # for char in special_chars:  path = path.replace(char, '-')
    driver.save_screenshot(path.replace("//","/"))
    return screenshot_name
#>



# In runAiBot.py, replace the existing submitted_jobs function with this one

def submitted_jobs(job_id: str, title: str, company: str, work_location: str, work_style: str, description: str, experience_required: int | Literal['Unknown', 'Error in extraction'], 
                   skills: list[str] | Literal['In Development'], hr_name: str | Literal['Unknown'], hr_link: str | Literal['Unknown'], resume: str, 
                   reposted: bool, date_listed: datetime | Literal['Unknown'], date_applied:  datetime | Literal['Pending'], job_link: str, application_link: str, 
                   questions_list: set | None, connect_request: Literal['In Development']) -> None:
    '''
    Function to create or update a candidate-specific CSV file for successful applications.
    The new format is: Timestamp | JobID | Job Title | Company | Attempted | Result
    '''
    try:
        # --- NEW: Define the new CSV format and file path ---
        # The file will be named based on the candidate's first name from YAML config
        candidate_name = f"{first_name.lower()}" 
        output_dir = 'output'
        csv_path = f'{output_dir}/{candidate_name}.csv'
        
        # Define the headers for our new, simpler CSV format
        fieldnames = ['Timestamp', 'JobID', 'Job Title', 'Company', 'Attempted', 'Result']

        # Ensure the output directory exists
        make_directories([output_dir])

        # New Entry
        new_row = {
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'JobID': truncate_for_csv(job_id),
            'Job Title': truncate_for_csv(title),
            'Company': truncate_for_csv(company),
            'Attempted': 'Easy Apply' if application_link == "Easy Applied" else 'External',
            'Result': 'Success'
        }

        # Read existing rows to prepend
        existing_rows = []
        if os.path.exists(csv_path):
            with open(csv_path, mode='r', newline='', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                existing_rows = list(reader)

        # Write header + new_row + existing_rows (Newest First)
        with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(new_row)
            writer.writerows(existing_rows)
        
        print_lg(f"✅ Successfully logged to '{candidate_name}.csv' for job: {title} at {company}")
        
        # Website sync is now handled in the main apply_to_jobs loop after count increment!

    except Exception as e:
        print_lg("Failed to update the new candidate CSV file!", e)
        # Optional: Show an alert if logging fails
        # pyautogui.alert(f"Failed to write to {csv_path}!\n\nError: {e}", "CSV Logging Error")


# Function to discard the job application
def discard_job() -> None:
    actions.send_keys(Keys.ESCAPE).perform()
    wait_span_click(driver, 'Discard', 2)






# Function to apply to jobs
def apply_to_jobs(search_terms: list[str]) -> None:
    applied_jobs = get_applied_job_ids(file_name)
    rejected_jobs = set()
    blacklisted_companies = set()
    global current_city, failed_count, skip_count, easy_applied_count, external_jobs_count, tabs_count, pause_before_submit, pause_at_failed_question, useNewResume
    current_city = current_city.strip()

    if randomize_search_order:  shuffle(search_terms)
    if randomize_search_order:  shuffle(search_terms)
    for searchTerm in search_terms:
        # Pre-apply filters via URL parameters to avoid clicking them every time
        # f_AL=true -> Easy Apply
        # f_WT=1,2,3 -> Work Type (1=On-site, 2=Remote, 3=Hybrid)
        # f_TPR=r604800 -> Date Posted (r604800 = Past week, r86400 = Past 24h)
        # geoId=103644278 -> United States (approx) or use location text
        
        base_url = f"https://www.linkedin.com/jobs/search/?keywords={searchTerm}"
        
        # Add Easy Apply filter
        base_url += "&f_AL=true"
        
        # Add Work Type filter based on logic (assuming user wants Remote/Hybrid if configured, or just default)
        # Note: Mapping specific config to URL params is complex, but we can add standard ones
        # Use existing 'apply_filters' logic which clicks buttons effectively, 
        # BUT the user asked to not click every time.
        # Compromise: We add 'f_AL=true' which is the most critical one.
        
        try:
            driver.get(base_url)
            print_lg("\n________________________________________________________________________________________________________________________\n")
            print_lg(f'\n>>>> Now searching for "{searchTerm}" <<<<\n\n')

            apply_filters(driver, wait, actions, cfg) # Still needed for complex filters like 'Remote' specifically if URL param isn't perfect

            current_count = 0
            while current_count < switch_number:
                try:
                    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[@data-occludable-job-id]")))

                    pagination_element, current_page = get_page_info(driver)

                    # Find all job listings in current page
                    buffer(3)
                    job_listings = driver.find_elements(By.XPATH, "//li[@data-occludable-job-id]")  

                
                    for job in job_listings:
                        if keep_screen_awake: pyautogui.press('shiftright')
                        if current_count >= switch_number: break
                        print_lg("\n-@-\n")

                        job_id,title,company,work_location,work_style,skip = get_job_main_details(driver, job, blacklisted_companies, rejected_jobs, click_gap)
                        
                        if skip: continue
                        # Redundant fail safe check for applied jobs!
                        try:
                            if job_id in applied_jobs or find_by_class(driver, "jobs-s-apply__application-link", 2):
                                print_lg(f'Already applied to "{title} | {company}" job. Job ID: {job_id}!')
                                continue
                        except Exception as e:
                            print_lg(f'Trying to Apply to "{title} | {company}" job. Job ID: {job_id}')

                        job_link = "https://www.linkedin.com/jobs/view/"+job_id
                        application_link = "Easy Applied"
                        date_applied = "Pending"
                        hr_link = "Unknown"
                        hr_name = "Unknown"
                        connect_request = "In Development" # Still in development
                        date_listed = "Unknown"
                        skills = "Needs an AI" # Still in development
                        resume = "Pending"
                        reposted = False
                        questions_list = None
                        screenshot_name = "Not Available"

                        jobs_top_card = None
                        try:
                            rejected_jobs, blacklisted_companies, jobs_top_card = check_blacklist(driver, rejected_jobs,job_id,company,blacklisted_companies, about_company_good_words, about_company_bad_words, click_gap)
                        except ValueError as e:
                            print_lg(e, 'Skipping this job!\n')
                            failed_job(job_id, title, company, job_link, resume, date_listed, "Found Blacklisted words in About Company", e, "Skipped", screenshot_name)
                            skip_count += 1
                            continue
                        except Exception as e:
                            print_lg(f"Warning: Failed to check blacklist or find job card for Job ID {job_id}. Continuing with limited info.")
                            # Ensure jobs_top_card is at least None if it was already None, but it should be assigned correctly by returning None from check_blacklist now.
                            # We don't need to do anything here as check_blacklist now returns instead of raising.



                        # Hiring Manager info
                        try:
                            hr_info_card = WebDriverWait(driver,2).until(EC.presence_of_element_located((By.CLASS_NAME, "hirer-card__hirer-information")))
                            hr_link = hr_info_card.find_element(By.TAG_NAME, "a").get_attribute("href")
                            hr_name = hr_info_card.find_element(By.TAG_NAME, "span").text
                        except Exception as e:
                            print_lg(f'HR info was not given for "{title}" with Job ID: {job_id}!')


                        # Calculation of date posted
                        try:
                            if jobs_top_card:
                                time_posted_text = jobs_top_card.find_element(By.XPATH, './/span[contains(normalize-space(), " ago")]').text
                                print("Time Posted: " + time_posted_text)
                                if time_posted_text.__contains__("Reposted"):
                                    reposted = True
                                    time_posted_text = time_posted_text.replace("Reposted", "")
                                date_listed = calculate_date_posted(time_posted_text.strip())
                            else:
                                print_lg("Skipping date calculation as Job Card was not found.")
                        except Exception as e:
                            print_lg("Failed to calculate the date posted!",e)
                            date_listed = "Unknown"


                        description, experience_required, skip, reason, message = get_job_description(driver, cfg)
                        if skip:
                            print_lg(message)
                            failed_job(job_id, title, company, job_link, resume, date_listed, reason, message, "Skipped", screenshot_name)
                            rejected_jobs.add(job_id)
                            skip_count += 1
                            continue

                        
                        if use_AI and description != "Unknown":
                            ##> ------ Yang Li : MARKYangL - Feature ------
                            try:
                                if ai_provider.lower() == "openai":
                                    skills = ai_extract_skills(aiClient, description)
                                elif ai_provider.lower() == "deepseek":
                                    skills = deepseek_extract_skills(aiClient, description)
                                elif ai_provider.lower() == "gemini":
                                    skills = gemini_extract_skills(aiClient, description)
                                else:
                                    skills = "In Development"
                                print_lg(f"Extracted skills using {ai_provider} AI")
                            except Exception as e:
                                print_lg("Failed to extract skills:", e)
                                skills = "Error extracting skills"
                            ##<

                        uploaded = False
                        # Case 1: Easy Apply Button
                        if try_xp(driver, ".//button[contains(@class,'jobs-apply-button') and contains(@class, 'artdeco-button--3') and contains(@aria-label, 'Easy')]"):
                            try: 
                                try:
                                    errored = ""
                                    modal = find_by_class(driver, "jobs-easy-apply-modal")
                                    wait_span_click(modal, "Next", 1)
                                    # if description != "Unknown":
                                    #     resume = create_custom_resume(description)
                                    resume = "Previous resume"
                                    next_button = True
                                    questions_list = set()
                                    next_counter = 0
                                    while next_button:
                                        next_counter += 1
                                        if next_counter >= 15: 
                                            if pause_at_failed_question:
                                                screenshot(driver, job_id, "Needed manual intervention for failed question")
                                                pyautogui.alert("Couldn't answer one or more questions.\nPlease click \"Continue\" once done.\nDO NOT CLICK Back, Next or Review button in LinkedIn.\n\n\n\n\nYou can turn off \"Pause at failed question\" setting in config.yaml\nTo TEMPORARILY disable pausing, click \"Disable Pause\"", "Help Needed", "Continue")
                                                next_counter = 1
                                                continue
                                            if questions_list: print_lg("Stuck for one or some of the following questions...", questions_list)
                                            screenshot_name = screenshot(driver, job_id, "Failed at questions")
                                            errored = "stuck"
                                            raise Exception("Seems like stuck in a continuous loop of next, probably because of new questions.")
                                        questions_list = answer_questions(driver, actions, modal, questions_list, work_location, job_description=description, config_vars=cfg, ai_client=aiClient, randomly_answered_questions=randomly_answered_questions)
                                        if useNewResume and not uploaded: uploaded, resume = upload_resume(modal, default_resume_path)
                                        try: 
                                            next_button = modal.find_element(By.XPATH, './/span[contains(translate(normalize-space(.), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "review")]') 
                                        except NoSuchElementException:  next_button = modal.find_element(By.XPATH, './/button[contains(span, "Next")]')
                                        try: next_button.click()
                                        except ElementClickInterceptedException: break    # Happens when it tries to click Next button in About Company photos section
                                        buffer(click_gap)

                                except NoSuchElementException: errored = "nose"
                                finally:
                                    if questions_list and errored != "stuck": 
                                        print_lg("Answered the following questions...", questions_list)
                                        print("\n\n" + "\n".join(str(question) for question in questions_list) + "\n\n")
                                    wait_span_click(driver, "Review", 1, scrollTop=True)
                                    cur_pause_before_submit = pause_before_submit
                                    if errored != "stuck" and cur_pause_before_submit:
                                        decision = pyautogui.confirm('1. Please verify your information.\n2. If you edited something, please return to this final screen.\n3. DO NOT CLICK "Submit Application".\n\n\n\n\nYou can turn off "Pause before submit" setting in config.yaml\nTo TEMPORARILY disable pausing, click "Disable Pause"', "Confirm your information",["Disable Pause", "Discard Application", "Submit Application"])
                                        if decision == "Discard Application": raise Exception("Job application discarded by user!")
                                        pause_before_submit = False if "Disable Pause" == decision else True
                                        # try_xp(modal, ".//span[normalize-space(.)='Review']")
                                    follow_company(modal)
                                    if wait_span_click(driver, "Submit application", 2, scrollTop=True): 
                                        date_applied = datetime.now()
                                        if not wait_span_click(driver, "Done", 2): actions.send_keys(Keys.ESCAPE).perform()
                                    elif errored != "stuck" and cur_pause_before_submit and "Yes" in pyautogui.confirm("You submitted the application, didn't you 😒?", "Failed to find Submit Application!", ["Yes", "No"]):
                                        date_applied = datetime.now()
                                        # wait_span_click(driver, "Done", 2)
                                        pass
                                    else:
                                        print_lg("Since, Submit Application failed, discarding the job application...")
                                        # if screenshot_name == "Not Available":  screenshot_name = screenshot(driver, job_id, "Failed to click Submit application")
                                        # else:   screenshot_name = [screenshot_name, screenshot(driver, job_id, "Failed to click Submit application")]
                                        if errored == "nose": raise Exception("Failed to click Submit application 😑")


                            except Exception as e:
                                print_lg("Failed to Easy apply!")
                                # print_lg(e)
                                critical_error_log("Somewhere in Easy Apply process",e)
                                failed_job(job_id, title, company, job_link, resume, date_listed, "Problem in Easy Applying", e, application_link, screenshot_name)
                                failed_count += 1
                                discard_job()
                                continue
                        else:
                            # Case 2: Apply externally
                            skip, application_link, tabs_count = external_apply(pagination_element, job_id, job_link, resume, date_listed, application_link, screenshot_name)
                            if dailyEasyApplyLimitReached:
                                print_lg("\n###############  Daily application limit for Easy Apply is reached!  ###############\n")
                                return
                            if skip: continue

                        submitted_jobs(job_id, title, company, work_location, work_style, description, experience_required, skills, hr_name, hr_link, resume, reposted, date_listed, date_applied, job_link, application_link, questions_list, connect_request)
                        if uploaded:   useNewResume = False

                        print_lg(f'Successfully saved "{title} | {company}" job. Job ID: {job_id} info')
                        current_count += 1
                        if application_link == "Easy Applied":
                            easy_applied_count += 1
                            update_candidate_count(first_name.lower(), "easy_applied", counts_data)
                            
                            # Prepare CSV line for Website Notes (Comma separated as requested)
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            csv_line = f"{timestamp},{job_id},{title},{company},Easy Apply,Success"
                            
                            # Queue for bulk sync instead of immediate send
                            pending_activity_logs.append(csv_line)


                        else:   
                            external_jobs_count += 1
                            update_candidate_count(first_name.lower(), "external", counts_data)

                            # Prepare CSV line for Website Notes (Comma separated as requested)
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            csv_line = f"{timestamp},{job_id},{title},{company},External,Success"

                            # Queue for bulk sync instead of immediate send
                            pending_activity_logs.append(csv_line)

                        applied_jobs.add(job_id)



                    # Switching to next page
                    if pagination_element == None:
                        print_lg("Couldn't find pagination element, probably at the end page of results!")
                        break
                    try:
                        pagination_element.find_element(By.XPATH, f"//button[@aria-label='Page {current_page+1}']").click()
                        print_lg(f"\n>-> Now on Page {current_page+1} \n")
                    except NoSuchElementException:
                        print_lg(f"\n>-> Didn't find Page {current_page+1}. Probably at the end page of results!\n")
                        break

                except StaleElementReferenceException:
                    print_lg("Encountered stale element reference. Refreshing job listings...")
                    buffer(2)
                    continue
                except (NoSuchWindowException, WebDriverException) as e:
                    print_lg("Browser window closed or session is invalid. Ending application process.", e)
                    raise e # Re-raise to be caught by main
                except Exception as e:
                    print_lg("An unexpected error occurred in the job loop. Continuing to next keyword...")
                    critical_error_log("In Applier Keyword Job Loop", e)
                    break # Exit while loop to move to next keyword
        except (NoSuchWindowException, WebDriverException) as e:
            raise e
        except Exception as e:
            print_lg(f"Failed to process keyword '{searchTerm}'! Error: {e}")
            critical_error_log("In Applier Search Loop", e)
            continue # Move to next searchTerm
        finally:
            # Sync logs after each search term
            try:
                sync_bulk_activity_logs()
            except Exception as e:
                print_lg(f"Failed periodic sync for {searchTerm}: {e}")


        
def run(total_runs: int) -> int:
    if dailyEasyApplyLimitReached:
        return total_runs
    print_lg("\n########################################################################################################################\n")
    print_lg(f"Date and Time: {datetime.now()}")
    print_lg(f"Cycle number: {total_runs}")
    print_lg(f"Currently looking for jobs posted within '{date_posted}' and sorting them by '{sort_by}'")
    apply_to_jobs(search_terms)
    print_lg("########################################################################################################################\n")
    if not dailyEasyApplyLimitReached:
        print_lg("Sleeping for 10 min...")
        sleep(300)
        print_lg("Few more min... Gonna start with in next 5 min...")
        sleep(300)
    buffer(3)
    return total_runs + 1



chatGPT_tab = False
linkedIn_tab = False

def main() -> None:
    global driver, wait, actions, counts_data
    # Load persistent counts
    counts_data = load_counts()
    candidate_name = f"{first_name.lower()}"
    candidate_counts = get_candidate_counts(candidate_name, counts_data)
    global easy_applied_count, external_jobs_count, failed_count, skip_count
    easy_applied_count = candidate_counts["easy_applied"]
    external_jobs_count = candidate_counts["external"]
    failed_count = candidate_counts["failed"]
    skip_count = candidate_counts["skipped"]

    # Create Chrome driver
    options = webdriver.ChromeOptions()
    if run_in_background:
        options.add_argument("--headless")
    if disable_extensions:
        options.add_argument("--disable-extensions")
    if safe_mode:
        options.add_argument("--incognito")
    user_data_dir = find_default_profile_directory()
    if user_data_dir and not safe_mode:
        options.add_argument(f"--user-data-dir={user_data_dir}")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    try:
        global linkedIn_tab, tabs_count, useNewResume, aiClient
        alert_title = "Error Occurred. Closing Browser!"
        total_runs = 1
        
        # Validate configuration
        if not os.path.exists(default_resume_path):
            pyautogui.alert(text='Your default resume "{}" is missing! Please update it\'s folder path "default_resume_path" in config.yaml\n\nOR\n\nAdd a resume with exact name and path (check for spelling mistakes including cases).\n\n\nFor now the bot will continue using your previous upload from LinkedIn!'.format(default_resume_path), title="Missing Resume", button="OK")
            useNewResume = False
        
        # Login to LinkedIn
        tabs_count = len(driver.window_handles)
        driver.get("https://www.linkedin.com/login")
        if not is_logged_in_LN(): login_LN()
        
        linkedIn_tab = driver.current_window_handle

        # # Login to ChatGPT in a new tab for resume customization
        # if use_resume_generator:
        #     try:
        #         driver.switch_to.new_window('tab')
        #         driver.get("https://chat.openai.com/")
        #         if not is_logged_in_GPT(): login_GPT()
        #         open_resume_chat()
        #         global chatGPT_tab
        #         chatGPT_tab = driver.current_window_handle
        #     except Exception as e:
        #         print_lg("Opening OpenAI chatGPT tab failed!")
        if use_AI:
            if ai_provider == "openai":
                aiClient = ai_create_openai_client()
            ##> ------ Yang Li : MARKYangL - Feature ------
            # Create DeepSeek client
            elif ai_provider == "deepseek":
                aiClient = deepseek_create_client()
            elif ai_provider == "gemini":
                aiClient = gemini_create_client()
            ##<

            try:
                about_company_for_ai = " ".join([word for word in (first_name+" "+last_name).split() if len(word) > 3])
                print_lg(f"Extracted about company info for AI: '{about_company_for_ai}'")
            except Exception as e:
                print_lg("Failed to extract about company info!", e)
        
        # Start applying to jobs
        driver.switch_to.window(linkedIn_tab)
        total_runs = run(total_runs)
        while(run_non_stop):
            if cycle_date_posted:
                date_options = ["Past 24 hours", "Past week", "Past month", "Any time"]
                global date_posted
                date_posted = date_options[date_options.index(date_posted)+1 if date_options.index(date_posted)+1 > len(date_options) else -1] if stop_date_cycle_at_24hr else date_options[0 if date_options.index(date_posted)+1 >= len(date_options) else date_options.index(date_posted)+1]
            if alternate_sortby:
                global sort_by
                sort_by = "Most recent" if sort_by == "Most relevant" else "Most relevant"
                total_runs = run(total_runs)
                sort_by = "Most recent" if sort_by == "Most relevant" else "Most relevant"
            total_runs = run(total_runs)
            if dailyEasyApplyLimitReached:
                break
        

    except (NoSuchWindowException, WebDriverException) as e:
        print_lg("Browser window closed or session is invalid. Exiting.", e)
    except Exception as e:
        critical_error_log("In Applier Main", e)
        pyautogui.alert(e,alert_title)
    finally:
        # Final Bulk Sync before exit
        try:
            sync_bulk_activity_logs()
        except Exception as e:
            print_lg(f"Failed final sync: {e}")

        print_lg("\n\nTotal runs:                     {}".format(total_runs))
        print_lg("Jobs Easy Applied:              {}".format(easy_applied_count))
        print_lg("External job links collected:   {}".format(external_jobs_count))
        print_lg("                              ----------")
        print_lg("Total applied or collected:     {}".format(easy_applied_count + external_jobs_count))
        print_lg("\nFailed jobs:                    {}".format(failed_count))
        print_lg("Irrelevant jobs skipped:        {}\n".format(skip_count))
        if randomly_answered_questions: print_lg("\n\nQuestions randomly answered:\n  {}  \n\n".format(";\n".join(str(question) for question in randomly_answered_questions)))
        quote = choice([
            "You're one step closer than before.", 
            "All the best with your future interviews.", 
            "Keep up with the progress. You got this.", 
            "If you're tired, learn to take rest but never give up.",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
            "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson",
            "Every job is a self-portrait of the person who does it. Autograph your work with excellence.",
            "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. - Steve Jobs",
            "Opportunities don't happen, you create them. - Chris Grosser",
            "The road to success and the road to failure are almost exactly the same. The difference is perseverance.",
            "Obstacles are those frightful things you see when you take your eyes off your goal. - Henry Ford",
            "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt"
            ])
        msg = f"\n{quote}\n\n\nBest regards,\nSai Vignesh Golla\nhttps://www.linkedin.com/in/saivigneshgolla/\n\n"
        pyautogui.alert(msg, "Exiting..")
        print_lg(msg,"Closing the browser...")
        if tabs_count >= 10:
            msg = "NOTE: IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM!\n\nOr it's highly likely that application will just open browser and not do anything next time!" 
            pyautogui.alert(msg,"Info")
            print_lg("\n"+msg)
        ##> ------ Yang Li : MARKYangL - Feature ------
        if use_AI and aiClient:
            try:
                if ai_provider.lower() == "openai":
                    ai_close_openai_client(aiClient)
                elif ai_provider.lower() == "deepseek":
                    ai_close_openai_client(aiClient)
                elif ai_provider.lower() == "gemini":
                    pass # Gemini client does not need to be closed
                print_lg(f"Closed {ai_provider} AI client.")
            except Exception as e:
                print_lg("Failed to close AI client:", e)
        ##<
        # Save final counts
        candidate_name = f"{first_name.lower()}"
        get_candidate_counts(candidate_name, counts_data).update({
            "easy_applied": easy_applied_count,
            "external": external_jobs_count,
            "failed": failed_count,
            "skipped": skip_count
        })
        save_counts(counts_data)
        try:
            if driver:
                driver.quit()
        except WebDriverException as e:
            print_lg("Browser already closed.", e)
        except Exception as e:
            critical_error_log("When quitting...", e)


if __name__ == "__main__":
    main()
