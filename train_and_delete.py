import tensorflow as tf
import numpy as np
import os
import time

def create_and_train_model():
    print("Starting model training...")
    start_time = time.time()  # Start the timer

    X = np.random.rand(20000, 500)
    y = np.random.rand(20000, 1)

    # Model definition
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(512, activation='relu', input_shape=(500,)),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, batch_size=128, verbose=1, validation_split=0.2)
    elapsed_time = time.time() - start_time  # End the timer and calculate elapsed time
    print(f"completed in {elapsed_time:.2f} seconds.\n")
    
    print("Restarting training loop...\n")
    time.sleep(2)  # Pause before next training cycle

# Infinite training loop
while True:
    create_and_train_model()
