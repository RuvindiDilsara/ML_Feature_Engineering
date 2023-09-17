# -*- coding: utf-8 -*-
"""Label_2_Feature_Engineering.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Hp1rU03E_ZE971lmx9WJVWKE3p6Dd_i4
"""

import pandas as pd
import numpy as np

#constants
L1 = 'label_1'
L2 = 'label_2'
L3 = 'label_3'
L4 = 'label_4'

LABELS = [L1, L2, L3, L4]
AGE_LABEL = L2
FEATURES = [f"feature_{i}" for i in range (1,257)]

from google.colab import drive
MOUNT_PATH='/content/drive'
drive.mount(MOUNT_PATH)

WORKING_DIR=f"{MOUNT_PATH}/MyDrive/ML/Feature_Engineering"

train = pd.read_csv(f"{WORKING_DIR}/train.csv")
train.head()

valid = pd.read_csv(f"{WORKING_DIR}/valid.csv")
valid.head()

test = pd.read_csv(f"{WORKING_DIR}/test.csv")
test.head()

"""**Scale** the dataset"""

from sklearn.preprocessing import StandardScaler

x_train = {}
y_train = {}
x_valid = {}
y_valid = {}
x_test = {}
y_test = {}

for target_label in LABELS:
  tr_df = train[train['label_2'].notna()] if target_label == 'label_2' else train
  vl_df = valid[valid['label_2'].notna()] if target_label == 'label_2' else valid
  # test_df = test[test['label_2'].notna()] if target_label == 'label_2' else test
  test_df = test

  scaler = StandardScaler()
  x_train[target_label] = pd.DataFrame(scaler.fit_transform(tr_df.drop(LABELS, axis = 1)), columns=FEATURES)
  y_train[target_label] = tr_df[target_label]

  x_valid[target_label] = pd.DataFrame(scaler.transform(vl_df.drop(LABELS, axis = 1)), columns=FEATURES)
  y_valid[target_label] = vl_df[target_label]

  x_test[target_label] = pd.DataFrame(scaler.transform(test_df.drop(LABELS, axis = 1)), columns=FEATURES)
  y_test[target_label] = test_df[target_label]

from sklearn.neighbors import KNeighborsRegressor  # Import KNeighborsRegressor

# Create a KNN regressor with a specified number of neighbors
regressor = KNeighborsRegressor(n_neighbors=2)

# Fit the KNN regressor to the PCA-transformed features
regressor.fit(x_train[L2], y_train[L2])

from sklearn import metrics
# Make predictions
y_pred = regressor.predict(x_valid[L2])
y_pred_test = regressor.predict(x_test[L2])

# Evaluate the KNN Regressor's performance
print("Mean Absolute Error:", metrics.mean_absolute_error(y_valid[L2], y_pred))
print("Mean Squared Error:", metrics.mean_squared_error(y_valid[L2], y_pred))
print("R-squared:", metrics.r2_score(y_valid[L2], y_pred))

"""## SelectKBest with PCA"""

from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.decomposition import PCA

# Step 1: Feature selection with SelectKBest
new_selector = SelectKBest(f_classif, k=100)
x_train_new = new_selector.fit_transform(x_train[L2], y_train[L2])
x_valid_new = new_selector.transform(x_valid[L2])
x_test_new = new_selector.transform(x_test[L2])

# Step 2: Apply PCA to the selected features
pca = PCA(n_components=0.95, svd_solver='full')
x_train_pca = pca.fit_transform(x_train_new)
x_valid_pca = pca.transform(x_valid_new)
x_test_pca = pca.transform(x_test_new)
print("Shape after PCA: ", x_train_pca.shape)

# Create a KNN regressor with a specified number of neighbors (e.g., n_neighbors=5)
regressor = KNeighborsRegressor(n_neighbors=2)

# Fit the KNN regressor to the PCA-transformed features
regressor.fit(x_train_pca, y_train[L2])

# Make predictions on the validation set
y_pred_sb_pca = regressor.predict(x_valid_pca)
y_pred_sb_pca_test = regressor.predict(x_test_pca)

# Evaluate the KNN Regressor's performance
print("Mean Absolute Error:", metrics.mean_absolute_error(y_valid[L2], y_pred_sb_pca))
print("Mean Squared Error:", metrics.mean_squared_error(y_valid[L2], y_pred_sb_pca))
print("R-squared:", metrics.r2_score(y_valid[L2], y_pred_sb_pca))

output_df = pd.DataFrame({
    'Predicted labels before feature engineering': y_pred_test,
    'Predicted labels after feature engineering': y_pred_sb_pca_test,
    'No of new features': x_test_pca.shape[1]
})


for i in range(256):
  if i < x_test_pca.shape[1]:
    output_df[f'new_feature_{i+1}'] = x_test_pca[:, i]
  else:
    output_df[f'new_feature_{i+1}'] = None

output_df.shape
output_df.head()

# Save the DataFrame to the specified CSV file path
output_df.to_csv(f"{WORKING_DIR}/190140L_label_2.csv", index=False)

"""# Co-relation matrix"""

x_train_pca_df = pd.DataFrame(x_train_pca)
corr_matrix = x_train_pca_df.corr()
corr_matrix.head()

import matplotlib.pyplot as plt
import seaborn as sns

corr_treshold = 0.5
filterred_correlation_matrix = corr_matrix[(corr_matrix > corr_treshold) | (corr_matrix < -corr_treshold)]
plt.figure(figsize=(10,8))
sns.heatmap(filterred_correlation_matrix, annot=True, cmap='coolwarm', center = 0)