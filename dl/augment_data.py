import cv2
import os
import random
import numpy as np

# Configuration
DATASET_PATH = "dataset/train"
TARGET_COUNT = 300
IMG_SIZE = (224, 224)

def augment_image(image):
    """Applies random transformations using OpenCV."""
    h, w = image.shape[:2]
    
    # Random Flip
    if random.random() > 0.5:
        image = cv2.flip(image, 1)

    # Random Rotation (-20 to 20 degrees)
    angle = random.uniform(-20, 20)
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    image = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)

    # Random Brightness/Contrast
    alpha = random.uniform(0.8, 1.2) # Contrast
    beta = random.uniform(-20, 20)   # Brightness
    image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    # Random Zoom (Crop and Resize)
    if random.random() > 0.3:
        zoom_factor = random.uniform(0.85, 1.0)
        crop_h, crop_w = int(h * zoom_factor), int(w * zoom_factor)
        start_y = (h - crop_h) // 2
        start_x = (w - crop_w) // 2
        image = image[start_y:start_y+crop_h, start_x:start_x+crop_w]
        image = cv2.resize(image, (w, h))

    return image

def balance_dataset():
    """Balances each class to TARGET_COUNT via augmentation."""
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset path '{DATASET_PATH}' not found.")
        return

    classes = [d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))]
    
    for cls in classes:
        cls_path = os.path.join(DATASET_PATH, cls)
        images = [f for f in os.listdir(cls_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        current_count = len(images)
        print(f"Class '{cls}': {current_count} images found.")
        
        if current_count == 0:
            print(f"Skipping empty class '{cls}'.")
            continue
            
        needed = TARGET_COUNT - current_count
        if needed <= 0:
            print(f"Class '{cls}' already has enough images.")
            continue
            
        print(f"Generating {needed} augmented images for '{cls}'...")
        
        generated = 0
        while generated < needed:
            # Pick a random source image
            src_name = random.choice(images)
            src_path = os.path.join(cls_path, src_name)
            img = cv2.imread(src_path)
            
            if img is None:
                continue
                
            # Augment
            aug_img = augment_image(img)
            
            # Save
            new_name = f"aug_{generated}_{src_name}"
            save_path = os.path.join(cls_path, new_name)
            cv2.imwrite(save_path, aug_img)
            
            generated += 1
            
        print(f"✅ Class '{cls}' balanced to {TARGET_COUNT} images.\n")

if __name__ == "__main__":
    balance_dataset()
