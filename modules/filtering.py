import os
import re
import csv
import pyautogui
from time import sleep
from random import randint
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from modules.helpers import print_lg, buffer
from modules.clickers_and_finders import (
    wait_span_click, multi_sel_noWait, boolean_button_click, 
    scroll_to_view, try_xp, try_find_by_classes, find_by_class, text_input
)
from modules.ai.openaiConnections import ai_answer_question
from modules.ai.deepseekConnections import deepseek_answer_question
from modules.ai.geminiConnections import gemini_answer_question

# RegEx for experience extraction
re_experience = re.compile(r'[(]?\s*(\d+)\s*[)]?\\s*[-to]*\s*\d*[+]*\s*year[s]?', re.IGNORECASE)

def get_applied_job_ids(file_name: str) -> set:
    '''
    Function to get a `set` of applied job's Job IDs
    * Returns a set of Job IDs from existing applied jobs history csv file
    '''
    job_ids = set()
    try:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        job_ids.add(row[0])
    except Exception as e:
        print_lg(f"Error reading applied jobs history: {e}")
    return job_ids

def set_search_location(driver, actions, search_location) -> None:
    '''
    Function to set search location
    '''
    if search_location.strip():
        try:
            print_lg(f'Setting search location as: "{search_location.strip()}"')
            search_location_ele = try_xp(driver, ".//input[@aria-label='City, state, or zip code' and not(@disabled)]", False)
            if not search_location_ele:
                 search_location_ele = try_xp(driver, ".//input[contains(@placeholder, 'Location')]", False)
            if not search_location_ele:
                 search_location_ele = try_xp(driver, ".//input[contains(@id, 'jobs-search-box-location')]", False)
            
            text_input(actions, search_location_ele, search_location, "Search Location")
        except ElementNotInteractableException:
            try_xp(driver, ".//label[@class='jobs-search-box__input-icon jobs-search-box__keywords-label']")
            actions.send_keys(Keys.TAB, Keys.TAB).perform()
            actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            actions.send_keys(search_location.strip()).perform()
            sleep(2)
            actions.send_keys(Keys.ENTER).perform()
            try_xp(driver, ".//button[@aria-label='Cancel']")
        except Exception as e:
            try_xp(driver, ".//button[@aria-label='Cancel']")
            print_lg("Failed to update search location, continuing with default location!", e)

def apply_filters(driver, wait, actions, config_vars) -> None:
    '''
    Function to apply job search filters
    '''
    set_search_location(driver, actions, config_vars.get('search_location', ''))

    try:
        click_gap = config_vars.get('click_gap', 5)
        recommended_wait = 1 if click_gap < 1 else 0

        # Try to find and click "All filters" button
        all_filters_xpath = '//button[contains(translate(normalize-space(.), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "all filters")]'
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, all_filters_xpath))).click()
        except:
             wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(., "filters")]'))).click()
             
        buffer(recommended_wait)

        wait_span_click(driver, config_vars.get('sort_by'))
        wait_span_click(driver, config_vars.get('date_posted'))
        buffer(recommended_wait)

        multi_sel_noWait(driver, config_vars.get('experience_level', [])) 
        multi_sel_noWait(driver, config_vars.get('companies', []), actions)
        if config_vars.get('experience_level') or config_vars.get('companies'): buffer(recommended_wait)

        multi_sel_noWait(driver, config_vars.get('job_type', []))
        multi_sel_noWait(driver, config_vars.get('on_site', []))
        if config_vars.get('job_type') or config_vars.get('on_site'): buffer(recommended_wait)

        multi_sel_noWait(driver, config_vars.get('location', []))
        multi_sel_noWait(driver, config_vars.get('industry', []))
        if config_vars.get('location') or config_vars.get('industry'): buffer(recommended_wait)

        multi_sel_noWait(driver, config_vars.get('job_function', []))
        multi_sel_noWait(driver, config_vars.get('job_titles', []))
        if config_vars.get('job_function') or config_vars.get('job_titles'): buffer(recommended_wait)

        if config_vars.get('under_10_applicants'): boolean_button_click(driver, actions, "Under 10 applicants")
        if config_vars.get('in_your_network'): boolean_button_click(driver, actions, "In your network")
        if config_vars.get('fair_chance_employer'): boolean_button_click(driver, actions, "Fair Chance Employer")

        wait_span_click(driver, config_vars.get('salary'))
        buffer(recommended_wait)
        
        multi_sel_noWait(driver, config_vars.get('benefits', []))
        multi_sel_noWait(driver, config_vars.get('commitments', []))
        if config_vars.get('benefits') or config_vars.get('commitments'): buffer(recommended_wait)

        # Click "Show results"
        try:
            show_results_button: WebElement = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Apply current filters to show") or contains(., "Show results")]')))
            show_results_button.click()
        except:
            try_xp(driver, '//div[@role="dialog"]//button[@type="submit"]')
            try_xp(driver, '//button[contains(@class, "search-reusables__filter-pull-button")]')

    except Exception as e:
        print_lg(f"Setting the preferences failed! Error: {e}")
        try:
            dismiss_button = driver.find_element(By.XPATH, '//button[@aria-label="Dismiss" or @aria-label="Close"]')
            dismiss_button.click()
        except:
            pass

def get_page_info(driver) -> tuple[WebElement | None, int | None]:
    '''
    Function to get pagination element and current page number
    '''
    try:
        pagination_element = try_find_by_classes(driver, ["jobs-search-pagination__pages", "artdeco-pagination", "artdeco-pagination__pages"])
        scroll_to_view(driver, pagination_element)
        current_page = int(pagination_element.find_element(By.XPATH, "//button[contains(@class, 'active')]").text)
    except Exception as e:
        print_lg("Failed to find Pagination element, hence couldn't scroll till end!")
        pagination_element = None
        current_page = None
    return pagination_element, current_page

def get_job_main_details(driver, job: WebElement, blacklisted_companies: set, rejected_jobs: set, click_gap: int = 5) -> tuple[str, str, str, str, str, bool]:
    '''
    # Function to get job main details.
    Returns a tuple of (job_id, title, company, work_location, work_style, skip)
    '''
    job_details_button = job.find_element(By.TAG_NAME, 'a')
    scroll_to_view(driver, job_details_button, True)
    job_id = job.get_dom_attribute('data-occludable-job-id')
    title = job_details_button.text
    title = title[:title.find("\n")]
    
    other_details = job.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__subtitle').text
    index = other_details.find(' · ')
    company = other_details[:index]
    work_location = other_details[index+3:]
    work_style = work_location[work_location.rfind('(')+1:work_location.rfind(')')]
    work_location = work_location[:work_location.rfind('(')].strip()
    
    skip = False
    if company in blacklisted_companies:
        print_lg(f'Skipping "{title} | {company}" job (Blacklisted Company). Job ID: {job_id}!')
        skip = True
    elif job_id in rejected_jobs: 
        print_lg(f'Skipping previously rejected "{title} | {company}" job. Job ID: {job_id}!')
        skip = True
    try:
        if job.find_element(By.CLASS_NAME, "job-card-container__footer-job-state").text == "Applied":
            skip = True
            print_lg(f'Already applied to "{title} | {company}" job. Job ID: {job_id}!')
    except: pass
    
    try: 
        if not skip: job_details_button.click()
    except Exception as e:
        print_lg(f'Failed to click "{title} | {company}" job on details button. Job ID: {job_id}!') 
        # Note: discard_job() should be called by the caller
        job_details_button.click() # To pass the error outside
        
    buffer(click_gap)
    return (job_id, title, company, work_location, work_style, skip)

def check_blacklist(driver, rejected_jobs: set, job_id: str, company: str, blacklisted_companies: set, about_company_good_words: list, about_company_bad_words: list, click_gap: int = 5) -> tuple[set, set, WebElement | None]:
    try:
        jobs_top_card = try_find_by_classes(driver, ["job-details-jobs-unified-top-card__primary-description-container","job-details-jobs-unified-top-card__primary-description","jobs-unified-top-card__primary-description","jobs-details__main-content"])
    except:
        jobs_top_card = None

    try:
        about_company_org_ele = find_by_class(driver, "jobs-company__box", 2)
        scroll_to_view(driver, about_company_org_ele)
        about_company_org = about_company_org_ele.text
    except Exception as e:
        return rejected_jobs, blacklisted_companies, jobs_top_card
        
    about_company = about_company_org.lower()
    skip_checking = False
    for word in about_company_good_words:
        if word.lower() in about_company:
            print_lg(f'Found the word "{word}". So, skipped checking for blacklist words.')
            skip_checking = True
            break
            
    if not skip_checking:
        for word in about_company_bad_words: 
            if word.lower() in about_company: 
                rejected_jobs.add(job_id)
                blacklisted_companies.add(company)
                raise ValueError(f'\n"{about_company_org}"\n\nContains "{word}".')
                
    buffer(click_gap)
    if jobs_top_card:
        try: scroll_to_view(driver, jobs_top_card)
        except: pass
    return rejected_jobs, blacklisted_companies, jobs_top_card

def extract_years_of_experience(text: str) -> int:
    matches = re.findall(re_experience, text)
    if len(matches) == 0: 
        print_lg(f'\n{text}\n\nCouldn\'t find experience requirement in About the Job!')
        return 0
    return max([int(match) for match in matches if int(match) <= 12])

def get_job_description(driver, config_vars) -> tuple[str, int | str, bool, str | None, str | None]:
    '''
    Function to extract job description and validate filters
    '''
    try:
        jobDescription = "Unknown"
        experience_required = "Unknown"
        found_masters = 0
        jobDescription = find_by_class(driver, "jobs-box__html-content").text
        jobDescriptionLow = jobDescription.lower()
        skip = False
        skipReason = None
        skipMessage = None
        
        bad_words = config_vars.get('bad_words', [])
        for word in bad_words:
            if word.lower() in jobDescriptionLow:
                skipMessage = f'\n{jobDescription}\n\nContains bad word "{word}". Skipping this job!\n'
                skipReason = "Found a Bad Word in About Job"
                skip = True
                break
                
        if not skip and config_vars.get('security_clearance') == False and ('polygraph' in jobDescriptionLow or 'clearance' in jobDescriptionLow or 'secret' in jobDescriptionLow):
            skipMessage = f'\n{jobDescription}\n\nFound "Clearance" or "Polygraph". Skipping this job!\n'
            skipReason = "Asking for Security clearance"
            skip = True
            
        if not skip:
            if config_vars.get('did_masters') and 'master' in jobDescriptionLow:
                print_lg(f'Found the word "master" in \n{jobDescription}')
                found_masters = 2
            experience_required = extract_years_of_experience(jobDescription)
            current_experience = config_vars.get('current_experience', -1)
            if current_experience > -1 and experience_required > current_experience + found_masters:
                skipMessage = f'\n{jobDescription}\n\nExperience required {experience_required} > Current Experience {current_experience + found_masters}. Skipping this job!\n'
                skipReason = "Required experience is high"
                skip = True
                
    except Exception as e:
        if jobDescription == "Unknown": print_lg("Unable to extract job description!")
        else:
            experience_required = "Error in extraction"
            print_lg("Unable to extract years of experience required!")
    finally:
        return jobDescription, experience_required, skip, skipReason, skipMessage

def upload_resume(modal, resume_path) -> tuple[bool, str]:
    try:
        modal.find_element(By.NAME, "file").send_keys(os.path.abspath(resume_path))
        return True, os.path.basename(resume_path)
    except: 
        return False, "Previous resume"

def answer_common_questions(label: str, answer: str, require_visa: str) -> str:
    if 'sponsorship' in label or 'visa' in label: 
        answer = require_visa
    return answer

def answer_questions(driver, actions, modal, questions_list, work_location, job_description, config_vars, ai_client=None, randomly_answered_questions=None) -> set:
    if randomly_answered_questions is None:
        randomly_answered_questions = set()
        
    all_questions = modal.find_elements(By.XPATH, ".//div[@data-test-form-element]")
    
    overwrite_previous_answers = config_vars.get('overwrite_previous_answers', False)
    gender = config_vars.get('gender', 'Decline')
    disability_status = config_vars.get('disability_status', 'Decline')
    current_city = config_vars.get('current_city', '')
    country = config_vars.get('country', '')
    state = config_vars.get('state', '')
    require_visa = config_vars.get('require_visa', 'No')
    us_citizenship = config_vars.get('us_citizenship', 'No')
    veteran_status = config_vars.get('veteran_status', 'No')
    use_AI = config_vars.get('use_AI', False)
    ai_provider = config_vars.get('ai_provider', 'openai')
    user_information_all = config_vars.get('user_information_all', '')
    linkedin_summary = config_vars.get('linkedin_summary', '')
    cover_letter = config_vars.get('cover_letter', '')

    for Question in all_questions:
        # 1. Select questions
        select_ele = try_xp(Question, ".//select", False)
        if select_ele:
            label_org = "Unknown"
            try:
                label_tag = Question.find_element(By.TAG_NAME, "label")
                label_org = label_tag.find_element(By.TAG_NAME, "span").text
            except: pass
            
            answer = 'Yes'
            label = label_org.lower()
            select = Select(select_ele)
            selected_option = select.first_selected_option.text
            
            optionsText = [option.text for option in select.options]
            options_str = "".join([f' "{option}",' for option in optionsText])
            
            prev_answer = selected_option
            if overwrite_previous_answers or selected_option == "Select an option":
                if 'email' in label or 'phone' in label: 
                    answer = prev_answer
                elif 'gender' in label or 'sex' in label: 
                    answer = gender
                elif 'disability' in label: 
                    answer = disability_status
                elif 'proficiency' in label: 
                    answer = 'Professional'
                elif any(loc_word in label for loc_word in ['location', 'city', 'state', 'country']):
                    if 'country' in label: answer = country 
                    elif 'state' in label: answer = state
                    elif 'city' in label: answer = current_city if current_city else work_location
                    else: answer = work_location
                else: 
                    answer = answer_common_questions(label, answer, require_visa)
                    
                try: 
                    select.select_by_visible_text(answer)
                except NoSuchElementException:
                    possible_answer_phrases = []
                    if answer == 'Decline': possible_answer_phrases = ["Decline", "not wish", "don't wish", "Prefer not", "not want"]
                    elif 'yes' in answer.lower(): possible_answer_phrases = ["Yes", "Agree", "I do", "I have"]
                    elif 'no' in answer.lower(): possible_answer_phrases = ["No", "Disagree", "I don't", "I do not"]
                    else: possible_answer_phrases = [answer, answer.lower(), answer.upper()]
                    
                    foundOption = False
                    for phrase in possible_answer_phrases:
                        for option in optionsText:
                            if phrase.lower() in option.lower() or option.lower() in phrase.lower():
                                select.select_by_visible_text(option)
                                answer = option
                                foundOption = True
                                break
                        if foundOption: break
                        
                    if not foundOption:
                        print_lg(f'Failed to find an option with text "{answer}" for question labelled "{label_org}", answering randomly!')
                        if len(select.options) > 1:
                            select.select_by_index(randint(1, len(select.options)-1))
                            answer = select.first_selected_option.text
                        randomly_answered_questions.add((f'{label_org} [ {options_str} ]',"select"))
            questions_list.add((f'{label_org} [ {options_str} ]', answer, "select", prev_answer))
            continue
        
        # 2. Radio questions
        radio = try_xp(Question, './/fieldset[@data-test-form-builder-radio-button-form-component="true"]', False)
        if radio:
            prev_answer = None
            label_ele = try_xp(radio, './/span[@data-test-form-builder-radio-button-form-component__title]', False)
            try: label_ele = find_by_class(label_ele, "visually-hidden", 2.0)
            except: pass
            label_org = label_ele.text if label_ele else "Unknown"
            answer = 'Yes'
            label = label_org.lower()

            label_with_options = label_org + ' [ '
            options = radio.find_elements(By.TAG_NAME, 'input')
            options_labels = []
            
            for option in options:
                opt_id = option.get_attribute("id")
                option_label_ele = try_xp(radio, f'.//label[@for="{opt_id}"]', False)
                opt_text = option_label_ele.text if option_label_ele else "Unknown"
                options_labels.append( f'"{opt_text}"<{option.get_attribute("value")}>' )
                if option.is_selected(): prev_answer = options_labels[-1]
                label_with_options += f' {options_labels[-1]},'

            if overwrite_previous_answers or prev_answer is None:
                if 'citizenship' in label or 'employment eligibility' in label: answer = us_citizenship
                elif 'veteran' in label or 'protected' in label: answer = veteran_status
                elif 'disability' in label or 'handicapped' in label: answer = disability_status
                else: answer = answer_common_questions(label, answer, require_visa)
                
                foundOptionEle = try_xp(radio, f".//label[normalize-space()='{answer}']", False)
                if foundOptionEle: 
                    actions.move_to_element(foundOptionEle).click().perform()
                else:    
                    possible_answer_phrases = ["Decline", "not wish", "don't wish", "Prefer not", "not want"] if answer == 'Decline' else [answer]
                    ele_to_click = options[0]
                    answer = options_labels[0]
                    found = False
                    for phrase in possible_answer_phrases:
                        for i, opt_label in enumerate(options_labels):
                            if phrase in opt_label:
                                ele_to_click = options[i]
                                answer = f'Decline ({opt_label})' if len(possible_answer_phrases) > 1 else opt_label
                                found = True
                                break
                        if found: break
                    actions.move_to_element(ele_to_click).click().perform()
                    if not found: randomly_answered_questions.add((f'{label_with_options} ]',"radio"))
            else: answer = prev_answer
            questions_list.add((label_with_options+" ]", answer, "radio", prev_answer))
            continue
        
        # 3. Text questions
        text_ele = try_xp(Question, ".//input[@type='text']", False)
        if text_ele: 
            do_actions = False
            label_lbl = try_xp(Question, ".//label[@for]", False)
            try: label_lbl = label_lbl.find_element(By.CLASS_NAME,'visually-hidden')
            except: pass
            label_org = label_lbl.text if label_lbl else "Unknown"
            answer = "" 
            label = label_org.lower()
            prev_answer = text_ele.get_attribute("value")
            
            if not prev_answer or overwrite_previous_answers:
                # Basic rules for text fields
                if 'phone' in label: answer = config_vars.get('phone_number', '')
                elif 'salary' in label or 'pay' in label or 'compensation' in label:
                    if 'monthly' in label: answer = config_vars.get('desired_salary_monthly', '')
                    elif 'lakh' in label: answer = config_vars.get('desired_salary_lakhs', '')
                    else: answer = config_vars.get('desired_salary', '')
                elif 'experience' in label:
                    answer = str(config_vars.get('current_experience', 0))
                # Add more rules as needed...
                
                if not answer or str(answer).strip() == "":
                    pyautogui.alert(
                        f"Could not auto-fill the question:\n\n'{label_org}'\n\n"
                        "Please type the answer manually in LinkedIn.\n\n"
                        "Click OK after you finish typing.",
                        "Manual Input Required"
                    )
                    while True:
                        current_val = text_ele.get_attribute("value")
                        if current_val and current_val.strip() != "":
                            answer = current_val
                            break
                        sleep(0.5)

                text_ele.clear()
                text_ele.send_keys(answer)
            questions_list.add((label, text_ele.get_attribute("value"), "text", prev_answer))
            continue

        # 4. Textarea questions
        text_area = try_xp(Question, ".//textarea", False)
        if text_area:
            label_lbl = try_xp(Question, ".//label[@for]", False)
            label_org = label_lbl.text if label_lbl else "Unknown"
            label = label_org.lower()
            answer = ""
            prev_answer = text_area.get_attribute("value")
            if not prev_answer or overwrite_previous_answers:
                if 'summary' in label: answer = linkedin_summary
                elif 'cover' in label: answer = cover_letter
                
                if answer == "" and use_AI and ai_client:
                    try:
                        if ai_provider.lower() == "openai":
                            answer = ai_answer_question(ai_client, label_org, question_type="textarea", job_description=job_description, user_information_all=user_information_all)
                        elif ai_provider.lower() == "deepseek":
                            answer = deepseek_answer_question(ai_client, label_org, options=None, question_type="textarea", job_description=job_description, about_company=None, user_information_all=user_information_all)
                        elif ai_provider.lower() == "gemini":
                            answer = gemini_answer_question(ai_client, label_org, options=None, question_type="textarea", job_description=job_description, about_company=None, user_information_all=user_information_all)
                        else:
                            randomly_answered_questions.add((label_org, "textarea"))
                    except Exception as e:
                        print_lg("Failed to get AI answer!", e)
                        randomly_answered_questions.add((label_org, "textarea"))
                elif answer == "":
                    randomly_answered_questions.add((label_org, "textarea"))
                    
            text_area.clear()
            text_area.send_keys(answer)
            questions_list.add((label, text_area.get_attribute("value"), "textarea", prev_answer))
            continue

        # 5. Checkbox questions
        checkbox = try_xp(Question, ".//input[@type='checkbox']", False)
        if checkbox:
            label_span = try_xp(Question, ".//span[@class='visually-hidden']", False)
            label_org = label_span.text if label_span else "Unknown"
            answer_ele = try_xp(Question, ".//label[@for]", False)
            answer_text = answer_ele.text if answer_ele else "Unknown"
            prev_answer = checkbox.is_selected()
            checked = prev_answer
            if not prev_answer:
                try:
                    actions.move_to_element(checkbox).click().perform()
                    checked = True
                except Exception as e: 
                    print_lg("Checkbox click failed!", e)
            questions_list.add((f'{label_org} ([X] {answer_text})', checked, "checkbox", prev_answer))
            continue

    # Try to close potential date picker
    try_xp(driver, "//button[contains(@aria-label, 'This is today')]")
    return questions_list
