# Strategic Negotiation Chatbot

This is a FastAPI-based negotiation chatbot that simulates a price negotiation between a customer and a supplier. The chatbot uses AI to respond to customer offers and employs sentiment analysis to determine the best negotiation strategy.

## Features

- **AI-Powered Negotiation**: Utilizes the DistilGPT2 model for generating persuasive responses.
- **Sentiment Analysis**: Analyzes customer sentiment using TextBlob to adjust negotiation tactics.
- **Product Negotiation**: Supports negotiation for various products with predefined price ranges.
- **Web Interface**: Provides a simple HTML interface for users to interact with the chatbot.

## Technologies Used

- Python
- FastAPI
- Transformers (Hugging Face)
- TextBlob
- HTML/CSS for the frontend

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   
2. **Install dependencies**:

   ```bash
   pip install requirements.txt

3. **Run the application**:

   ```bash
   python negotiator.py

4. **Access the chatbot**:

Open your browser and navigate to http://127.0.0.1:8000.


## Usage

- Select a product from the dropdown menu.
- Enter your offer statement, including your proposed price.
- The chatbot will respond with a counteroffer or accept your offer based on its negotiation logic.
- The negotiation will end after 8 rounds or if you type "bye" or "no deal".

## Example Products and Prices

| Product      | Original Price | Minimum Price |
|--------------|----------------|---------------|
| Laptop       | Rs. 50,000    | Rs. 45,000    |
| Smartphone   | Rs. 20,000    | Rs. 17,000    |
| Headphones   | Rs. 3,000     | Rs. 2,500     |
| Tablet       | Rs. 25,000    | Rs. 23,000    |
