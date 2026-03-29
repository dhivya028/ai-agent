from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import google.generativeai as genai
import PIL.Image
import json
import os
import io

# Loading API keys from .env file
load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI()

# Serving product images as static files
app.mount("/images", StaticFiles(directory="frontend/images"), name="images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loading product catalog
with open("backend/products.json", "r") as file:
    PRODUCTS = json.load(file)

image_analysis_cache = {}
class ChatRequest(BaseModel):
    message: str
    image_filename: Optional[str] = None

# analyze image
def analyze_image_with_gemini(image_bytes: bytes):
    """Try Gemini Vision first, fall back to smart filename detection."""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        image = PIL.Image.open(io.BytesIO(image_bytes))
        prompt = """Look at this image and identify the product shown.
Respond with ONLY a valid JSON object, no extra text, no markdown.
Format: {"category": "...", "subcategory": "...", "description": "..."}
category: dress, accessory, gadget, or unknown
subcategory: dress, headphones, earbuds, speaker, smartwatch, charger, watch, bag, backpack, sunglasses, necklace, or unknown
description: one short sentence about what you see"""

        response = model.generate_content([image, prompt])
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()
        return json.loads(raw_text)

    except Exception as e:
        print(f"[Gemini failed, using filename fallback] {e}")
        return None  # Signal to use filename fallback


def detect_from_filename(filename: str):
    """Smart filename-based fallback detection."""
    name = filename.lower().replace("-", " ").replace("_", " ")
    name = os.path.splitext(name)[0]

    checks = [
        (["headphone", "headset", "over ear"], "gadget", "headphones", "Headphones"),
        (["earbud", "earphone", "airpod", "tws"], "gadget", "earbuds", "Wireless Earbuds"),
        (["speaker", "boombox"], "gadget", "speaker", "Bluetooth Speaker"),
        (["smartwatch", "smart watch", "fitbit"], "gadget", "smartwatch", "Smart Watch"),
        (["charger", "powerbank", "power bank"], "gadget", "charger", "Portable Charger"),
        (["watch", "timepiece"], "accessory", "watch", "Wrist Watch"),
        (["backpack", "rucksack"], "accessory", "backpack", "Backpack"),
        (["bag", "handbag", "purse", "tote"], "accessory", "bag", "Handbag"),
        (["sunglass", "shades", "eyewear"], "accessory", "sunglasses", "Sunglasses"),
        (["necklace", "chain", "jewelry"], "accessory", "necklace", "Necklace"),
        (["dress", "gown", "midi", "maxi", "frock"], "dress", "dress", "Dress"),
    ]
    for keywords, cat, sub, desc in checks:
        if any(k in name for k in keywords):
            return {"category": cat, "subcategory": sub, "description": desc}

    return {"category": "unknown", "subcategory": "unknown",
            "description": "Please rename image (e.g. headphones.jpg, dress.jpg)"}

# HELPERS
def get_products_by_category(category: str):
    return [p for p in PRODUCTS if p["category"] == category]

# UPLOAD IMAGE — powered by Google Vision
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    content = await file.read()

    analysis = analyze_image_with_gemini(content)
    if analysis is None:
        # Gemini failed — use smart filename detection
        analysis = detect_from_filename(file.filename)

    # Cache result by filename
    image_analysis_cache[file.filename] = analysis

    return {
        "filename":    file.filename,
        "content_type": file.content_type,
        "message":     "Image uploaded and analyzed successfully",
        "ai_analysis": analysis
    }

# CHAT — text + image search
@app.post("/chat")
def chat(request: ChatRequest):
    user_message = request.message.lower().strip()
    products = PRODUCTS

    #IMAGE SEARCH 
    if request.image_filename:
        analysis = image_analysis_cache.get(request.image_filename)

        if not analysis:
            return {
                "reply": " Please upload the image first, then click Send.",
                "products": []
            }

        detected_category = analysis.get("category",    "unknown")
        detected_sub      = analysis.get("subcategory", "unknown")
        description       = analysis.get("description", "a product")

        if detected_category == "dress":
            filtered = get_products_by_category("dress")
            reply = f"I detected: {description} . Here are similar dresses!"

        elif detected_category == "gadget":
            filtered = get_products_by_category("gadget")
            if detected_sub == "headphones":
                filtered = [p for p in filtered if "headphone" in p["name"].lower()]
                reply = f"I detected: {description} . Here are similar headphones!"
            elif detected_sub == "earbuds":
                filtered = [p for p in filtered if "earbud" in p["name"].lower()]
                reply = f"I detected: {description} . Here are similar earbuds!"
            elif detected_sub == "speaker":
                filtered = [p for p in filtered if "speaker" in p["name"].lower()]
                reply = f"I detected: {description} . Here are similar speakers!"
            elif detected_sub == "smartwatch":
                filtered = [p for p in filtered if "smart" in p["name"].lower()]
                reply = f"I detected: {description} . Here are similar smartwatches!"
            elif detected_sub == "charger":
                filtered = [p for p in filtered if "charger" in p["name"].lower()]
                reply = f"I detected: {description} . Here are similar chargers!"
            else:
                reply = f"I detected: {description} . Here are similar gadgets!"
            if not filtered:
                filtered = get_products_by_category("gadget")

        elif detected_category == "accessory":
            filtered = get_products_by_category("accessory")
            if detected_sub == "watch":
                filtered = [p for p in filtered if "watch" in p["name"].lower()]
                reply = f"I detected: {description} . Here are similar watches!"
            elif detected_sub == "bag":
                filtered = [p for p in filtered if "bag" in p["name"].lower()]
                reply = f"I detected: {description} . Here are similar bags!"
            elif detected_sub == "backpack":
                filtered = [p for p in filtered if "backpack" in p["name"].lower()]
                reply = f"I detected: {description} . Here are similar backpacks!"
            elif detected_sub == "sunglasses":
                filtered = [p for p in filtered if "sunglass" in p["name"].lower()]
                reply = f"I detected: {description} . Here are similar sunglasses!"
            elif detected_sub == "necklace":
                filtered = [p for p in filtered if "necklace" in p["name"].lower()]
                reply = f"I detected: {description} . Here are similar necklaces!"
            else:
                reply = f"I detected: {description} . Here are similar accessories!"
            if not filtered:
                filtered = get_products_by_category("accessory")

        else:
            filtered = []
            reply = (
                f"I analyzed your image and detected: {description}. "
                f"This doesn't match our catalog. "
                f"We carry: dresses, accessories (bags, watches, sunglasses, necklaces), "
                f"and gadgets (headphones, earbuds, speakers, smartwatches, chargers)."
            )

        return {"reply": reply, "products": filtered}

    #TEXT SEARCH
    if "name" in user_message:
        return {"reply": "I am your AI Shopping Assistant "}

    elif "what can you do" in user_message:
        return {
            "reply": (
                "I can help you find products by text or image! \n"
                "• Type what you're looking for (e.g. 'black dress', 'cheap earbuds')\n"
                "• Upload ANY photo of a product and I'll find similar items!"
            )
        }

    elif "dress" in user_message:
        filtered = [p for p in products if p["category"] == "dress"]
        if "black" in user_message:
            filtered = [p for p in filtered if p["color"] == "black"]
        if "blue" in user_message:
            filtered = [p for p in filtered if p["color"] == "blue"]
        if "red" in user_message:
            filtered = [p for p in filtered if p["color"] == "red"]
        if "cheap" in user_message or "budget" in user_message or "under 50" in user_message:
            filtered = [p for p in filtered if p["price"] < 50]
        if not filtered:
            return {"reply": "Sorry, I couldn't find matching dresses ", "products": []}
        reply = "Here are some dresses"
        if "black" in user_message: reply += " in black"
        if "blue"  in user_message: reply += " in blue"
        if "red"   in user_message: reply += " in red"
        if "cheap" in user_message or "budget" in user_message: reply += " under budget"
        reply += " "
        return {"reply": reply, "products": filtered}

    elif any(w in user_message for w in ["accessory", "bag", "handbag", "watch", "watches", "sunglasses", "necklace", "backpack"]):
        filtered = [p for p in products if p["category"] == "accessory"]
        if "watch"     in user_message: filtered = [p for p in filtered if "watch"    in p["name"].lower()]
        elif "bag"     in user_message: filtered = [p for p in filtered if "bag"      in p["name"].lower()]
        elif "backpack"in user_message: filtered = [p for p in filtered if "backpack" in p["name"].lower()]
        elif "sunglass"in user_message: filtered = [p for p in filtered if "sunglass" in p["name"].lower()]
        elif "necklace"in user_message: filtered = [p for p in filtered if "necklace" in p["name"].lower()]
        if "black" in user_message: filtered = [p for p in filtered if p["color"] == "black"]
        if "gold"  in user_message: filtered = [p for p in filtered if p["color"] == "gold"]
        if not filtered:
            return {"reply": "Sorry, I couldn't find matching accessories ", "products": []}
        reply = "Here are some accessories "
        return {"reply": reply, "products": filtered}

    elif any(w in user_message for w in ["gadget", "earbud", "earbuds", "speaker", "smartwatch", "smart watch", "headphone", "headphones", "charger", "power bank"]):
        filtered = [p for p in products if p["category"] == "gadget"]
        if "earbud"    in user_message: filtered = [p for p in filtered if "earbud"   in p["name"].lower()]
        elif "speaker" in user_message: filtered = [p for p in filtered if "speaker"  in p["name"].lower()]
        elif "smartwatch" in user_message or "smart watch" in user_message:
            filtered = [p for p in filtered if "smart" in p["name"].lower()]
        elif "headphone" in user_message: filtered = [p for p in filtered if "headphone" in p["name"].lower()]
        elif "charger"   in user_message: filtered = [p for p in filtered if "charger"   in p["name"].lower()]
        if "black" in user_message: filtered = [p for p in filtered if p["color"] == "black"]
        if "white" in user_message: filtered = [p for p in filtered if p["color"] == "white"]
        if "cheap" in user_message or "budget" in user_message: filtered = [p for p in filtered if p["price"] < 80]
        if not filtered:
            return {"reply": "Sorry, I couldn't find matching gadgets ", "products": []}
        reply = "Here are some gadgets "
        return {"reply": reply, "products": filtered}

    else:
        return {"reply": "I didn't understand that. Try: 'black dress', 'earbuds', or upload a product photo "}


@app.get("/")
def home():
    return {"message": "AI Shopping Assistant API is running"}


@app.get("/check-key")
def check_key():
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        return {"status": "GOOGLE_API_KEY is NOT set"}
    return {"status": f" Google Gemini Key found: {key[:10]}"}


@app.get("/products")
def get_products():
    return PRODUCTS


@app.get("/products/{product_id}")
def get_product(product_id: str):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return {"error": "Product not found"}
