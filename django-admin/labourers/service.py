# facial_recognition/service.py
import face_recognition
import cv2
import numpy as np
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

class FacialRecognitionService:
    def __init__(self, tolerance=0.6):
        self.tolerance = tolerance
    
    def encode_face(self, image_path):
        """Encode a face from an image file"""
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            return None
        
        face_encodings = face_recognition.face_encodings(image, face_locations)
        return face_encodings[0] if face_encodings else None
    
    def verify_face(self, live_image, stored_encoding):
        """Verify if live image matches stored encoding"""
        if stored_encoding is None:
            return False, 0.0
        
        live_encoding = self.encode_face(live_image)
        if live_encoding is None:
            return False, 0.0
        
        # Calculate face distance
        face_distance = face_recognition.face_distance([stored_encoding], live_encoding)[0]
        confidence = max(0, 1 - face_distance)
        
        match = face_distance <= self.tolerance
        
        return match, confidence
    
    def perform_liveness_check(self, image):
        """Simple liveness check (can be enhanced with anti-spoofing)"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Check for blurriness (simple variance of Laplacian)
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Basic checks
        is_blurry = fm < 100  # Threshold for blurriness
        has_face = len(face_recognition.face_locations(img_array)) > 0
        
        return {
            'liveness_passed': has_face and not is_blurry,
            'blurriness_score': fm,
            'face_detected': has_face
        }