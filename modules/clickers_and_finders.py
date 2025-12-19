
from config.loader import *
from modules.helpers import buffer, print_lg, sleep
from modules.shadow_dom_handler import find_and_click_robust, find_in_shadow_root, robust_click, is_element_visible
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

# Click Functions


def wait_span_click_enhanced(driver: WebDriver, text: str, time: float=5.0, click: bool=True, scroll: bool=True, scrollTop: bool=False) -> WebElement | bool:
    '''
    Enhanced version of wait_span_click that handles both light DOM and Shadow DOM elements.
    Uses robust clicking strategies to ensure element interaction even if hidden or in shadow roots.
    
    Flow:
    1. Try finding in light DOM with XPath
    2. If not found, search recursively through Shadow DOM using JavaScript
    3. Use robust click with multiple fallback strategies
    4. Return WebElement if found and clicked
    
    - Returns `WebElement` if found, else `False` if not found.
    - Clicks on it if `click = True`.
    - Will spend a max of `time` seconds in searching for each element.
    - Will scroll to the element if `scroll = True`.
    - Will scroll to the top if `scrollTop = True`.
    '''
    if text:
        try:
            # Try light DOM first
            try:
                button = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, './/span[normalize-space(.)="'+text+'"]')))
                print_lg(f"Found '{text}' in light DOM")
            except:
                # Try shadow DOM
                button = find_in_shadow_root(driver, text, time)
                if button:
                    print_lg(f"Found '{text}' in Shadow DOM")
                else:
                    print_lg(f"Element '{text}' not found in light DOM or Shadow DOM")
                    return False
            
            if scroll:
                scroll_to_view(driver, button, scrollTop)
            
            if click:
                success = robust_click(driver, button, text)
                if success:
                    return button
                else:
                    print_lg(f"Failed to click '{text}' despite finding it")
                    return False
            
            return button
        except Exception as e:
            print_lg(f"Click Failed! Didn't find or click '{text}': {str(e)}")
            return False


def wait_span_click(driver: WebDriver, text: str, time: float=5.0, click: bool=True, scroll: bool=True, scrollTop: bool=False) -> WebElement | bool:
    '''
    Finds the span element with the given `text`.
    - Returns `WebElement` if found, else `False` if not found.
    - Clicks on it if `click = True`.
    - Will spend a max of `time` seconds in searching for each element.
    - Will scroll to the element if `scroll = True`.
    - Will scroll to the top if `scrollTop = True`.
    '''
    if text:
        try:
            button = WebDriverWait(driver,time).until(EC.presence_of_element_located((By.XPATH, './/span[normalize-space(.)="'+text+'"]')))
            if scroll:  scroll_to_view(driver, button, scrollTop)
            if click:
                button.click()
                buffer(click_gap)
            return button
        except Exception as e:
            print_lg("Click Failed! Didn't find '"+text+"'")
            # print_lg(e)
            return False

def multi_sel(driver: WebDriver, texts: list, time: float=5.0) -> None:
    '''
    - For each text in the `texts`, tries to find and click `span` element with that text.
    - Will spend a max of `time` seconds in searching for each element.
    '''
    for text in texts:

        wait_span_click(driver, text, time, False)

        try:
            button = WebDriverWait(driver,time).until(EC.presence_of_element_located((By.XPATH, './/span[normalize-space(.)="'+text+'"]')))
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print_lg("Click Failed! Didn't find '"+text+"'")
            # print_lg(e)

def multi_sel_noWait(driver: WebDriver, texts: list, actions: ActionChains = None) -> None:
    '''
    - For each text in the `texts`, tries to find and click `span` element with that class.
    - If `actions` is provided, bot tries to search and Add the `text` to this filters list section.
    - Won't wait to search for each element, assumes that element is rendered.
    '''
    for text in texts:
        try:
            button = driver.find_element(By.XPATH, './/span[normalize-space(.)="'+text+'"]')
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            if actions: company_search_click(driver,actions,text)
            else:   print_lg("Click Failed! Didn't find '"+text+"'")
            # print_lg(e)

def boolean_button_click(driver: WebDriver, actions: ActionChains, text: str) -> None:
    '''
    Tries to click on the boolean button with the given `text` text.
    '''
    try:
        list_container = driver.find_element(By.XPATH, './/h3[normalize-space()="'+text+'"]/ancestor::fieldset')
        button = list_container.find_element(By.XPATH, './/input[@role="switch"]')
        scroll_to_view(driver, button)
        actions.move_to_element(button).click().perform()
        buffer(click_gap)
    except Exception as e:
        print_lg("Click Failed! Didn't find '"+text+"'")
        # print_lg(e)

# Find functions
def find_by_class(driver: WebDriver, class_name: str, time: float=5.0) -> WebElement | Exception:
    '''
    Waits for a max of `time` seconds for element to be found, and returns `WebElement` if found, else `Exception` if not found.
    '''
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

# Scroll functions
# def scroll_to_view(driver: WebDriver, element: WebElement, top: bool = False, smooth_scroll: bool = smooth_scroll) -> None:
#     '''
#     Scrolls the `element` to view.
#     - `smooth_scroll` will scroll with smooth behavior.
#     - `top` will scroll to the `element` to top of the view.
#     '''
#     if top:
#         return driver.execute_script('arguments[0].scrollIntoView();', element)
#     behavior = "smooth" if smooth_scroll else "instant"
#     return driver.execute_script('arguments[0].scrollIntoView({block: "center", behavior: "'+behavior+'" });', element)
def scroll_to_view(driver: WebDriver, element: WebElement, top: bool = False, smooth_scroll: bool = None) -> None:
    """
    Scrolls the element into view.
    - If smooth_scroll is None, it tries to read the global smooth_scroll injected by loader.py.
    - top=True forces normal scrollIntoView().
    """
    if smooth_scroll is None:
        # Try to use the global setting injected by loader
        smooth_scroll = globals().get("smooth_scroll", False)

    if top:
        return driver.execute_script('arguments[0].scrollIntoView();', element)

    behavior = "smooth" if smooth_scroll else "instant"
    return driver.execute_script(
        'arguments[0].scrollIntoView({block: "center", behavior: "%s" });' % behavior,
        element
    )

# Enter input text functions
def text_input_by_ID(driver: WebDriver, id: str, value: str, time: float=5.0) -> None | Exception:
    '''
    Enters `value` into the input field with the given `id` if found, else throws NotFoundException.
    - `time` is the max time to wait for the element to be found.
    '''
    username_field = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.ID, id)))
    username_field.send_keys(Keys.CONTROL + "a")
    username_field.send_keys(value)

def try_xp(driver: WebDriver, xpath: str, click: bool=True) -> WebElement | bool:
    try:
        if click:
            driver.find_element(By.XPATH, xpath).click()
            return True
        else:
            return driver.find_element(By.XPATH, xpath)
    except: return False

def try_linkText(driver: WebDriver, linkText: str) -> WebElement | bool:
    try:    return driver.find_element(By.LINK_TEXT, linkText)
    except:  return False

def try_find_by_classes(driver: WebDriver, classes: list[str]) -> WebElement | ValueError:
    for cla in classes:
        try:    return driver.find_element(By.CLASS_NAME, cla)
        except: pass
    raise ValueError("Failed to find an element with given classes")

def company_search_click(driver: WebDriver, actions: ActionChains, companyName: str) -> None:
    '''
    Tries to search and Add the company to company filters list.
    '''
    wait_span_click(driver,"Add a company",1)
    search = driver.find_element(By.XPATH,"(.//input[@placeholder='Add a company'])[1]")
    search.send_keys(Keys.CONTROL + "a")
    search.send_keys(companyName)
    buffer(3)
    actions.send_keys(Keys.DOWN).perform()
    actions.send_keys(Keys.ENTER).perform()
    print_lg(f'Tried searching and adding "{companyName}"')

def text_input(actions: ActionChains, textInputEle: WebElement | bool, value: str, textFieldName: str = "Text") -> None | Exception:
    if textInputEle:
        sleep(1)
        # actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
        textInputEle.clear()
        textInputEle.send_keys(value.strip())
        sleep(2)
        actions.send_keys(Keys.ENTER).perform()
    else:
        print_lg(f'{textFieldName} input was not given!')
