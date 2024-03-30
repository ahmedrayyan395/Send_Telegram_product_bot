import json
import requests
from bs4 import BeautifulSoup
import time

def send_product_data_to_telegram():
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
            product_status = soup.find("div", class_="stock unavailable").span.text.strip()

            return product_name, product_status
        except Exception as e:
            print(f"An error occurred while extracting product details for {product_url}: {str(e)}")
            return None, None

    # Fetch the HTML content of the page
    url = "https://www.dzrt.com/ar/our-products.html"
    response = requests.get(url)
    html_content = response.content

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
    bot_token = "6958486146:AAFtYb_TaInJtSSFevXDn39BCssCzj4inV4"
    chat_id = "@dezert224"  # Replace with your channel username
    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    for product_data in product_data_list:
        product_name = product_data.get("name", "")
        product_status = product_data.get("status", "")  # سيتم توفيرها في المخزون قريباً 
        product_url = product_data.get("url", "")

        # Create the message text
        message_text = f"Product Name: {product_name}\nProduct Status: {product_status}\nProduct URL: {product_url}"

        # Send the message to the Telegram channel
        params = {"chat_id": chat_id, "text": message_text}
        response = requests.post(telegram_api_url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Product data sent successfully for {product_name}")
        else:
            print(f"Failed to send product data for {product_name}. Status code: {response.status_code}")

# Main loop to run the code every minute
while True:
    send_product_data_to_telegram()
    # Sleep for 60 seconds (1 minute)
    time.sleep(60)
