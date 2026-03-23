import tensorflow as tf
from tensorflow.keras import layers, models, applications
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import os

# ==============================
# 1️⃣ CONFIGURATION
# ==============================
IMG_SIZE = (224, 224)
BATCH_SIZE = 16 
EPOCHS = 20
LEARNING_RATE = 1e-4

TRAIN_PATH = "dataset/train"
VAL_PATH = "dataset/val"
MODEL_SAVE_PATH = "saved_model/final_body_model.keras"

# Ensure save directory exists
os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

# ==============================
# 2️⃣ LOAD DATASETS
# ==============================
train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_PATH,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    VAL_PATH,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

class_names = train_ds.class_names
print(f"Classes found: {class_names}")

# ==============================
# 3️⃣ DATA AUGMENTATION & PREPROCESSING
# ==============================
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.2),
    layers.RandomZoom(0.2),
    layers.RandomContrast(0.2),
])

# Apply augmentation and preprocessing
def preprocess(image, label):
    return applications.mobilenet_v2.preprocess_input(image), label

def augment_and_preprocess(image, label):
    image = data_augmentation(image)
    return preprocess(image, label)

train_ds = train_ds.map(augment_and_preprocess).prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.map(preprocess).prefetch(buffer_size=tf.data.AUTOTUNE)

# ==============================
# 4️⃣ CLASS WEIGHTS
# ==============================
print("Computing class weights...")
y_labels = []
for _, label in tf.keras.utils.image_dataset_from_directory(TRAIN_PATH, image_size=IMG_SIZE, batch_size=BATCH_SIZE, shuffle=False):
    y_labels.extend(label.numpy())

class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(y_labels),
    y=np.array(y_labels)
)
class_weights = dict(enumerate(class_weights))
print(f"Class Weights: {class_weights}")

# ==============================
# 5️⃣ MODEL (Standard MobileNetV2)
# ==============================
base_model = applications.MobileNetV2(
    weights="imagenet", 
    include_top=False, 
    input_shape=(224, 224, 3)
)

base_model.trainable = True
# Freeze the first 100 layers
for layer in base_model.layers[:100]:
    layer.trainable = False

inputs = layers.Input(shape=(224, 224, 3))
x = base_model(inputs, training=True)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.5)(x)
x = layers.Dense(128, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(0.01))(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(len(class_names), activation="softmax")(x)

model = models.Model(inputs, outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ==============================
# 6️⃣ TRAINING
# ==============================
callbacks = [
    EarlyStopping(patience=8, restore_best_weights=True, monitor='val_loss'),
    ReduceLROnPlateau(patience=3, factor=0.5, verbose=1, monitor='val_loss'),
    ModelCheckpoint("saved_model/best_model.keras", save_best_only=True, monitor='val_accuracy')
]

print("Starting MobileNetV2 training...")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    class_weight=class_weights,
    callbacks=callbacks
)

model.save(MODEL_SAVE_PATH)
print(f"✅ Training complete. Model saved to {MODEL_SAVE_PATH}")
