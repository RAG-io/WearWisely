import tensorflow as tf
from sklearn.metrics import classification_report
import numpy as np

IMG_SIZE = (224, 224)
BATCH_SIZE = 8

VAL_PATH = "dataset/val"
MODEL_PATH = "saved_model/final_body_model.keras"

model = tf.keras.models.load_model(MODEL_PATH)

val_ds = tf.keras.utils.image_dataset_from_directory(
    VAL_PATH,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

class_names = val_ds.class_names

loss, acc = model.evaluate(val_ds)
print("Validation Accuracy:", acc)

y_true = []
y_pred = []

for images, labels in val_ds:
    preds = model.predict(images)
    y_true.extend(labels.numpy())
    y_pred.extend(np.argmax(preds, axis=1))

print(classification_report(y_true, y_pred, target_names=class_names))
