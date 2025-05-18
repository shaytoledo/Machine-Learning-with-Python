
import numpy as np
import pandas as pd
from collections import Counter
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from scipy.spatial.distance import cdist
import time
import json

def load_and_scale_data(train_path, val_path):
    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)

    x_train = df_train.iloc[:, :-1].values
    y_train = df_train.iloc[:, -1].values

    x_val = df_val.iloc[:, :-1].values
    y_val = df_val.iloc[:, -1].values

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_val_scaled = scaler.transform(x_val)

    return x_train_scaled, y_train, x_val_scaled, y_val, scaler, df_train


def get_smart_radius_linspace(x_train_scaled, x_val_scaled, min_cap=0.8, max_cap=4.0, resolution=300):
    dist_matrix = cdist(x_val_scaled, x_train_scaled, metric="euclidean")
    mean_min_dist = np.mean(np.min(dist_matrix, axis=1))

    low = max(0.1, mean_min_dist * min_cap)
    high = mean_min_dist * max_cap

    return np.linspace(low, high, resolution)


def get_closest_label(mean_df_trn, vector):
    dists = np.linalg.norm(mean_df_trn.values - vector, axis=1)
    return mean_df_trn.index[np.argmin(dists)]


def majority_vote(labels, default_label, global_counts=None):
    if len(labels) == 0:
        return default_label

    count = Counter(labels)
    top = count.most_common()

    if len(top) > 1 and top[0][1] == top[1][1]:  # tie
        if global_counts:
            tied = [label for label, freq in top if freq == top[0][1]]
            return max(tied, key=lambda l: global_counts[l])

    return top[0][0]


def find_best_radius(x_train, y_train, x_val, y_val, radius_array, mean_df_trn):
    best_radius = None
    best_accuracy = 0

    distances = cdist(x_val, x_train, metric="euclidean")
    global_counts = Counter(y_train)

    for radius in radius_array:
        predictions = []
        for i, val_vector_distances in enumerate(distances):
            vld_vector = x_val[i]
            neighbor_indices = np.where(val_vector_distances <= radius)[0]
            neighbors = y_train[neighbor_indices] if len(neighbor_indices) > 0 else []
            label = majority_vote(neighbors, get_closest_label(mean_df_trn, vld_vector), global_counts)
            predictions.append(label)

        accuracy = accuracy_score(y_val, predictions)
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_radius = radius

    return best_radius


def classify_with_NNR(data_trn, data_vld, df_tst):
    print(f'starting classification with {data_trn}, {data_vld}, predicting on {len(df_tst)} instances')

    x_train, y_train, x_val, y_val, scaler, df_train = load_and_scale_data(data_trn, data_vld)

    feature_cols = df_train.columns[:-1]
    mean_df_trn = df_train.groupby(df_train.columns[-1])[feature_cols].mean()
    mean_df_trn_scaled = scaler.transform(mean_df_trn.values)
    mean_df_trn = pd.DataFrame(mean_df_trn_scaled, index=mean_df_trn.index)

    radius_array = get_smart_radius_linspace(x_train, x_val, min_cap=0.3, max_cap=4.0, resolution=300)
    best_radius = find_best_radius(x_train, y_train, x_val, y_val, radius_array, mean_df_trn)


    x_test = scaler.transform(df_tst.values)
    distances_test = cdist(x_test, x_train, metric="euclidean")
    global_counts = Counter(y_train)

    predictions = []
    for i, test_vector_distances in enumerate(distances_test):
        test_vector = x_test[i]
        neighbor_indices = np.where(test_vector_distances <= best_radius)[0]
        neighbors = y_train[neighbor_indices] if len(neighbor_indices) > 0 else []
        label = majority_vote(neighbors, get_closest_label(mean_df_trn, test_vector), global_counts)
        predictions.append(label)

    return predictions





# todo: fill in your student ids
students = {'id1': '314654484', 'id2': '302345749'}

if __name__ == '__main__':
    start = time.time()

    with open('config.json', 'r', encoding='utf8') as json_file:
        config = json.load(json_file)

    df = pd.read_csv(config['data_file_test'])
    predicted = classify_with_NNR(config['data_file_train'],
                                  config['data_file_validation'],
                                  df.drop(['class'], axis=1))

    labels = df['class'].values
    if not predicted:  # empty prediction, should not happen in your implementation
        predicted = list(range(len(labels)))

    assert(len(labels) == len(predicted))  # make sure you predict label for all test instances
    print(f'test set classification accuracy: {accuracy_score(labels, predicted)}')

    print(f'total time: {round(time.time()-start, 0)} sec')
