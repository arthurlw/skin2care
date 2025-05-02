# work with this file !!

import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re

class SkinSortScraper:
    def __init__(self, output_dir='scraped_products'):
        self.base_url = "https://skinsort.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.driver = None
        self.categories = {
            'Makeup Removers': '/products/makeup-removers',
            'Face Cleansers': '/products/face-cleansers',
            'Exfoliators': '/products/exfoliators',
            'Toners': '/products/toners',

            'Wash Off Masks': '/products/wash-off-masks',
            'Sheet Masks': '/products/sheet-masks',
            'Overnight Masks': '/products/overnight-masks',

            'Ampoules': '/products/ampoules',
            'Essences': '/products/essences',
            'Serums': '/products/serums',
            'Facial Treatments': '/products/facial-treatments',
            'Emulsions': '/products/emulsions',

            'Oils': '/products/oils',
            'Night Moisturizers': '/products/night-moisturizers',
            'Day Moisturizers': '/products/day-moisturizers',
            'General Moisturizers': '/products/general-moisturizers',

            'Eye Moisturizers': '/products/eye-moisturizers',
            'Eye Masks': '/products/eye-masks',

            'Sunscreens': '/products/sunscreens',
            'Tanning': '/products/tanning',
            'After Sun Care': '/products/after-sun-care',

            'Lip Moisturizers': '/products/lip-moisturizers',
            'Lip Masks': '/products/lip-masks',
        }
        # Create output directory if it doesn't exist
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.initialize_selenium()
        self.initialize_categories()


    def initialize_selenium(self):
        """Set up Selenium WebDriver"""
        options = Options()
        options.headless = True  # Run browser in headless mode (no GUI)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


    def initialize_categories(self):
        """Extract all available product categories from the website"""
        try:
            self.driver.get(self.base_url)  # Navigate to the base URL using Selenium
            time.sleep(2)  # Wait for the page to load
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            category_links = soup.select('a.hover\\:underline[href^="/products/"]')
            count = 0

            for link in category_links:
                category_name = link.text.strip()
                category_url = link['href']
                self.categories[category_name] = category_url

            print(f"Initialized {len(self.categories)} product categories")
        except Exception as e:
            print(f"Error initializing categories: {str(e)}")


    def scrape_category(self, category_name, category_url):
        """Scrape all products in a specific category"""
        full_url = f"{self.base_url}{category_url}"
        self.driver.get(full_url)
        time.sleep(3)  # Wait for initial load

        # Handle popup (only once)
        try:
            close_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[data-modal-presentation-target="dismissSignUpModal"]')
            self.driver.execute_script("arguments[0].click();", close_btn)
            print("Closed popup.")
            time.sleep(1)
        except Exception:
            print("No popup found.")

        # Click "Load More" button repeatedly
        while True:
            try:
                load_more_button = self.driver.find_element(
                    By.XPATH,
                    '//button[contains(@class, "bg-indigo-800") and contains(@class, "font-header")]'
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(1)
                load_more_button.click()
                print("Clicked Show More Products...")
                time.sleep(3)
            except Exception as e:
                print(f"No more buttons or error: {e}")
                break

        # Parse the fully loaded page
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        product_links = soup.select('a[href^="/products/"][data-turbo-frame="_top"]')
        if not product_links:
            product_links = soup.select('a[href^="/products/"][class*="relative w-full"]')

        print(f"Found {len(product_links)} products in {category_name}")

        category_products = []
        for link in product_links:
            try:
                product_href = link['href']
                product_url = f"{self.base_url}{product_href}"
                product_data = self.get_product_data(product_url, category_name)
                if product_data:
                    category_products.append(product_data)

                time.sleep(1)  # Avoid overwhelming the server
            except Exception as e:
                print(f"Error scraping product in {category_name}: {str(e)}")

        return category_products


    def scrape_all_categories(self):
        """Scrape products from all categories with error recovery"""
        all_products = {}
        
        for category_name, category_url in self.categories.items():
            print(f"\nScraping category: {category_name}")
            try:
                # Check if driver is still valid, recreate if needed
                try:
                    # Quick test to see if the driver is still responsive
                    self.driver.current_url
                except Exception as e:
                    print(f"Driver session invalid, recreating: {str(e)}")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                    self.initialize_selenium()
                
                # Now scrape the category
                category_products = self.scrape_category(category_name, category_url)
                if category_products:
                    all_products[category_name] = category_products
                    
                    # Save category-specific JSON
                    category_filename = f"{category_name.lower().replace(' ', '_')}_products.json"
                    category_filepath = os.path.join(self.output_dir, category_filename)
                    with open(category_filepath, 'w', encoding='utf-8') as f:
                        json.dump(category_products, f, indent=2, ensure_ascii=False)
                    print(f"Saved {len(category_products)} products for {category_name}")
            except Exception as e:
                print(f"Error scraping category {category_name}: {str(e)}")
                # Try to recreate the driver for the next category
                try:
                    if self.driver:
                        self.driver.quit()
                except:
                    pass
                self.initialize_selenium()

        
        # Save comprehensive JSON
        all_products_filepath = os.path.join(self.output_dir, 'all_products.json')
        with open(all_products_filepath, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        
        return all_products

        
    def get_product_data(self, product_url, category_name):
        self.driver.get(product_url)
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Trait icons with alt-text (fixes the "Not vegan" issue)
        icon_traits = {
            "alcohol_free": "alcohol-free",
            "eu_allergen_free": "eu-allergen-free",
            "fragrance_free": "fragrance-free",
            "oil_free": 'oil-free',
            'paraben_free': 'paraben-free',
            'silicon_free': 'silicon-free',
            'sulfate_free': 'sulfate-free',
            "cruelty_free": "cruelty-free",
            "fungal_acne_safe": "fungal-acne-safe",
            "reef_safe": "reef-safe",
            "vegan": "vegan",
        }
   
        product_data = {
            "product_url": product_url,
            "product_name": "",
            "brand": "",
            "price": "",
            "rating": "",
            "alcohol_free": None,
            "eu_allergen_free": None,
            "fragrance_free": None,
            "oil_free": None,
            'paraben_free': None,
            'silicon_free': None,
            'sulfate_free': None,
            "cruelty_free": None,
            "fungal_acne_safe": None,
            "reef_safe": None,
            "vegan": None,
            "category": category_name,
            "ingredients": [],
            "pros": [],
            "cons": [],
        }


        # Basic info
        product_name_elem = soup.select_one('h1')
        if product_name_elem:
            full_text = product_name_elem.get_text(separator="\n").strip()
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            if len(lines) >= 2:
                product_data["brand"] = lines[0]
                product_data["product_name"] = " ".join(lines[1:])
            elif len(lines) == 1:
                product_data["product_name"] = lines[0]


        # Look for all img tags with known trait icons
        trait_icons = soup.select('img[alt]')

        for img in trait_icons:
            alt = img.get('alt', '').strip().lower()  # example: 'vegan', 'not vegan'
            for key, label in icon_traits.items():
                if alt == label:
                    product_data[key] = True
                elif alt == f"not {label}":
                    product_data[key] = False

        for key, label in icon_traits.items():
            if product_data.get(key) is True:
                product_data[key] = label
            elif product_data.get(key) is False:
                product_data[key] = f"Not {label}"
            # Leave None as-is

        # Price & Rating
        price_elem = soup.select_one('span.text-warm-gray-800.text-sm.underline.font-semibold')
        if price_elem:
            product_data["price"] = price_elem.text.strip()


        rating_elem = soup.select_one('span.font-bold.tracking-tight')
        if rating_elem:
            rating_text = rating_elem.text.strip()
            try:
                product_data["rating"] = rating_text
            except ValueError:
                # In case the text can't be converted to a float
                product_data["rating"] = ""


        # Ingredients section
        ingredients_section = soup.select_one('div[id="ingredients-section"]')
        ingredients_list = []  # Temporary list to collect ingredients

        if ingredients_section:
            # Look for spans with data-ingredient-name-for attribute
            ingredient_spans = ingredients_section.select('span[data-ingredient-name-for]')
            if ingredient_spans:
                # Clean each ingredient text by removing newlines and excess whitespace
                ingredients_list = [re.sub(r'\s+', ' ', span.get_text()).strip() for span in ingredient_spans]
            else:
                # Try list format as a fallback
                ingredients_items = ingredients_section.select('li')
                if ingredients_items:
                    ingredients_list = [re.sub(r'\s+', ' ', item.text).strip() for item in ingredients_items]
                else:
                    # Fallback: get text from a tags inside p (with x-ref="ingredientsList")
                    paragraph = ingredients_section.find('p', {'x-ref': 'ingredientsList'})
                    if paragraph:
                        ingredients_links = paragraph.find_all('a')
                        ingredients_list = [re.sub(r'\s+', ' ', ingredient.text).strip() for ingredient in ingredients_links]

        # Join all ingredients with commas into a single string
        if ingredients_list:
            product_data["ingredients"] = ", ".join(ingredients_list)
        else:
            product_data["ingredients"] = "No ingredients found"

        # Another fallback: Try to find any spans with data-ingredient-name-for attribute anywhere
        if product_data["ingredients"] == "No ingredients found":
            all_ingredient_spans = soup.select('span[data-ingredient-name-for]')
            if all_ingredient_spans:
                ingredients_list = [re.sub(r'\s+', ' ', span.get_text()).strip() for span in all_ingredient_spans]
                product_data["ingredients"] = ", ".join(ingredients_list)

        # Pros / Cons
        # Pros section
        pros_items = soup.select('button[id^="ingredient-attribute-best"]')
        product_data["pros"] = ", ".join(button.select_one('span.font-semibold').text.strip() for button in pros_items)

        # Cons section
        cons_items = soup.select('button[id^="ingredient-attribute-worst"]')
        product_data["cons"] = ", ".join(button.select_one('span.font-semibold').text.strip() for button in cons_items)

        # Image
        try:
            img_elem = soup.select_one('img.aspect-square') or soup.select_one('img.h-64')
            if not img_elem:
                img_elems = soup.select('img')
                img_elem = img_elems[0] if img_elems else None
            if img_elem:
                product_data["image_url"] = img_elem.get('src', '')
        except Exception as e:
            print(f"Error extracting image: {str(e)}")
            product_data["image_url"] = ""

        return product_data

def main():
    
    scraper = SkinSortScraper()  

    try:
        # Scrape all categories
        all_products = scraper.scrape_all_categories()
        
        print(f"\nTotal products scraped: {sum(len(products) for products in all_products.values())}")
    except Exception as e:
        print(f"An error occurred during scraping: {str(e)}")
    finally:
        # Close the browser
        if scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    main()