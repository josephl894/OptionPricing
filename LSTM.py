#Work in progress
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import monteCarloAmerican
from OptionsPricingCalculatorApp import App
"""
root = tk.Tk()
app = App(root)
root.mainloop() 
"""
#Data Preparation
n = 25
m = 500

#stock_price_paths = monteCarloAmerican.generate_path(app.price, app.T, app.r, app.sigma, n, m)
stock_price_paths = monteCarloAmerican.generate_path(100, 252, 5, 10, n, m)

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(stock_price_paths.reshape(-1, 1)).reshape(m, n)

#Define Long Short-Term Memory Network Model
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(n, 1)),  # First LSTM layer
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(50, return_sequences=True),  # Second LSTM layer
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(50),  # Third LSTM layer
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(1)  # Output layer for option value prediction
])

model.compile(optimizer='adam', loss='mse')

def intrinsic_value(S, K, option_type):
    if option_type == 'call':
        return max(S - K, 0)
    elif option_type == 'put':
        return max(K - S, 0)
    else:
        raise ValueError("Option type must be 'call' or 'put'")

#Train
epochs = 5
batch_size = 32

for epoch in range(epochs):
    for path in scaled_data:
        path = path.reshape(1, n, 1)  # Adjusting shape for LSTM input
        
        for t in reversed(range(n)):
            current_data = path[:, :t+1, :]
            current_data = pad_sequences(current_data, maxlen=n, padding='post', dtype='float32')
            continuation_value = model.predict(current_data)
            immediate_value = intrinsic_value(100,150,"call")
            
            if immediate_value > continuation_value:
                target = immediate_value
            else:
                target = continuation_value

            model.fit(current_data, np.array([[target]]), epochs=1, batch_size=batch_size, verbose=0, shuffle=False)

#Predict
sample_path = scaled_data[0].reshape(1, n, 1)
predicted_option_value = model.predict(sample_path)

print(f"predicted_option_value: {predicted_option_value :.2f}")