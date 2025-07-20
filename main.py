from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import mediapipe as mp
import numpy as np
from PIL import Image
import io
import math
import logging

app = FastAPI()

# Mount static files for serving frontend assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Golden ratio constant
GOLDEN_RATIO = 1.618

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

def get_symmetry_level(score):
    """Determine symmetry level based on score (0-1 scale converted to 0-100)."""
    score_percent = score * 100
    if 90 <= score_percent <= 100:
        return "Divine Symmetry ✨"
    elif 75 <= score_percent < 90:
        return "Elegant Harmony 💫"
    elif 60 <= score_percent < 75:
        return "Refined Balance 🌿"
    elif 40 <= score_percent < 60:
        return "Natural Allure 🌸"
    else:  # 0 <= score_percent < 40
        return "Authentic Beauty 🌙"
    
def compute_symmetry_score(image):
    """Process image and compute symmetry score based on golden ratio."""
    # Convert PIL image to numpy array
    image_np = np.array(image)
    
    # Process image with MediaPipe
    results = face_mesh.process(image_np)
    
    if not results.multi_face_landmarks:
        raise HTTPException(status_code=400, detail="No face detected in the image")
    
    landmarks = results.multi_face_landmarks[0].landmark
    
    # Extract key facial landmarks (normalized coordinates)
    left_eye = (landmarks[33].x * image.width, landmarks[33].y * image.height)  # Left eye center
    right_eye = (landmarks[263].x * image.width, landmarks[263].y * image.height)  # Right eye center
    nose_tip = (landmarks[1].x * image.width, landmarks[1].y * image.height)  # Nose tip
    nose_left = (landmarks[234].x * image.width, landmarks[234].y * image.height)  # Left side of nose
    nose_right = (landmarks[454].x * image.width, landmarks[454].y * image.height)  # Right side of nose
    mouth_left = (landmarks[61].x * image.width, landmarks[61].y * image.height)  # Left mouth corner
    mouth_right = (landmarks[291].x * image.width, landmarks[291].y * image.height)  # Right mouth corner
    chin = (landmarks[152].x * image.width, landmarks[152].y * image.height)  # Chin
    forehead = (landmarks[10].x * image.width, landmarks[10].y * image.height)  # Forehead (approx)
    left_face_edge = (landmarks[234].x * image.width, landmarks[234].y * image.height)  # Left face edge (approx)
    right_face_edge = (landmarks[454].x * image.width, landmarks[454].y * image.height)  # Right face edge (approx)
    
    # Calculate key distances
    eye_distance = calculate_distance(left_eye, right_eye)
    nose_width = calculate_distance(nose_left, nose_right)
    mouth_width = calculate_distance(mouth_left, mouth_right)
    face_width = calculate_distance(left_face_edge, right_face_edge)
    forehead_to_eyes = calculate_distance(forehead, left_eye)
    eyes_to_chin = calculate_distance(left_eye, chin)
    eye_to_nose = calculate_distance(left_eye, nose_tip)
    nose_to_chin = calculate_distance(nose_tip, chin)
    
    # Log distances for debugging
    logger.info(f"Distances: eye_distance={eye_distance:.2f}, nose_width={nose_width:.2f}, "
                f"mouth_width={mouth_width:.2f}, face_width={face_width:.2f}, "
                f"forehead_to_eyes={forehead_to_eyes:.2f}, eyes_to_chin={eyes_to_chin:.2f}")
    
    # Calculate ratios
    ratios = [
        face_width / eye_distance if eye_distance != 0 else 1.0,
        forehead_to_eyes / eyes_to_chin if eyes_to_chin != 0 else 1.0,
        nose_width / mouth_width if mouth_width != 0 else 1.0,
        eye_to_nose / nose_to_chin if nose_to_chin != 0 else 1.0
    ]
    # Log ratios for debugging
    logger.info(f"Ratios: face_width/eye_distance={ratios[0]:.2f}, "
                f"forehead_to_eyes/eyes_to_chin={ratios[1]:.2f}, "
                f"nose_width/mouth_width={ratios[2]:.2f}, "
                f"eye_to_nose/nose_to_chin={ratios[3]:.2f}")
    
    # Compute how close each ratio is to the golden ratio
    ratio_deviations = [min(abs(ratio - GOLDEN_RATIO) / GOLDEN_RATIO, 1.0) for ratio in ratios]  # Cap deviation at 1.0
    avg_deviation = sum(ratio_deviations) / len(ratio_deviations)
    
    # Convert deviation to a symmetry score (closer to 1 is better)
    symmetry_score = max(0.0, 1.0 - avg_deviation * 0.3)  # Adjusted scaling factor
    
    # Log final score
    logger.info(f"Symmetry Score: {symmetry_score:.2f}")
    
    return round(symmetry_score, 2)

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend HTML page."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Endpoint to analyze uploaded image for facial symmetry."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read and process the image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Compute symmetry score
        score = compute_symmetry_score(image)
        level = get_symmetry_level(score)
        
        return {
            "symmetry_score": score,
            "symmetry_level": level,
            "message": (
                f"Your face has a symmetry score of {score:.2f} (closer to 1 is more symmetrical), "
                f"earning the '{level}' level! This is for fun and does not reflect beauty or worth!"
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

# Cleanup MediaPipe resources on shutdown
@app.on_event("shutdown")
def shutdown_event():
    face_mesh.close()