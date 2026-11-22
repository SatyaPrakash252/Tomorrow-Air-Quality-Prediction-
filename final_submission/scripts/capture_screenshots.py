"""
capture_screenshots.py
──────────────────────
Captures live high-resolution 1920x1080 screenshots of the running VayuDrishti application:
1. Landing/overview (screenshot_landing.png)
2. City dashboard for ML-tier city (screenshot_dashboard_ml.png)
3. City dashboard for AI-tier city (screenshot_dashboard_ai.png)
4. City selector search (screenshot_city_search.png)
5. Health risk page (screenshot_health_risk.png)
6. Alerts page (screenshot_alerts.png)
7. Research/models page (screenshot_research_models.png)
8. API docs page (screenshot_api_docs.png)
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT_ASSETS_DIR = os.path.join(PROJECT_ROOT, "final_submission", "report_assets")
os.makedirs(REPORT_ASSETS_DIR, exist_ok=True)

def main():
    print("=" * 70)
    print(" CAPTURING LIVE APP SCREENSHOTS FOR THESIS & PRESENTATION")
    print("=" * 70)

    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=opts)

    try:
        # 1. Landing Page
        print("  1. Capturing Landing Page...")
        driver.get("http://localhost:5173/")
        time.sleep(3)
        driver.save_screenshot(os.path.join(REPORT_ASSETS_DIR, "screenshot_landing.png"))

        # 2. City Dashboard (ML Tier - Delhi)
        print("  2. Capturing ML-Tier City Dashboard (Delhi)...")
        driver.get("http://localhost:5173/dashboard")
        time.sleep(4)
        driver.save_screenshot(os.path.join(REPORT_ASSETS_DIR, "screenshot_dashboard_ml.png"))

        # 3. City Selector Search
        print("  3. Capturing City Selector Search...")
        try:
            # Click the city selector dropdown button in the navbar or page
            btn = driver.find_elements(By.TAG_NAME, "button")
            # Look for button that opens city search or click selector
            for b in btn:
                if "Delhi" in b.text or "Select" in b.text or "City" in b.text or "Search" in b.text:
                    b.click()
                    time.sleep(1)
                    break
            driver.save_screenshot(os.path.join(REPORT_ASSETS_DIR, "screenshot_city_search.png"))
        except Exception as e:
            print(f"Selector click note: {e}")
            driver.save_screenshot(os.path.join(REPORT_ASSETS_DIR, "screenshot_city_search.png"))

        # 4. City Dashboard (AI Tier - Bhubaneswar)
        print("  4. Capturing AI-Tier City Dashboard (Bhubaneswar)...")
        # Direct URL or state update
        driver.get("http://localhost:5173/dashboard?city=Bhubaneswar")
        time.sleep(3)
        # Check if selector is needed, or click Bhubaneswar
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if inputs:
                inputs[0].clear()
                inputs[0].send_keys("Bhubaneswar")
                time.sleep(1)
                b_elems = driver.find_elements(By.XPATH, "//*[contains(text(), 'Bhubaneswar')]")
                if b_elems:
                    b_elems[0].click()
                    time.sleep(2)
        except Exception:
            pass
        driver.save_screenshot(os.path.join(REPORT_ASSETS_DIR, "screenshot_dashboard_ai.png"))

        # 5. Health Risk Page
        print("  5. Capturing Health Risk Page...")
        driver.get("http://localhost:5173/risk")
        time.sleep(3)
        driver.save_screenshot(os.path.join(REPORT_ASSETS_DIR, "screenshot_health_risk.png"))

        # 6. Alerts Page
        print("  6. Capturing Public Alerts Page...")
        driver.get("http://localhost:5173/alerts")
        time.sleep(3)
        driver.save_screenshot(os.path.join(REPORT_ASSETS_DIR, "screenshot_alerts.png"))

        # 7. Research / Models / About Page
        print("  7. Capturing Research & Architecture Page...")
        driver.get("http://localhost:5173/about")
        time.sleep(3)
        driver.save_screenshot(os.path.join(REPORT_ASSETS_DIR, "screenshot_research_models.png"))

        # 8. API Documentation (FastAPI Swagger Docs)
        print("  8. Capturing OpenAPI /docs Page...")
        driver.get("http://localhost:8000/docs")
        time.sleep(3)
        driver.save_screenshot(os.path.join(REPORT_ASSETS_DIR, "screenshot_api_docs.png"))

        print("\n[OK] All 8 application screenshots successfully captured and saved to report_assets/")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
