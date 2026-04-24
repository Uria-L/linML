import matplotlib.pyplot as plt
import pandas as pd
import joblib

df = pd.read_csv("../data/metrics.csv")

# Load trained model
model = joblib.load("isolation_forest.pkl")

X = df[["cpu", "io_read", "io_write"]].values  # shape (n,3)
y = X.ravel()               # 1D array

mean_cpu = df.groupby('binary')['cpu'].mean().sort_values(ascending=False)
mean_io_read = df.groupby('binary')['io_read'].mean().sort_values(ascending=False)
mean_io_write = df.groupby('binary')['io_write'].mean().sort_values(ascending=False)

top_cpu = mean_cpu.head(30)  # adjust number shown
top_read = mean_io_read.head(30)
top_write = mean_io_write.head(30)


# Anomaly score distribution
scores = model.score_samples(X)
plt.hist(scores, bins=50, edgecolor='black')
plt.xlabel('Anomaly Score')
plt.ylabel('Frequency')
plt.show()

# Create 3 subplots side-by-side
fig, axes = plt.subplots(1, 3, figsize=(18, max(6, 0.3 * len(top_cpu))))

# Plot 1: CPU
top_cpu.sort_values().plot(kind='barh', color='C0', ax=axes[0])
axes[0].set_xlabel('Mean CPU (CPU_60s)')
axes[0].set_title('Mean CPU usage by binary (top {})'.format(len(top_cpu)))
axes[0].tick_params(axis='y', labelsize=9)

# Plot 2: IO Read
top_read.sort_values().plot(kind='barh', color='C1', ax=axes[1])
axes[1].set_xlabel('Mean IO Read (bytes/sec)')
axes[1].set_title('Mean IO Read by binary (top {})'.format(len(top_read)))
axes[1].tick_params(axis='y', labelsize=9)

# Plot 3: IO Write
top_write.sort_values().plot(kind='barh', color='C2', ax=axes[2])
axes[2].set_xlabel('Mean IO Write (bytes/sec)')
axes[2].set_title('Mean IO Write by binary (top {})'.format(len(top_write)))
axes[2].tick_params(axis='y', labelsize=9)

plt.tight_layout()
plt.show()
