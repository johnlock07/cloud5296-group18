import tensorflow as tf
import numpy as np
import os
import time

def create_and_train_model():
    print("Starting model training...")
    start_time = time.time()  # Start the timer

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

    print("Restarting training loop...\n")
    elapsed_time = time.time() - start_time  # End the timer and calculate elapsed time
    print(f"completed in {elapsed_time:.2f} seconds.\n")
    time.sleep(2)  # Pause before next training cycle

# Infinite training loop
while True:
    create_and_train_model()
