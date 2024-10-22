import streamlit as st
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import os
from datetime import datetime
import base64
from PIL import Image
import io

class AutomationAction:
    def __init__(self, action_type, locator_type, locator_value, parameters=None):
        self.action_type = action_type
        self.locator_type = locator_type
        self.locator_value = locator_value
        self.parameters = parameters
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def to_dict(self):
        return {
            "action_type": self.action_type,
            "locator_type": self.locator_type,
            "locator_value": self.locator_value,
            "parameters": self.parameters,
            "timestamp": self.timestamp
        }

def initialize_session_state():
    """Initialize session state variables with new features"""
    if 'driver' not in st.session_state:
        st.session_state.driver = None
    if 'actions_history' not in st.session_state:
        st.session_state.actions_history = []
    if 'current_url' not in st.session_state:
        st.session_state.current_url = ""
    if 'recorded_scripts' not in st.session_state:
        st.session_state.recorded_scripts = {}
    if 'screenshot_history' not in st.session_state:
        st.session_state.screenshot_history = []
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False

def setup_driver(proxy=None, user_agent=None):
    """Setup and configure Chrome WebDriver with extended options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')
    
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def take_screenshot(driver):
    """Capture and return screenshot as base64"""
    screenshot = driver.get_screenshot_as_png()
    return base64.b64encode(screenshot).decode()

def generate_python_code(actions):
    """Generate executable Python code from recorded actions"""
    code = """from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def run_automation():
    # Setup driver
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    try:
"""
    
    for action in actions:
        if action['action'] == 'navigate':
            code += f"        driver.get('{action['url']}')\n"
        else:
            code += f"        element = WebDriverWait(driver, 10).until(\n"
            code += f"            EC.presence_of_element_located((By.{action['locator_type']}, '{action['locator_value']}'))\n"
            code += "        )\n"
            
            if action['action'] == 'click':
                code += "        element.click()\n"
            elif action['action'] == 'send_keys':
                code += f"        element.send_keys('{action['parameters']}')\n"
            elif action['action'] == 'clear':
                code += "        element.clear()\n"
    
    code += """    finally:
        driver.quit()

if __name__ == '__main__':
    run_automation()
"""
    return code

def main():
    st.title("Advanced Selenium Automation Builder")
    initialize_session_state()
    
    # Enhanced sidebar with additional features
    with st.sidebar:
        st.header("Controls")
        
        # Browser Configuration
        st.subheader("Browser Settings")
        user_agent = st.text_input("Custom User Agent (optional)")
        proxy = st.text_input("Proxy Server (optional)")
        
        # Start/Stop Browser with new configuration
        if st.session_state.driver is None:
            if st.button("Start Browser"):
                st.session_state.driver = setup_driver(proxy, user_agent)
                st.success("Browser started successfully!")
        else:
            if st.button("Stop Browser"):
                st.session_state.driver.quit()
                st.session_state.driver = None
                st.success("Browser stopped successfully!")
        
        # Navigation with wait options
        st.subheader("Navigation")
        url = st.text_input("Enter URL", value=st.session_state.current_url)
        wait_time = st.slider("Page Load Wait Time (seconds)", 0, 30, 10)
        
        if st.button("Navigate") and st.session_state.driver:
            try:
                st.session_state.driver.get(url)
                time.sleep(wait_time)
                st.session_state.current_url = url
                st.session_state.actions_history.append({
                    "action": "navigate",
                    "url": url,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Take screenshot after navigation
                screenshot = take_screenshot(st.session_state.driver)
                st.session_state.screenshot_history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "screenshot": screenshot
                })
                
                st.success("Navigated successfully!")
            except Exception as e:
                st.error(f"Navigation failed: {str(e)}")
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["Automation Builder", "Screenshots", "Generated Code"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("Selenium Actions")
            
            # Enhanced Element Locator
            st.subheader("Element Locator")
            locator_type = st.selectbox(
                "Select Locator Type",
                ["ID", "CLASS_NAME", "NAME", "TAG_NAME", "XPATH", "CSS_SELECTOR", "LINK_TEXT", "PARTIAL_LINK_TEXT"]
            )
            
            locator_value = st.text_input("Enter Locator Value")
            
            # Enhanced Action Selection
            action_type = st.selectbox(
                "Select Action",
                ["click", "send_keys", "clear", "get_text", "get_attribute", 
                 "double_click", "right_click", "hover", "drag_and_drop"]
            )
            
            # Action Parameters
            if action_type == "send_keys":
                input_text = st.text_input("Enter text to send")
                special_keys = st.multiselect(
                    "Add Special Keys",
                    ["ENTER", "TAB", "ESCAPE", "RETURN", "SPACE"]
                )
            elif action_type == "get_attribute":
                attribute_name = st.text_input("Enter attribute name")
            elif action_type == "drag_and_drop":
                target_locator = st.text_input("Enter target element locator")
            
            # Execute Action Button
            if st.button("Execute Action") and st.session_state.driver:
                try:
                    element = WebDriverWait(st.session_state.driver, 10).until(
                        EC.presence_of_element_located((getattr(By, locator_type), locator_value))
                    )
                    
                    action_result = None
                    if action_type == "click":
                        element.click()
                        action_result = "Click successful"
                    elif action_type == "send_keys":
                        keys_to_send = input_text
                        for key in special_keys:
                            keys_to_send += getattr(Keys, key)
                        element.send_keys(keys_to_send)
                        action_result = f"Sent keys: {input_text}"
                    elif action_type == "clear":
                        element.clear()
                        action_result = "Element cleared"
                    elif action_type == "get_text":
                        action_result = element.text
                    elif action_type == "get_attribute":
                        action_result = element.get_attribute(attribute_name)
                    elif action_type == "double_click":
                        ActionChains(st.session_state.driver).double_click(element).perform()
                        action_result = "Double click successful"
                    elif action_type == "right_click":
                        ActionChains(st.session_state.driver).context_click(element).perform()
                        action_result = "Right click successful"
                    elif action_type == "hover":
                        ActionChains(st.session_state.driver).move_to_element(element).perform()
                        action_result = "Hover successful"
                    
                    # Record action
                    st.session_state.actions_history.append({
                        "action": action_type,
                        "locator_type": locator_type,
                        "locator_value": locator_value,
                        "parameters": input_text if action_type == "send_keys" else None,
                        "result": action_result,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    # Take screenshot after action
                    screenshot = take_screenshot(st.session_state.driver)
                    st.session_state.screenshot_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "screenshot": screenshot
                    })
                    
                    st.success(f"Action executed successfully: {action_result}")
                except Exception as e:
                    st.error(f"Action failed: {str(e)}")
        
        with col2:
            st.header("Action History")
            if st.session_state.actions_history:
                for action in st.session_state.actions_history:
                    st.write("---")
                    st.write(f"**Action:** {action['action']}")
                    st.write(f"**Time:** {action['timestamp']}")
                    if 'result' in action:
                        st.write(f"**Result:** {action['result']}")
            
            if st.button("Save Actions"):
                if st.session_state.actions_history:
                    filename = f"selenium_actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    # Save actions as JSON
                    with open(f"{filename}.json", 'w') as f:
                        json.dump(st.session_state.actions_history, f, indent=4)
                    
                    # Generate and save Python script
                    with open(f"{filename}.py", 'w') as f:
                        f.write(generate_python_code(st.session_state.actions_history))
                    
                    st.success(f"Actions saved to {filename}.json and {filename}.py")
                else:
                    st.warning("No actions to save")
            
            if st.button("Clear History"):
                st.session_state.actions_history = []
                st.success("History cleared")
    
    with tab2:
        st.header("Screenshot History")
        for screenshot in st.session_state.screenshot_history:
            st.write(f"Screenshot taken at: {screenshot['timestamp']}")
            st.image(base64.b64decode(screenshot['screenshot']))
    
    with tab3:
        st.header("Generated Python Code")
        if st.session_state.actions_history:
            st.code(generate_python_code(st.session_state.actions_history), language="python")
        else:
            st.info("No actions recorded yet. The generated code will appear here.")

if __name__ == "__main__":
    main()
