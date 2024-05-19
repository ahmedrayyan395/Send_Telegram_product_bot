import json
import requests
from bs4 import BeautifulSoup
import time

# Global list to store product names that are successfully sent
sent_products = []

# Variable to store the time of the last clearing of the sent_products list
last_clear_time = time.time()

# Function to extract product details
def extract_product_details(product_url):
    try:
        # Fetch the HTML content of the product page
        response = requests.get(product_url)
        html_content = response.content
        
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract product name
        product_name = soup.find("span", class_="base", itemprop="name").text.strip()

        # Extract product status
        product_status_element = soup.find("div", class_="stock available").span
        product_status = product_status_element.text.strip() if product_status_element else None

        return product_name, product_status
    except Exception as e:
        print(f"An error occurred while extracting product details for {product_url}: {str(e)}")
        return None, None

# Function to send product data to Telegram
def send_product_data_to_telegram():
    global sent_products, last_clear_time  # Access the global variables

    # Example usage
    url = "https://www.dzrt.com/ar/our-products.html"
    html_content = fetch_url_with_retry(url)
    if html_content:
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all product links
        product_links = [a["href"] for a in soup.find_all("a", class_="product-item-link")]

        # Initialize a list to store product data
        product_data_list = []

        # Loop through each product link to extract details
        for product_link in product_links:
            product_info = {}
            product_info["url"] = product_link

            # Extract product details
            product_name, product_status = extract_product_details(product_link)
            if product_name and product_status:
                product_info["name"] = product_name
                product_info["status"] = product_status
                product_data_list.append(product_info)

                # Print product details
                print(f"Product Name: {product_name}")
                print(f"Product Status: {product_status}")
                print("-" * 50)

        # Print the product data list
        print("Product Data List:")
        for product_data in product_data_list:
            print(product_data)

        # Convert the product data list to JSON
        payload = json.dumps(product_data_list)

        # Send the product data to the Telegram channel using the bot
        bot_token = "6758564840:AAG1L-yn-5-FSru-jZW_oN261YGi-EEqTcs"
        chat_id = "@DZRT_VIPGold"
        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        for product_data in product_data_list:
            product_name = product_data.get("name", "")
            product_status = product_data.get("status", "")
            product_url = product_data.get("url", "")

            # Check if the product status is "متوفر" and it's not in the list of sent products
            if product_status == "متوفر" and product_name not in sent_products:
                # Create the message text
                message_text = f"Product Name: {product_name}\nProduct Status: {product_status}\nProduct URL: {product_url}"

                # Send the message to the Telegram channel
                params = {"chat_id": chat_id, "text": message_text}
                response = requests.post(telegram_api_url, params=params)

                # Check if the request was successful
                if response.status_code == 200:
                    print(f"Product data sent successfully for {product_name}")
                    # Add the product name to the list of sent products
                    sent_products.append(product_name)
                else:
                    print(f"Failed to send product data for {product_name}. Status code: {response.status_code}")

        # Clear the list of sent products every 60 minutes
        if time.time() - last_clear_time >= 3600:
            sent_products.clear()
            last_clear_time = time.time()  # Update the last clear time

def fetch_url_with_retry(url, max_retries=7, delay=1):
    retries = 0
    while retries < max_retries:
        try:
            # Make the request
            response = requests.get(url)
            # If the request was successful, return the content
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
        except requests.RequestException as e:
            # If an error occurs, print the error and retry after a delay
            print(f"An error occurred: {e}")
        
        # Increment the retry counter
        retries += 1
        # Delay before retrying
        time.sleep(delay)
    
    # If max retries reached and no successful response received, return None
    print(f"Max retries reached for URL: {url}")
    return None

# Main loop to run the code every minute
while True:
    send_product_data_to_telegram()
    # Sleep for 60 seconds (1 minute)
    time.sleep(10)
