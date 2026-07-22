from __future__ import annotations

from collections import Counter


def binary_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float | int | dict[int, int]]:
    tp = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 1)
    tn = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 0)
    fp = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 0)
    precision = tp / (tp + fp) if tp + fp else 0.0
    fraud_recall = tp / (tp + fn) if tp + fn else 0.0
    nonfraud_recall = tn / (tn + fp) if tn + fp else 0.0
    fraud_f1 = 2 * precision * fraud_recall / (precision + fraud_recall) if precision + fraud_recall else 0.0
    non_precision = tn / (tn + fn) if tn + fn else 0.0
    non_f1 = 2 * non_precision * nonfraud_recall / (non_precision + nonfraud_recall) if non_precision + nonfraud_recall else 0.0
    n = len(y_true)
    return {
        "n": n,
        "accuracy": (tp + tn) / n if n else 0.0,
        "fraud_f1": fraud_f1,
        "macro_f1": (fraud_f1 + non_f1) / 2,
        "balanced_accuracy": (fraud_recall + nonfraud_recall) / 2,
        "fraud_recall": fraud_recall,
        "nonfraud_recall": nonfraud_recall,
        "predicted_fraud_ratio": sum(y_pred) / n if n else 0.0,
        "label_counts": dict(Counter(y_true)),
        "prediction_counts": dict(Counter(y_pred)),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }
