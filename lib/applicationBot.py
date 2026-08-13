import os
import re
import urllib.parse
from json import load
import time
import yaml
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

class linkedInBot:
    def __init__(self,resumeName,jobBlob):
        self.loginUri = "https://www.linkedin.com/login/?trk=guest_homepage-basic_nav-header-signin"
        self.driver = webdriver.Firefox()
        self.jobBlob = jobBlob
        self.resumeName = resumeName
        load_dotenv()
        self.user = os.getenv("user")
        self.passwd = os.getenv("passwd")
        self.userAA = os.getenv("userAA")
        with open("./instructionSheets/answers.yaml", "r", encoding="utf-8") as f:
            self.answers = yaml.safe_load(f)
        self.flat_answers = self._flatten_dict(self.answers)
    def login(self):
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(2)

        # 1. Inject Cookies
        try:
            with open("cookies.json", "r", encoding="utf-8") as cookyFile:
                cookies = load(cookyFile)
                for cookie in cookies:
                    self.driver.add_cookie({"name": cookie["name"], "value": cookie["value"]})

            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(3)
        except Exception as e:
            print(f"Cookie injection skipped: {e}")

        # 2. Check if cookies successfully logged us in (Redirected to feed)
        if "feed" in self.driver.current_url:
            print("Successfully logged in via cookies!")
            return

        # 3. Wait for LinkedIn's actual username/email selector
        try:
            emailBox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "username"))
            )
            passwdBox = self.driver.find_element(By.ID, "password")

            emailBox.clear()
            emailBox.send_keys(self.user)
            passwdBox.clear()
            passwdBox.send_keys(self.passwd)

            # LinkedIn submit button
            loginBtn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            loginBtn.click()

        except Exception:
            # If it times out, check if LinkedIn triggered a CAPTCHA/Verification checkpoint
            if "checkpoint" in self.driver.current_url:
                print("LinkedIn triggered a Security Checkpoint / CAPTCHA verification.")
            else:
                print("Failed to locate login fields.")

    def gotoJob(self,obj):
        self.driver.get(obj['link'])

    def getLinkByRegex(self,pattern):
        workday_regex_pattern = re.compile(rf'{pattern}')
        for link in self.driver.find_elements(By.TAG_NAME, "a"):
            href = link.get_attribute("href")
            if href and workday_regex_pattern.search(href):
                return link
    def addFile(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(os.path.abspath(self.resumeName))
            createAccount =   self.driver.find_element(By.CSS_SELECTOR, '[data-automation-id="pageFooterNextButton"]')
            createAccount.click()
        except Exception as e:
            return e
    def newLoginWorkDay(self):
        userIdBox =       self.driver.find_element(By.ID,"input-4")
        passwdBox =       self.driver.find_element(By.ID,"input-5")
        verifyPasswdBox = self.driver.find_element(By.ID,"input-6")
        EULAAgree =       self.driver.find_element(By.ID,"input-9")
        createAccount =   self.driver.find_element(By.CSS_SELECTOR, '[data-automation-id="click_filter"]')
        userIdBox.clear()
        userIdBox.send_keys(self.userAA)
        passwdBox.clear()
        passwdBox.send_keys(self.passwd)
        verifyPasswdBox.clear()
        verifyPasswdBox.send_keys(self.passwd)
        EULAAgree.click()
        createAccount.click()

    def loginWorkDay(self):
        try:
            userIdBox =       self.driver.find_element(By.ID,"input-4")
            passwdBox =       self.driver.find_element(By.ID,"input-5")
            loginBox =        self.driver.find_element(By.CSS_SELECTOR, '[data-automation-id="click_filter"]')
            userIdBox.clear()
            userIdBox.send_keys(self.userAA)
            passwdBox.clear()
            passwdBox.send_keys(self.passwd)
            loginBox.click()
        except Exception as e:
            return e

    def _flatten_dict(self, d, parent_key=''):
        """Flattens nested YAML dictionary into a simple key-value map."""
        items = []
        for k, v in d.items():
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, k).items())
            else:
                items.append((k.lower().replace('_', ' '), str(v)))
        return dict(items)

    def handle_previous_worker_question(self):
        """
        Specifically targets 'Have you previously worked for...' radio/yes-no questions.
        """
        target_answer = self.flat_answers.get("previously worked", "No").strip().lower()

        # Common phrases found on application portals
        phrases = [
            "previously worked",
            "former employee",
            "prior employee",
            "have you ever been employed",
            "previously employed",
            "previously been employed"
        ]

        for phrase in phrases:
            # Find labels/legends containing any of the target phrases
            xpath = f"//*[(self::label or self::legend or self::span) and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{phrase}')]"
            matching_elements = self.driver.find_elements(By.XPATH, xpath)

            for elem in matching_elements:
                try:
                    # Find the parent container holding the Yes/No choices
                    container = elem.find_element(By.XPATH, "./ancestor::fieldset | ./ancestor::div[contains(@class, 'form') or contains(@data-automation-id, 'formField')]")

                    # Locate the specific radio option or label matching "Yes" or "No"
                    option_xpath = f".//*[(self::label or self::input or self::button) and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_answer}')]"
                    options = container.find_elements(By.XPATH, option_xpath)

                    for option in options:
                        if option.is_displayed():
                            option.click()
                            time.sleep(0.5)
                            return True
                except Exception:
                    continue

        return False


    def fill_phone_type(self):
        """Handles both Workday custom popover dropdowns and standard select inputs for Phone Type."""
        phone_type = self.answers.get("personal_info", {}).get("phone_type", "Mobile")

        # 1. Try Workday Custom Dropdown (button/div based)
        try:
            dropdown_btn = self.driver.find_element(
                By.XPATH,
                "//button[contains(@aria-label, 'Phone Type') or contains(@data-automation-id, 'phone-device-type')]"
                " | //div[contains(@data-automation-id, 'phone-device-type')]//button"
            )
            if dropdown_btn.is_displayed():
                dropdown_btn.click()
                time.sleep(1)

                # Match option in popup list
                option_xpath = f"//*[(self::li or self::div[@role='option']) and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{phone_type.lower()}')]"
                option = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, option_xpath))
                )
                option.click()
                time.sleep(0.5)
                return
        except Exception:
            pass

        # 2. Fallback to standard HTML <select> tag
        try:
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            for select_elem in selects:
                select_id = (select_elem.get_attribute("id") or "").lower()
                select_name = (select_elem.get_attribute("name") or "").lower()

                if "phone" in select_id or "phone" in select_name or "device" in select_id:
                    select = Select(select_elem)
                    select.select_by_visible_text(phone_type)
                    return
        except Exception:
            pass

    def fill_work_experience(self):
        """Robust Work Experience filler using dynamic label and wrapper matching."""
        experiences = self.answers.get("work_experience", [])
        if not experiences:
            return

        # 1. Check if we need to click an initial "Add" button to reveal fields
        self._ensure_experience_form_open()

        for index, exp in enumerate(experiences):
            # For additional entries beyond the first, click "Add Another"
            if index > 0:
                self._click_add_another_experience()

            print(f"Populating Work Experience entry #{index + 1}...")

            # Fill fields using flexible locator combinations
            self._type_into_workday_field(["Job Title", "Title"], exp.get("title"), "jobTitle")
            self._type_into_workday_field(["Company", "Company Name"], exp.get("company"), "company")
            self._type_into_workday_field(["Location"], exp.get("location"), "location")
            self._type_into_workday_field(["Description", "Summary", "Role Description"], exp.get("description"), "description", is_textarea=True)


    def _ensure_experience_form_open(self):
        """Clicks 'Add' or 'Add Experience' if the form fields are not currently visible."""
        add_button_xpaths = [
            "//button[@data-automation-id='add-work-experience']",
            "//button[@data-automation-id='Add']",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add work experience')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add experience')]"
        ]

        for xpath in add_button_xpaths:
            try:
                buttons = self.driver.find_elements(By.XPATH, xpath)
                for btn in buttons:
                    if btn.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(0.5)
                        btn.click()
                        time.sleep(1.5)
                        return
            except Exception:
                continue


    def _click_add_another_experience(self):
        """Clicks the 'Add Another' or '+' button for multi-experience entries."""
        try:
            add_another_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH, 
                    "//button[contains(@aria-label, 'Add Another') or contains(@data-automation-id, 'add-row') or contains(., 'Add Another')]"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_another_btn)
            add_another_btn.click()
            time.sleep(1.5)
        except Exception as e:
            print(f"Could not add extra experience row: {e}")


    def _type_into_workday_field(self, label_names, text_value, automation_id_key, is_textarea=False):
        """
        Locates a Workday input field using 3 fallback methods:
        Method 1: Wrapper div data-automation-id + input child
        Method 2: Label text -> input tag association
        Method 3: Direct input data-automation-id
        """
        if not text_value:
            return

        tag_type = "textarea" if is_textarea else "input"

        # Construct Locator Patterns
        patterns = []

        # 1. Wrapper div pattern (Common in Workday React forms)
        patterns.append(f"//div[contains(@data-automation-id, '{automation_id_key}') or contains(@data-automation-id, '{automation_id_key.lower()}')]//{tag_type}")

        # 2. Direct input automation ID pattern
        patterns.append(f"//{tag_type}[contains(@data-automation-id, '{automation_id_key}')]")

        # 3. Label text matching (Matches <label>Title</label> -> <input>)
        for label in label_names:
            # Match by 'for' attribute or parent/following sibling input
            patterns.append(f"//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]/following::${tag_type}[1]")
            patterns.append(f"//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]/..//{tag_type}")

        # Iterate through patterns until a visible element is found
        for pattern in patterns:
            try:
                elements = self.driver.find_elements(By.XPATH, pattern)
                for elem in elements:
                    if elem.is_displayed():
                        # Scroll center to clear sticky banners
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                        time.sleep(0.2)

                        # React event dispatch sequence
                        elem.click()
                        elem.clear()
                        elem.send_keys(str(text_value))
                        time.sleep(0.3)
                        return True
            except Exception:
                continue

        print(f"WARNING: Could not find field for '{automation_id_key}' / labels {label_names}")
        return False
    def handle_checkboxes(self):
        """Finds and toggles checkboxes based on boolean values in the YAML."""
        checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        for checkbox in checkboxes:
            if not checkbox.is_displayed():
                continue
            
            checkbox_id = checkbox.get_attribute("id")
            label_text = ""

            if checkbox_id:
                labels = self.driver.find_elements(By.XPATH, f"//label[@for='{checkbox_id}']")
                if labels:
                    label_text = labels[0].text.lower()
            
            if not label_text:
                label_text = (checkbox.get_attribute("aria-label") or "").lower()

            for key, value in self.flat_answers.items():
                if key in label_text:
                    # If YAML says True/Yes and it's not checked, click it
                    is_checked = checkbox.is_selected()
                    wants_checked = str(value).strip().lower() in ['true', 'yes', '1']
                    
                    if wants_checked and not is_checked:
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        time.sleep(0.3)
                    elif not wants_checked and is_checked:
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        time.sleep(0.3)
                    break
    def fill_form_from_yaml(self):
        """Populates text inputs, dropdowns, and radio buttons using YAML answers."""

        # 1. First, handle specific edge case: 
        self.handle_previous_worker_question()
        self.fill_phone_type()
        self.fill_work_experience()
        self.addFile()
        self.handle_checkboxes()
        # 2. Handle standard Text Inputs & Textareas
        inputs = self.driver.find_elements(By.XPATH, "//input[@type='text' or @type='email' or @type='tel' or not(@type)] | //textarea")
        for field in inputs:
            if not field.is_displayed():
                continue
            
            field_id = field.get_attribute("id")
            label_text = ""

            if field_id:
                labels = self.driver.find_elements(By.XPATH, f"//label[@for='{field_id}']")
                if labels:
                    label_text = labels[0].text.lower()

            if not label_text:
                label_text = (field.get_attribute("aria-label") or field.get_attribute("placeholder") or "").lower()

            for key, value in self.flat_answers.items():
                if key in label_text and not field.get_attribute("value"):
                    field.clear()
                    field.send_keys(value)
                    time.sleep(0.3)
                    break

        # 3. Handle Select Dropdowns
        select_elements = self.driver.find_elements(By.TAG_NAME, "select")
        for select_elem in select_elements:
            if not select_elem.is_displayed():
                continue
            
            select_id = select_elem.get_attribute("id")
            label_text = ""
            if select_id:
                labels = self.driver.find_elements(By.XPATH, f"//label[@for='{select_id}']")
                if labels:
                    label_text = labels[0].text.lower()

            for key, value in self.flat_answers.items():
                if key in label_text:
                    try:
                        select = Select(select_elem)
                        select.select_by_visible_text(value)
                    except Exception:
                        pass
                    break

        # 4. Handle Generic Radio Buttons
        radios = self.driver.find_elements(By.XPATH, "//input[@type='radio']")
        for radio in radios:
            if not radio.is_displayed():
                continue
            
            radio_value = (radio.get_attribute("value") or "").lower()
            radio_id = radio.get_attribute("id")

            if radio_id:
                labels = self.driver.find_elements(By.XPATH, f"//label[@for='{radio_id}']")
                if labels:
                    radio_value = labels[0].text.lower()

            for key, value in self.flat_answers.items():
                if value.lower() in radio_value:
                    radio.click()
                    time.sleep(0.3)
                    break
    def fill_lever_form(self):
        """Fills out standard fields, custom inputs, dropdowns, and radios on Lever (jobs.lever.co)."""
        print("Detected Lever application portal. Filling form...")
    
        personal_info = self.answers.get("personal_info", {})
    
        # Helper function to safely send keys and trigger JS input/change events
        def type_and_trigger(element, text):
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                element.clear()
                element.send_keys(str(text))
                # Trigger events for Lever's dynamic JS validation
                self.driver.execute_script(
                    "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
                    "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                    element
                )
                time.sleep(0.1)
            except Exception as e:
                print(f"Error typing into element: {e}")
    
        # -------------------------------------------------------------------------
        # 1. Standard Fields (Name, Email, Phone, Company, Social URLs)
        # -------------------------------------------------------------------------
        full_name = personal_info.get("full_name") or f"{personal_info.get('first_name', '')} {personal_info.get('last_name', '')}".strip()
        
        standard_inputs = {
            "name": full_name,
            "email": personal_info.get("email"),
            "phone": personal_info.get("phone"),
            "org": personal_info.get("current_company"),
            "urls[LinkedIn]": personal_info.get("linkedin_url"),
            "urls[GitHub]": personal_info.get("github_url"),
            "urls[Portfolio]": personal_info.get("portfolio_url"),
            "urls[Twitter]": personal_info.get("twitter_url"),
            "urls[Other]": personal_info.get("other_url") or personal_info.get("website"),
            "comments": personal_info.get("comments") or personal_info.get("cover_letter")
        }
    
        for name_attr, val in standard_inputs.items():
            if not val:
                continue
            try:
                # Flexible locator to handle case variations in name attributes
                elems = self.driver.find_elements(By.XPATH, f"//input[translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{name_attr.lower()}'] | //textarea[@name='{name_attr}']")
                for elem in elems:
                    if elem.is_displayed() and not elem.get_attribute("value"):
                        type_and_trigger(elem, val)
            except Exception:
                pass
            
        # -------------------------------------------------------------------------
        # 2. Resume Upload
        # -------------------------------------------------------------------------
        try:
            file_input = self.driver.find_element(By.XPATH, "//input[@type='file' and (@name='resume' or @id='resume-upload-input')]")
            if file_input:
                file_input.send_keys(os.path.abspath(self.resumeName))
                time.sleep(1)
        except Exception as e:
            print(f"Lever resume upload skipped/failed: {e}")
    
        # -------------------------------------------------------------------------
        # 3. Handle Select Dropdowns (Custom questions + EEO)
        # -------------------------------------------------------------------------
        select_elements = self.driver.find_elements(By.TAG_NAME, "select")
        for select_elem in select_elements:
            try:
                if not select_elem.is_displayed():
                    continue
                
                # Find closest parent container/label to identify question text
                parent = select_elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'application-question') or contains(@class, 'application-field') or contains(@class, 'eeo')]")
                question_text = parent.text.lower()
    
                select_obj = Select(select_elem)
                
                # Check against dictionary answers
                for key, value in self.flat_answers.items():
                    if key.lower() in question_text:
                        target_val = str(value).lower()
                        # Try matching option text
                        for option in select_obj.options:
                            if target_val in option.text.lower():
                                select_obj.select_by_visible_text(option.text)
                                time.sleep(0.2)
                                break
                        break
            except Exception:
                continue
            
        # -------------------------------------------------------------------------
        # 4. Handle Custom Text Questions & Textareas
        # -------------------------------------------------------------------------
        custom_questions = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'application-question')]")
        for group in custom_questions:
            try:
                question_text = group.text.lower()
                
                # Find matching text input or textarea
                inputs = group.find_elements(By.XPATH, ".//input[@type='text'] | .//textarea")
                for input_elem in inputs:
                    if input_elem.is_displayed() and not input_elem.get_attribute("value"):
                        for key, value in self.flat_answers.items():
                            if key.lower() in question_text:
                                type_and_trigger(input_elem, value)
                                break
            except Exception:
                continue
            
        # -------------------------------------------------------------------------
        # 5. Handle Radio Buttons & Checkboxes
        # -------------------------------------------------------------------------
        for key, value in self.flat_answers.items():
            val_str = str(value).lower()
            key_str = str(key).lower()
            
            try:
                # Find matching radio/checkbox elements where the label or surrounding text matches key and value
                clickable_elements = self.driver.find_elements(
                    By.XPATH,
                    f"//div[contains(@class, 'application-question') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key_str}')]"
                    f"//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{val_str}')]"
                )
                for label in clickable_elements:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", label)
                    label.click()
                    time.sleep(0.2)
            except Exception:
                pass
            
    def apply(self):
        time.sleep(1)
        try:
            current_url = self.driver.current_url.lower()

            # --- BRANCH 1: LEVER ---
            if "lever.co" in current_url:
                self.fill_lever_form()
                
                # Optionally submit the Lever form
                # submit_btn = self.driver.find_element(By.ID, "btn-submit")
                # submit_btn.click()
                return

            # --- BRANCH 2: WORKDAY / LINKEDIN (Existing Logic) ---
            try:
                raw_href = self.getLinkByRegex('/safety/go').get_attribute("href")
                post_url = urllib.parse.unquote(str(raw_href)[40:])
                self.driver.get(post_url)
            except Exception:
                pass

            # Detect Workday auth redirect
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-automation-id*="email"]'))
                ).click()
                self.newLoginWorkDay()
                time.sleep(5)
                self.loginWorkDay()
            except Exception:
                pass

            # Workday multi-page loop
            while True:
                self.fill_form_from_yaml()
                next_btn = self.driver.find_element(By.CSS_SELECTOR, '[data-automation-id="pageFooterNextButton"]')
                next_btn.click()
                time.sleep(4)

        except Exception as e:
            print(f"Application step completed or stopped: {e}")

    def close(self):
            """Cleans up the WebDriver session."""
            print("Job application loop complete. Closing browser...")
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing browser: {e}")
    def autoApply(self):
            self.login()
            print("Waiting for login to settle...")
            time.sleep(6)

            for job_id, job_url in self.jobBlob.items():
                print(f"\n--- Attempting to apply for Job ID: {job_id} ---")
                try:
                    # Assuming jobBlob is a dict like {'job1': {'link': 'url'}, ...}
                    # If it's just a flat dict {'job1': 'url'}, you'll need to adjust gotoJob
                    self.gotoJob({'link': job_url} if isinstance(job_url, str) else job_url)
                    self.apply()
                except Exception as e:
                    print(f"Failed processing job {job_id}: {e}")
                    continue # Skip to the next job in the queue
                
            self.close()
