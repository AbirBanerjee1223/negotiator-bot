import random
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from transformers import pipeline
from textblob import TextBlob

app = FastAPI()

# Initialize the text generation pipeline with DistilGPT2
generator = pipeline('text-generation', model='distilgpt2')

# Initialize sentiment analysis pipeline
sentiment_analyzer = pipeline('sentiment-analysis')

# Sample product data for negotiation with updated prices
products = {
    "laptop": {"price": 50000, "min_price": 45000},      # Original: 50000, Min: 45000
    "smartphone": {"price": 30000, "min_price": 25000},  # Original: 30000, Min: 25000
    "headphones": {"price": 3000, "min_price": 2500},    # Original: 6000, Min: 5000
    "tablet": {"price": 25000, "min_price": 12000},      # Original: 25000, Min: 22000
}

# Request body model
class NegotiationRequest(BaseModel):
    product: str
    offer_statement: str
    chat_history: str

# Function to analyze sentiment
def analyze_sentiment(message):
    analysis = TextBlob(message)
    return analysis.sentiment.polarity

# Function to generate AI response using the new prompt
def generate_ai_response(product_name, offer_price, original_price, counter_offer):
    prompt = f"""
You are a shopkeeper negotiating the price of a {product_name}. The customer has offered Rs. {offer_price}, but your original price is Rs. {original_price}. Provide a simple reason for why this new price is fair, such as maintaining quality service or covering the product’s costs. Avoid any kind of numbers in the reply. Just provide reasons in 1 line.
"""
    response = generator(prompt, max_length=500, num_return_sequences=1)[0]['generated_text']
    return response.split('\n')[-1].strip()

# Improved function to extract price from offer statement
def extract_price(offer_statement):
    words = offer_statement.split()
    for word in words:
        cleaned_word = ''.join(char for char in word if char.isdigit() or char == '.')
        if cleaned_word:
            try:
                return int(float(cleaned_word))
            except ValueError:
                pass
    return None

# Strategic negotiation logic
def strategic_negotiation(product, original_price, min_price, offer_statement, round):
    offer_price = extract_price(offer_statement)
    
    # Check for termination phrases
    if "bye" in offer_statement.lower() or "no deal" in offer_statement.lower():
        return "Negotiation ended. Thank you for your time!", True

    # Sentiment analysis
    sentiment_result = sentiment_analyzer(offer_statement)[0]
    sentiment_score = sentiment_result['score'] if sentiment_result['label'] == 'POSITIVE' else -sentiment_result['score']

    price_range = original_price - min_price

    # Adjust acceptance threshold based on sentiment and round
    acceptance_threshold = original_price - int(price_range * (0.1 + (round * 0.05) - (sentiment_score * 0.05)))

    if offer_price >= acceptance_threshold:
        return f"Excellent! I accept your offer of Rs. {offer_price}. It's a deal!", True
    
    if offer_price < min_price:
        # Randomly reduce price between 0.01% and 0.1% if the offer is below the minimum price
        reduction_percentage = random.randint(1, 10) / 10000.0  # 0.01% to 0.1%
        counter_offer = max(min_price, original_price - int(original_price * reduction_percentage))
        ai_response = generate_ai_response(product, offer_price, original_price, counter_offer)
        return f"{ai_response} How about Rs. {counter_offer} for the {product}?", False
    
    # After 3 attempts, reject if still below minimum
    if round >= 3 and offer_price < min_price:
        return f"After careful consideration, I must decline your offer of Rs. {offer_price}. Thank you for your time!", True
    
    # Counter offer logic
    counter_offer = max(min_price, original_price - int(price_range * (0.1 + (round * 0.05) - (sentiment_score * 0.05))))
    ai_response = generate_ai_response(product, offer_price, original_price, counter_offer)
    
    return f"{ai_response} How about Rs. {counter_offer} for the {product}?", False

# Negotiation logic
@app.post("/negotiate")
async def negotiate(product: str = Form(...), offer_statement: str = Form(...), chat_history: str = Form(...)):
    if product not in products:
        raise HTTPException(status_code=400, detail="Product not available")

    product_data = products[product]
    original_price = product_data["price"]
    min_price = product_data["min_price"]

    # Extract the negotiation round from chat history
    round = len(chat_history.split("Customer:")) - 1

    # Check for negotiation limit
    if round >= 8:
        return {
            "original_price": original_price,
            "offer_statement": offer_statement,
            "ai_response": f"As there is no improvement, I must decline any further negotiation. Thank you for your time!",
            "deal_made": True,
            "product": product
        }

    ai_response, deal_made = strategic_negotiation(product, original_price, min_price, offer_statement, round)

    return {
        "original_price": original_price,
        "offer_statement": offer_statement,
        "ai_response": ai_response,
        "deal_made": deal_made,
        "product": product
    }

# HTML form for easy chat interface
@app.get("/", response_class=HTMLResponse)
def chat_interface():
    return """
    <html>
        <head>
            <title>Strategic Negotiation Chatbot</title>
            <script>
                let chatHistory = "";
                let currentProduct = "";
                let negotiationComplete = false;

                function addMessageToChatBox(sender, message) {
                    const chatBox = document.getElementById('chatBox');
                    const messageElement = document.createElement('p');
                    messageElement.textContent = `${sender}: ${message}`;
                    chatBox.appendChild(messageElement);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                function submitOffer() {
                    if (negotiationComplete) {
                        alert("Negotiation is complete. Please refresh the page to start a new negotiation.");
                        return false;
                    }

                    const form = document.getElementById('negotiationForm');
                    const formData = new FormData(form);
                    
                    if (!currentProduct) {
                        currentProduct = formData.get('product');
                        addMessageToChatBox('System', `Starting negotiation for ${currentProduct}. Original price: Rs. ${getOriginalPrice(currentProduct)}`);
                    } else {
                        formData.set('product', currentProduct);
                    }
                    
                    formData.append('chat_history', chatHistory);

                    const offerStatement = formData.get('offer_statement');
                    addMessageToChatBox('Customer', offerStatement);
                    
                    fetch('/negotiate', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        addMessageToChatBox('Bot', data.ai_response);
                        
                        chatHistory += `Customer: ${offerStatement}\n`;
                        chatHistory += `Bot: ${data.ai_response}\n`;
                        
                        if (data.deal_made) {
                            negotiationComplete = true;
                            document.getElementById('submitButton').disabled = true;
                            addMessageToChatBox('System', 'Negotiation complete!');
                        }
                        
                        // Clear the offer statement input
                        document.getElementById('offer_statement').value = '';
                        
                        // Hide the product selection after the first offer
                        document.getElementById('productSelection').style.display = 'none';
                    });
                    
                    return false;
                }

                function getOriginalPrice(product) {
                    const prices = {
                        "laptop": 50000,
                        "smartphone": 30000,
                        "headphones": 3000,
                        "tablet": 25000
                    };
                    return prices[product] || "N/A";
                }
            </script>
            <style>
                #chatBox {
                    height: 300px;
                    border: 1px solid #ccc;
                    overflow-y: scroll;
                    padding: 10px;
                    margin-bottom: 10px;
                }
            </style>
        </head>
        <body>
            <h1>Strategic Negotiation Chatbot</h1>
            <div id="chatBox"></div>
            <form id="negotiationForm" onsubmit="return submitOffer()">
                <div id="productSelection">
                    <label for="product">Product:</label>
                    <select name="product" id="product" required>
                        <option value="laptop">Laptop</option>
                        <option value="smartphone">Smartphone</option>
                        <option value="headphones">Headphones</option>
                        <option value="tablet">Tablet</option>
                    </select><br><br>
                </div>
                <label for="offer_statement">Your Offer (with justification):</label>
                <textarea name="offer_statement" id="offer_statement" required rows="4" cols="50"></textarea><br><br>
                <button type="submit" id="submitButton">Submit Offer</button>
            </form>
        </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
