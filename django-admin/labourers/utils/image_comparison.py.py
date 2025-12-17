from PIL import Image, ImageChops, ImageStat
import io
import base64
import math
import hashlib

def image_to_base64(image):
    """Convert PIL Image to base64"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode()

def base64_to_image(base64_string):
    """Convert base64 to PIL Image"""
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    image_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_data))

def generate_image_hash(image):
    """Generate hash from PIL Image"""
    # Standardize image
    image = image.resize((200, 200)).convert('L')
    pixels = list(image.getdata())
    pixel_str = ''.join(str(p) for p in pixels)
    return hashlib.sha256(pixel_str.encode()).hexdigest()

def compare_images_simple(image1, image2):
    """
    Simple image comparison using:
    1. Hash comparison (exact match)
    2. Histogram comparison
    3. Pixel difference
    """
    # Resize both images to same size
    size = (300, 300)
    img1 = image1.resize(size).convert('RGB')
    img2 = image2.resize(size).convert('RGB')
    
    # Method 1: Hash comparison
    hash1 = generate_image_hash(img1)
    hash2 = generate_image_hash(img2)
    hash_similar = hash1 == hash2
    
    # Method 2: Histogram comparison
    hist1 = img1.histogram()
    hist2 = img2.histogram()
    
    # Calculate histogram similarity
    hist_similarity = sum(min(h1, h2) for h1, h2 in zip(hist1, hist2)) / sum(hist1)
    
    # Method 3: Pixel difference
    diff = ImageChops.difference(img1, img2)
    stat = ImageStat.Stat(diff)
    rms = math.sqrt(sum([x*x for x in stat.mean]) / len(stat.mean))
    
    # Convert to similarity percentage (0-100%)
    pixel_similarity = max(0, 100 - rms)
    
    # Combined score (weighted)
    similarity_score = (hist_similarity * 100 * 0.4) + (pixel_similarity * 0.6)
    
    return {
        'hash_match': hash_similar,
        'histogram_similarity': hist_similarity,
        'pixel_similarity': pixel_similarity,
        'similarity_score': similarity_score,
        'is_similar': similarity_score > 70  # 70% threshold
    }