AI Shopping Assistant

This project is an AI-powered shopping assistant that allows users to search for products using both text and images. It is inspired by modern conversational commerce systems and demonstrates how AI can be integrated into a simple e-commerce experience.

The application supports basic conversation, product search through natural language, and image-based product identification. All recommendations are generated from a predefined product catalog.

Features
Supports conversational queries (e.g., “What can you do?”)
Enables text-based product search (e.g., “black dress”, “cheap earbuds”)
Allows image-based product search through AI-powered image understanding
Displays relevant products from a structured catalog
Technology Stack
Backend: FastAPI (Python)
Frontend: HTML, CSS, JavaScript
AI Integration: Google Gemini Vision API
Data Storage: JSON-based product catalog
Configuration: Environment variables using .env

Technology Stack
Backend: FastAPI (Python)
Frontend: HTML, CSS, JavaScript
AI Integration: Google Gemini Vision API
Data Storage: JSON-based product catalog
Configuration: Environment variables using .env

AI-AGENT/
├── backend/
│   ├── main.py
│   └── products.json
├── frontend/
│   ├── index.html
│   └── images/
├── .env
├── README.md

Setup Instructions
1)Install required dependencies:
pip install fastapi uvicorn python-multipart python-dotenv google-generativeai pillow

2)Create a .env file and add the API key:
GOOGLE_API_KEY=our_api_key_here

3)Start the backend server:
python -m uvicorn backend.main:app --reload

4)start the browser

Usage

Users can interact with the assistant in two ways:

Text Search: Enter product-related queries such as “red dress under 50” or “bluetooth speaker”.
Image Search: Upload an image, and the system will identify the product type and display similar items from the catalog.

Summary
This project is an AI-powered shopping assistant designed to enhance product discovery through both text and image-based search. Built using FastAPI for the backend and a lightweight HTML, CSS, and JavaScript frontend, the system enables users to interact conversationally while exploring a predefined product catalog. Users can search for items using natural language queries such as “black dress” or “cheap earbuds,” and the system intelligently filters relevant products based on attributes like category, color, and price. Additionally, the application supports image-based search by analyzing uploaded images using the Google Gemini Vision API to identify the product type and recommend similar items from the catalog. The project demonstrates the integration of AI capabilities into a simple e-commerce workflow, highlighting how conversational interfaces and image understanding can improve user experience. It is designed as a scalable foundation that can be extended with advanced features such as vector-based image similarity and database integration.
