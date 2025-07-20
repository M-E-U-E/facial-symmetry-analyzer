# Facial Symmetry Analyzer

A FastAPI-based web application that analyzes facial symmetry using MediaPipe and golden ratio principles.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/M-E-U-E/facial-symmetry-analyzer.git
   cd facial-symmetry-analyzer
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a Static Directory**:
   Create a `static` directory in the project root and place `index.html` inside it.

5. **Run the Application**:
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the Application**:
   Open your browser and navigate to `http://localhost:8000`.

## Usage
- Upload a clear, well-lit image of a face using the web interface.
- The application will process the image and return a symmetry score (0 to 1, closer to 1 is more symmetrical).
- A disclaimer is included to emphasize that this is for entertainment purposes only.

## Notes
- The application uses MediaPipe for facial landmark detection, which is lightweight and efficient.
- Symmetry is calculated based on ratios like face width to eye distance, forehead to eyes, etc., compared to the golden ratio (1.618).
- Ensure the image contains a single, clearly visible face for best results.

## Ethical Considerations
- The application uses neutral language ("symmetry score") and includes a disclaimer to avoid harmful implications.
- This tool is for fun and does not measure beauty or personal worth.