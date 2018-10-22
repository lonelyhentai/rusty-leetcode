import math
import operator
from typing import Any, Dict, Union
from pandas import DataFrame, Series


def calculate_shannon_entropy(data_set: DataFrame) -> float:
    entries_num = len(data_set)
    label_counts: Dict[Any, int] = {}
    # create dictionary and count number of each label
    for _, feature_vector in data_set.iterrows():
        current_label = feature_vector[-1]
        if current_label not in label_counts.keys():
            label_counts[current_label] = 0
        label_counts[current_label] += 1
    # calculate sum(- p * log 2 p) to get entropy
    shannon_entropy = 0.0
    for key in label_counts.keys():
        probability = float(label_counts[key]) / entries_num
        shannon_entropy -= probability * math.log(probability, 2)
    return shannon_entropy


def split_data_set(data_set: DataFrame, axis: int, value: Any) -> DataFrame:
    ret_data_set = DataFrame()
    for index, feature_vector in data_set:
        if feature_vector[axis] == value:
            # reduce the target value and get new feature vector
            reduced_feature_vector = feature_vector[:axis]
            reduced_feature_vector.extend(feature_vector[axis + 1:])
            ret_data_set.append(reduced_feature_vector)
    return ret_data_set


def choose_best_feature_to_split(data_set: DataFrame) -> int:
    features_num = len(data_set.get_dtype_counts()) - 1
    base_entropy = calculate_shannon_entropy(data_set)
    best_info_gain = 0.0
    best_feature = -1
    for i in range(features_num):
        # create unique set to classify
        feature_list = data_set.iloc[:, i]
        unique_vals = set(feature_list)
        # calculate the new entropy
        new_entropy = 0.0
        for value in unique_vals:
            sub_data_set = split_data_set(data_set, i, value)
            probability = len(sub_data_set) / float(len(data_set))
            new_entropy += probability * calculate_shannon_entropy(sub_data_set)
        info_gain = base_entropy - new_entropy
        # get best_feature via info_gain
        if info_gain > best_info_gain:
            best_info_gain = info_gain
            best_feature = i
    return best_feature


def majority_count(class_list: Series) -> Any:
    class_count: Dict[Any, int] = {}
    # create dictionary and count number of each vote
    for vote in class_list:
        if vote not in class_count.keys():
            class_count[vote] = 0
        class_count[vote] += 1
    # sort with the 1st item
    sorted_class_count = sorted(class_count.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_class_count[0][0]


Leaf = Any
Node = Dict[Any, Dict]
Tree = Union[Leaf, Node]


def create_tree(data_set: DataFrame, labels: Series) -> Tree:
    class_list: Series = data_set.iloc[:, -1]
    if class_list.count(class_list[0]) == len(class_list):
        return class_list[0]
    if len(data_set[0]) == 1:
        return majority_count(class_list)
    best_feature = choose_best_feature_to_split(data_set)
    best_feature_label = labels[best_feature]
    my_tree: Dict[Any, Dict] = {best_feature_label: {}}
    del (labels[best_feature])
    feature_values = data_set.iloc[:, best_feature]
    unique_values = set(feature_values)
    for value in unique_values:
        sub_labels = labels[:]
        my_tree[best_feature_label][value] = create_tree(split_data_set(data_set, best_feature, value), sub_labels)
    return my_tree

