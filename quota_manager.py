import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Browser driver managers
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.firefox.service import Service as FirefoxService


class QuotaManager:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.driver_path = None  # Lazy-loaded on first use
        self._driver_path_cached = False
    
    def _ensure_driver_path(self):
        """Lazy-load the geckodriver path on first use"""
        if self._driver_path_cached:
            return
        
        print("[DEBUG] Caching geckodriver path...")
        try:
            self.driver_path = GeckoDriverManager().install()
            print(f"[DEBUG] Geckodriver cached at: {self.driver_path}")
        except Exception as e:
            print(f"[DEBUG] webdriver-manager failed: {e}, will use local geckodriver")
            self.driver_path = None
        
        self._driver_path_cached = True

    def _init_driver(self):
        print(f"[DEBUG] Initializing Firefox browser, headless={self.headless}")
        
        # Lazy-load the driver path on first use
        self._ensure_driver_path()
        
        options = webdriver.FirefoxOptions()
        options.page_load_strategy = 'eager'
        if self.headless:
            options.add_argument("--headless")
            os.environ['MOZ_HEADLESS'] = '1'
        else:
            os.environ.pop('MOZ_HEADLESS', None)
        
        try:
            if self.driver_path:
                service = FirefoxService(self.driver_path)
                self.driver = webdriver.Firefox(service=service, options=options)
            else:
                self.driver = webdriver.Firefox(options=options)
        except Exception as e:
            print(f"[DEBUG] Failed to start Firefox: {e}, trying without cached path")
            self.driver = webdriver.Firefox(options=options)
        
        print(f"[DEBUG] Browser initialized successfully")

    def get_quota(self, username, password, service_type="Internet", debug_mode=False):
        """
        Logs in and fetches the quota using Firefox.
        Always performs a fresh login to get accurate quota values.
        """
        target_headless = not debug_mode
        print(f"[DEBUG] get_quota called: debug_mode={debug_mode}, headless={target_headless}")
        
        # Check if we need to reinitialize the driver (headless mode changed)
        need_new_driver = False
        if self.driver is None:
            need_new_driver = True
        elif self.headless != target_headless:
            print("[DEBUG] Headless mode changed, reinitializing driver...")
            need_new_driver = True
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        
        if need_new_driver:
            self.headless = target_headless
            try:
                self._init_driver()
            except Exception as e:
                raise Exception(f"Failed to start browser: {str(e)}\n{traceback.format_exc()}")
        else:
            # Reusing existing driver - clear cookies for fresh login
            print("[DEBUG] Reusing existing browser, clearing session for fresh login...")
            try:
                self.driver.delete_all_cookies()
            except:
                pass


        try:
            print("[DEBUG] Navigating to login page...")
            self.driver.get("https://my.te.eg/user/login")

            # Wait for body to ensure page loaded
            print("[DEBUG] Waiting for page content...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # Discuss body wait is fine
            
            # --- Login Steps ---
            # 1. Username
            print("[DEBUG] Looking for username field...")
            try:
                user_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="text" or @id="etisalat-input"]'))
                )
            except:
                user_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/section/main/div/div/div/div[2]/div/div[2]/div/div[1]/div/form/div/div/div/div/div/div[1]/input'))
                )
            
            user_input.clear()
            user_input.send_keys(username)
            print("[DEBUG] Username entered")

            # 2. Password
            print("[DEBUG] Looking for password field...")
            try:
                pass_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))
                )
            except:
                pass_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/section/main/div/div/div/div[2]/div/div[2]/div/div[2]/form/div/div/div/div/input'))
                )
            pass_input.clear()
            pass_input.send_keys(password)
            print("[DEBUG] Password entered")

            # 3. Service Type Selection (skip for 4G - numbers starting with 015)
            is_4g = username.startswith("015")
            
            if is_4g:
                print("[DEBUG] 4G account detected, skipping service type selection")
            else:
                print(f"[DEBUG] Selecting service type: {service_type}")
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
                    
                    def handle_alert():
                        try:
                            alert = self.driver.switch_to.alert
                            print(f"[DEBUG] Alert detected: {alert.text}, dismissing...")
                            alert.accept()
                            time.sleep(0.5)
                            return True
                        except:
                            return False

                    def safe_click(element):
                        try:
                            element.click()
                        except UnexpectedAlertPresentException:
                            handle_alert()
                            # Retry click
                            element.click()
                        except Exception:
                            # Fallback
                            ActionChains(self.driver).move_to_element(element).click().perform()

                    # Wait for dropdown to be clickable
                    service_dropdown = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "ant-select-selector"))
                    )
                    
                    # Check for alert before interacting
                    handle_alert()
                    
                    # Click dropdown safely
                    safe_click(service_dropdown)
                    
                    time.sleep(1.5)  # Wait for dropdown animation
                    print("[DEBUG] Dropdown clicked, looking for options...")
                    
                    # Check for alert again
                    handle_alert()

                    target_service = "Internet" if service_type == "Internet" else service_type
                    
                    # Wait for dropdown options to appear and be visible
                    option = WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, f"//div[contains(@class, 'ant-select-item-option-content')]//span[contains(text(), '{target_service}')]"))
                    )
                    
                    print(f"[DEBUG] Found option: {option.text}")
                    
                    # Click option safely
                    safe_click(option)
                    
                    time.sleep(1)
                    print("[DEBUG] Service type selected successfully")
                except Exception as e:
                    print(f"[DEBUG] Service selection failed: {e}")
                    # If service selection fails, the login button won't work
                    raise Exception(f"Failed to select service type: {e}")

            # 4. Login Button
            print("[DEBUG] Clicking login button...")
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "login-withecare"))
            )
            login_btn.click()
            print("[DEBUG] Login button clicked, waiting for response...")

            # 5. Check for Success or Error
            result = WebDriverWait(self.driver, 30).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CLASS_NAME, "ant-progress-circle")),
                    EC.presence_of_element_located((By.CLASS_NAME, "ant-message-error"))
                )
            )

            if "ant-message-error" in result.get_attribute("class"):
                try:
                    err_text = result.text
                except:
                    err_text = "Unknown login error"
                raise Exception(f"Login failed: {err_text}")

            print("[DEBUG] Login successful, waiting for dashboard...")

            # 6. Wait for Dashboard & Quota
            WebDriverWait(self.driver, 20).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "ant-spin-spinning"))
            )

            print("[DEBUG] Looking for quota value...")
            
            if is_4g:
                # 4G: Look for FLTE remaining value
                print("[DEBUG] 4G account - looking for FLTE quota...")
                try:
                    # Wait for the usage overview section to load
                    time.sleep(2)
                    
                    # Find the "Remaining" span and get the value before it
                    # The structure is: <span>VALUE</span><span> Remaining</span>
                    remaining_spans = self.driver.find_elements(By.XPATH, 
                        "//span[contains(text(), 'Remaining')]"
                    )
                    
                    quota_value = None
                    for remaining_span in remaining_spans:
                        parent = remaining_span.find_element(By.XPATH, "..")
                        spans = parent.find_elements(By.TAG_NAME, "span")
                        for span in spans:
                            text = span.text.strip()
                            # Look for numeric value (e.g., "31,876.02")
                            if text and text.replace(",", "").replace(".", "").isdigit():
                                quota_value = text
                                break
                        if quota_value:
                            break
                    
                    if not quota_value:
                        # Fallback: try finding by style
                        remaining_elem = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, 
                                ".//span[contains(@style, 'font-size: 2.1875rem')]"
                            ))
                        )
                        quota_value = remaining_elem.text
                    
                    # Convert from MB to GB
                    quota_mb = float(quota_value.replace(",", ""))
                    quota_gb = quota_mb / 1024
                    print(f"[DEBUG] FLTE Quota found: {quota_value} MB = {quota_gb:.2f} GB")
                    return f"{quota_gb:.2f} GB"
                    
                except Exception as e:
                    print(f"[DEBUG] 4G quota extraction failed: {e}")
                    raise Exception(f"Failed to extract 4G quota: {e}")
            else:
                # Regular Internet quota
                remaining_elem = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, 
                        ".//span[contains(@style, 'font-size: 2.1875rem') and contains(@style, 'color: var(--ec-brand-primary)')]"
                    ))
                )

                quota_value = remaining_elem.text
                print(f"[DEBUG] Quota found: {quota_value}")
                return quota_value + " GB"

        except TimeoutException as e:
            raise Exception(f"Timeout waiting for page element. The page might have changed or be slow to respond.\nDetails: {str(e)}")
        except WebDriverException as e:
            raise Exception(f"Browser error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error: {str(e)}\n{traceback.format_exc()}")

if __name__ == "__main__":
    print("Testing QuotaManager (Dry Run)...")
    print(f"Supported browsers: {QuotaManager.SUPPORTED_BROWSERS}")
