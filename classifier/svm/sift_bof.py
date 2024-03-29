import os
import pickle
import time

import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.svm import SVC


def create(img_and_cls, dvector_len):
    start = time.time()
    images, classes = map(list, zip(*img_and_cls))
    local_features = []
    global_features = []
    sift = cv2.xfeatures2d.SIFT_create()
    clf = SVC(kernel='rbf', C=10000)

    # すべての画像の特徴量を取り出す
    for img in images:
        local_features.append(sift.detectAndCompute(img, None)[1])

    eft = np.concatenate(list(filter(lambda f: f is not None, local_features)))
    visual_words = MiniBatchKMeans(n_clusters=dvector_len).fit(eft).cluster_centers_

    for i in range(len(images)):
        dvector = np.zeros(dvector_len)
        if local_features[i] is not None:
            for f in local_features[i]:
                dvector[((visual_words - f) ** 2).sum(axis=1).argmin()] += 1
            dvector = dvector/sum(dvector)
        global_features.append(dvector)

    clf.fit(global_features, classes)

    return clf, visual_words

class SVM:

    def __init__(self, svm_name=None):
        decode_dir = 'learned/'
        self.sift = cv2.xfeatures2d.SIFT_create()
        with open(os.path.join(os.path.dirname(__file__), decode_dir + svm_name + '.pkl'), 'rb') as f:
            self.svm, self.visual_words = pickle.load(f)
        self.dvector_len = len(self.visual_words)

    def predict(self, image=None):

        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        feat = self.sift.detectAndCompute(gray_image, None)[1]
        dvector = np.zeros(self.dvector_len)
        if feat is not None:
            for f in feat:
                dvector[((self.visual_words - f) ** 2).sum(axis=1).argmin()] += 1
            dvector = dvector / sum(dvector)
        return self.svm.predict([dvector])[0]