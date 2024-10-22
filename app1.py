import streamlit as st
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import json
import os
from datetime import datetime

def initialize_session_state():
    """Initialize session state variables"""
    if 'driver' not in st.session_state:
        st.session_state.driver = None
    if 'actions_history' not in st.session_state:
        st.session_state.actions_history = []
    if 'current_url' not in st.session_state:
        st.session_state.current_url = ""

def setup_driver():
    """Setup and configure Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def save_actions(actions):
    """Save recorded actions to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"selenium_actions_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(actions, f, indent=4)
    return filename

def main():
    st.title("Selenium Automation Builder")
    initialize_session_state()
    
    # Sidebar for controls and settings
    with st.sidebar:
        st.header("Controls")
        
        # Start/Stop Browser
        if st.session_state.driver is None:
            if st.button("Start Browser"):
                st.session_state.driver = setup_driver()
                st.success("Browser started successfully!")
        else:
            if st.button("Stop Browser"):
                st.session_state.driver.quit()
                st.session_state.driver = None
                st.success("Browser stopped successfully!")
        
        # URL Navigation
        st.subheader("Navigation")
        url = st.text_input("Enter URL", value=st.session_state.current_url)
        if st.button("Navigate") and st.session_state.driver:
            try:
                st.session_state.driver.get(url)
                st.session_state.current_url = url
                st.session_state.actions_history.append({
                    "action": "navigate",
                    "url": url,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Navigated successfully!")
            except Exception as e:
                st.error(f"Navigation failed: {str(e)}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Selenium Actions")
        
        # Element Locator
        st.subheader("Element Locator")
        locator_type = st.selectbox(
            "Select Locator Type",
            ["ID", "CLASS_NAME", "NAME", "TAG_NAME", "XPATH", "CSS_SELECTOR"]
        )
        
        locator_value = st.text_input("Enter Locator Value")
        
        # Action Selection
        action_type = st.selectbox(
            "Select Action",
            ["click", "send_keys", "clear", "get_text", "get_attribute"]
        )
        
        # Action Parameters
        if action_type == "send_keys":
            input_text = st.text_input("Enter text to send")
        elif action_type == "get_attribute":
            attribute_name = st.text_input("Enter attribute name")
        
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
                    element.send_keys(input_text)
                    action_result = f"Sent keys: {input_text}"
                elif action_type == "clear":
                    element.clear()
                    action_result = "Element cleared"
                elif action_type == "get_text":
                    action_result = element.text
                elif action_type == "get_attribute":
                    action_result = element.get_attribute(attribute_name)
                
                # Record action
                st.session_state.actions_history.append({
                    "action": action_type,
                    "locator_type": locator_type,
                    "locator_value": locator_value,
                    "parameters": input_text if action_type == "send_keys" else None,
                    "result": action_result,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                filename = save_actions(st.session_state.actions_history)
                st.success(f"Actions saved to {filename}")
            else:
                st.warning("No actions to save")
        
        if st.button("Clear History"):
            st.session_state.actions_history = []
            st.success("History cleared")

if __name__ == "__main__":
    main()
