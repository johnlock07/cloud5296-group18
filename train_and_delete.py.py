import tensorflow as tf
import numpy as np
import os
import time

def create_and_train_model():
    print("Starting model training...")
    
    # Sample dataset
    X = np.random.rand(5000, 100)
    y = np.random.rand(5000, 1)

    # Define a simple model
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=20, verbose=1)  # Small training loop for load testing

    # Save model temporarily
    model_path = "/tmp/trained_model"
    model.save(model_path)
    print(f"Model saved at {model_path}")

    # Simulate usage for autoscaling impact
    time.sleep(5)

    # Delete model
    if os.path.exists(model_path):
        print("Deleting trained model...")
        os.system(f"rm -rf {model_path}")

    print("Restarting training loop...\n")
    time.sleep(2)  # Pause before next training cycle

# Infinite training loop
while True:
    create_and_train_model()