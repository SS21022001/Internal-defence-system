import cv2

# Function to preprocess the fingerprint image
def preprocess_image(image_path):
    # Load the image in grayscale
    image = cv2.imread(image_path, 0)

    # Apply Gaussian blur to reduce noise
    image = cv2.GaussianBlur(image, (5, 5), 0)

    # Apply adaptive thresholding to enhance fingerprint ridges
    _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    return image

# Function to extract fingerprint features
def extract_features(image):
    # Apply morphological operations to remove small gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

    # Find and draw contours around the fingerprint region
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, contours, -1, (255, 255, 255), thickness=2)

    # Extract the largest contour as the fingerprint region
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Crop the fingerprint region
        fingerprint = image[y:y+h, x:x+w]

        return fingerprint

    return None

# Function to perform fingerprint recognition
def fingerprint_recognition(image_path):
    # Preprocess the fingerprint image
    preprocessed_image = preprocess_image(image_path)

    # Extract fingerprint features
    fingerprint = extract_features(preprocessed_image)

    # Display the preprocessed image and extracted fingerprint
    cv2.imshow("Preprocessed Image", preprocessed_image)
    if fingerprint is not None:
        cv2.imshow("Extracted Fingerprint", fingerprint)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Image path (local file path)
image_path = 'fingerprint.jpg'

# Perform fingerprint recognition
fingerprint_recognition(image_path)
