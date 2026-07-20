"""
Train a neural network to predict aircraft conflicts.
Compare against the geometric baseline.
"""

import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve, auc, 
    precision_recall_curve, f1_score
)
import matplotlib.pyplot as plt

print("=" * 100)
print("NEURAL NETWORK CONFLICT CLASSIFIER")
print("=" * 100)
print()

# Load training data
print("Step 1: Load training data")
print("-" * 100)
with open('training_data.pkl', 'rb') as f:
    features, labels = pickle.load(f)

features = np.array(features)
labels = np.array(labels)

print(f"  Loaded {len(features)} samples")
print(f"  Features per sample: {features.shape[1]}")
print(f"  Class distribution: {np.sum(labels)} conflicts, {len(labels) - np.sum(labels)} safe")
print()

# Split data
print("Step 2: Split into train/test (80/20)")
print("-" * 100)
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, random_state=42, stratify=labels
)
print(f"  Train set: {len(X_train)} samples")
print(f"  Test set: {len(X_test)} samples")
print()

# Normalize features
print("Step 3: Normalize features")
print("-" * 100)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("  ✓ Scaled to mean=0, std=1")
print()

# Train neural network
print("Step 4: Train neural network")
print("-" * 100)
print("  Architecture: Input(8) → Hidden(32) → Hidden(16) → Output(1)")
print("  Activation: ReLU")
print("  Optimizer: Adam")
print("  Loss: Binary Crossentropy")
print()

model = MLPClassifier(
    hidden_layer_sizes=(32, 16),
    activation='relu',
    solver='adam',
    max_iter=500,
    random_state=42,
    verbose=False,
    learning_rate_init=0.001,
    batch_size=32,
)

print("  Training...")
model.fit(X_train_scaled, y_train)
print(f"  ✓ Training complete (converged in {model.n_iter_} iterations)")
print()

# Evaluate on test set
print("Step 5: Evaluate on test set")
print("-" * 100)

y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

accuracy = np.mean(y_pred == y_test)
print(f"  Accuracy: {accuracy*100:.2f}%")
print()

print("  Classification Report:")
print("  " + "-" * 70)
print(classification_report(y_test, y_pred, target_names=['Safe', 'Conflict'], 
                           digits=4).replace('\n', '\n  '))
print()

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

print("  Confusion Matrix:")
print(f"    True Negatives (correct safe): {tn}")
print(f"    False Positives (false alarm): {fp}")
print(f"    False Negatives (missed conflict): {fn}")
print(f"    True Positives (correct conflict): {tp}")
print()

# ROC-AUC
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)
print(f"  ROC-AUC Score: {roc_auc:.4f}")
print()

# Save model
print("Step 6: Save model")
print("-" * 100)
pickle.dump((model, scaler), open('conflict_model.pkl', 'wb'))
print("  ✓ Saved conflict_model.pkl")
print()

# Plotting
print("Step 7: Generate evaluation plots")
print("-" * 100)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Confusion matrix
ax = axes[0, 0]
im = ax.imshow(cm, cmap='Blues', aspect='auto')
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.set_title('Confusion Matrix')
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(['Safe', 'Conflict'])
ax.set_yticklabels(['Safe', 'Conflict'])
for i in range(2):
    for j in range(2):
        ax.text(j, i, cm[i, j], ha='center', va='center', color='white' if cm[i, j] > cm.max()/2 else 'black')

# ROC curve
ax = axes[0, 1]
ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random classifier')
ax.set_xlim([0.0, 1.0])
ax.set_ylim([0.0, 1.05])
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
ax.set_title('ROC Curve')
ax.legend(loc="lower right")
ax.grid(True, alpha=0.3)

# Precision-Recall curve
precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
ax = axes[1, 0]
ax.plot(recall, precision, color='green', lw=2)
ax.fill_between(recall, precision, alpha=0.2, color='green')
ax.set_xlabel('Recall')
ax.set_ylabel('Precision')
ax.set_title('Precision-Recall Curve')
ax.set_xlim([0.0, 1.0])
ax.set_ylim([0.0, 1.05])
ax.grid(True, alpha=0.3)

# Prediction distribution
ax = axes[1, 1]
ax.hist(y_pred_proba[y_test == 0], bins=30, alpha=0.6, label='Safe (actual)', color='blue')
ax.hist(y_pred_proba[y_test == 1], bins=30, alpha=0.6, label='Conflict (actual)', color='red')
ax.set_xlabel('Predicted Conflict Probability')
ax.set_ylabel('Count')
ax.set_title('Prediction Distribution')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('nn_evaluation.png', dpi=150, bbox_inches='tight')
print("  ✓ Saved nn_evaluation.png")
print()

print("=" * 100)
print("TRAINING COMPLETE!")
print("=" * 100)