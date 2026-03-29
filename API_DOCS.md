Base URL: http://127.0.0.1:8000

OVERVIEW:

This API powers an AI-driven shopping assistant that supports conversational interaction, product retrieval, and image-based product search. It is built using FastAPI and follows RESTful design principles.

The API allows clients to:

i)Retrieve product data
ii)Perform text-based product search
iii)Upload and analyze images using AI

ENDPOINTS:

GET /
Checks if the API is running.

Response

{
  "message": "AI Shopping Assistant API is running"
}

Verify API Key

GET /check-key
Validates whether the Google Gemini API key is configured.

Response (Success)

{
  "status": "Google Gemini API key is configured"
}

Response (Failure)

{
  "status": "GOOGLE_API_KEY is not set"
}

Get All Products

GET /products
Returns the complete product catalog.

Response

[
  {
    "id": "d001",
    "name": "Floral Summer Dress",
    "category": "dress",
    "price": 49.99
  }
]

Get Product by ID

GET /products/{product_id}
Returns details of a specific product.

Response (Success)

{
  "id": "g004",
  "name": "Noise Cancelling Headphones",
  "category": "gadget",
  "price": 149.99
}

Response (Failure)

{
  "error": "Product not found"
}

Upload Image

POST /upload-image
Uploads an image and analyzes it using AI.

Request

Content-Type: multipart/form-data
Field: file (image file)

Response

{
  "filename": "headphones.jpg",
  "message": "Image uploaded and analyzed successfully",
  "ai_analysis": {
    "category": "gadget",
    "subcategory": "headphones",
    "description": "Black over-ear headphones"
  }
}

If image analysis fails:

{
  "ai_analysis": {
    "category": "unknown",
    "subcategory": "unknown"
  }
}

Chat (Text & Image Search)

POST /chat
Handles both conversational queries and product search.

Request

{
  "message": "black dress",
  "image_filename": null
}

Response

{
  "reply": "Here are some dresses in black",
  "products": [
    {
      "id": "d002",
      "name": "Black Evening Dress",
      "price": 89.99
    }
  ]
}

Image-Based Search

After uploading an image, pass the filename:

Request

{
  "message": "",
  "image_filename": "headphones.jpg"
}

Response

{
  "reply": "Here are similar headphones",
  "products": [
    {
      "id": "g004",
      "name": "Noise Cancelling Headphones",
      "price": 149.99
    }
  ]
}

ERROR HANDLING:

Status Code	Description
200	Request successful
422	Invalid input
500	Server error

NOTES:

Image analysis is performed using Google Gemini Vision API.
Image-based search currently maps detected categories to products in the catalog.
The API is designed to be lightweight and can be extended with advanced features such as vector-based similarity search or database integration.



