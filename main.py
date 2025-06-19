import time
import json
import numpy as np
import pickle
from sklearn.preprocessing import  StandardScaler
from numpy.linalg import norm

from utils import evaluate_clustering_result

def load_data(features_file):
    """
    Load image features from a file.
    input: path to the file containing image features.
    output: a dictionary mapping filenames to their corresponding feature vectors.
    """
    with open(features_file, 'rb') as f:
        data = pickle.load(f)
    filenames = list(data.keys()) #names of the images
    embeddings = np.array(list(data.values()))# feature vectors of the images

    scaler = StandardScaler()# fit the scaler to the data
    scaled_embeddings = scaler.fit_transform(embeddings)

    items = [(filename, embedding) for filename, embedding in zip(filenames, scaled_embeddings)]
    return items

def find_centroid(cluster): 
    """
    Find the centroid of a cluster.
    """
    return np.mean(cluster, axis=0)

def remove_from_other_clusters(filename, embedding, cluster_id, cluster2filenames, cluster_members, cluster_centroids):
    """
    Remove a filename and its embedding from all clusters except the specified one.
    input: filename - the name of the file to remove,
    embedding - the feature vector of the file,
    cluster_id - the ID of the cluster to keep,
    cluster2filenames - a dictionary mapping cluster IDs to lists of filenames,
    cluster_members - a dictionary mapping cluster IDs to lists of embeddings,
    cluster_centroids - a dictionary mapping cluster IDs to their centroids.
    """
    for other_cluster_id in list(cluster2filenames.keys()):
        if other_cluster_id != cluster_id:
            if filename in cluster2filenames[other_cluster_id]:
                cluster2filenames[other_cluster_id].remove(filename)
                # Find the index of the embedding to remove it
                index = next(i for i, e in enumerate(cluster_members[other_cluster_id]) if np.array_equal(e, embedding))
                cluster_members[other_cluster_id].pop(index)
                cluster_centroids[other_cluster_id] = find_centroid(cluster_members[other_cluster_id])

def add_to_cluster(filename, embedding, cluster_id, cluster2filenames, cluster_members, cluster_centroids):
    """
    Add a file and its embedding to a cluster.
    """
    cluster2filenames[cluster_id].append(filename)
    cluster_members[cluster_id].append(embedding)
    
def cosine(a, b):
    """
    Calculate the cosine similarity between two vectors.
    input: a - first vector, b - second vector.
    output: cosine similarity between the two vectors.
    """
    return np.dot(a, b) / (norm(a) * norm(b))


def cluster_data(features_file, min_cluster_size, iterations):
    """
    This function clusters image feature vectors based on cosine similarity. It iteratively assigns images to the most similar cluster or creates a new one if similarity is too low, repeating until convergence or a set number of iterations.
    input: features_file - path to the file containing image features,
    min_cluster_size - minimum size of a cluster to be considered valid,
    iterations - number of iterations for the clustering algorithm.
    output: a dictionary mapping cluster IDs to lists of filenames in each cluster.
    """

    # todo: implement this function
    print(f'starting clustering images in file {features_file}')
    items = load_data(features_file)

    min_similarity = 0.052 # my choice, can be tuned
    cluster_centroids = dict()
    cluster2filenames = dict()
    cluster_members = dict()

    for i in range(iterations):
        print(f'iteration {i+1} of {iterations}')
        cluster_updates = 0 #initialize the number of cluster updates

        for filename, embedding in items:
            # find the closest cluster centroid
            max_similarity = 0
            cluster_id = -1

            for c, centroid in cluster_centroids.items():
                similarity = cosine(centroid, embedding)
                if similarity > max_similarity:
                    max_similarity = similarity
                    cluster_id = c

            if max_similarity > min_similarity:
                if filename not in cluster2filenames[cluster_id]:
                    remove_from_other_clusters(filename, embedding, cluster_id, cluster2filenames, cluster_members, cluster_centroids)
                    add_to_cluster(filename, embedding, cluster_id, cluster2filenames, cluster_members, cluster_centroids)
                    cluster_updates += 1
            else:
                cluster_id = len(cluster_centroids)
                cluster_centroids[cluster_id] = embedding
                cluster2filenames[cluster_id] = [filename]
                cluster_members[cluster_id] = [embedding]
                cluster_updates += 1
        if cluster_updates == 0:
            break  # Stop if no changes occurred

    print(f'clustering completed with {len(cluster_centroids)} clusters')
    print(cluster2filenames)
    return cluster2filenames


if __name__ == '__main__':
    start = time.time()

    with open('config.json', 'r', encoding='utf8') as json_file:
        config = json.load(json_file)

    result = cluster_data(config['features_file'],
                          config['min_cluster_size'],
                          config['max_iterations'])

    evaluation_scores = evaluate_clustering_result(config['labels_file'], result)  # implemented
    
    print(f'total time: {round(time.time()-start, 0)} sec')
