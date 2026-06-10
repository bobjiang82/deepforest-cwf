import os
import openml
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from deepforest import CascadeForestClassifier


def main():
    requested_n_jobs = int(os.environ.get("DF_N_JOBS", os.cpu_count() or 1))
    effective_n_jobs = min(requested_n_jobs, os.cpu_count() or requested_n_jobs)

    print("正在从 OpenML 下载 Covertype 数据集...")
    dataset = openml.datasets.get_dataset(159, download_data=True)

    X, y, categorical_indicator, attribute_names = dataset.get_data(
        target=dataset.default_target_attribute
    )

    print(f"数据集加载成功！样本数: {X.shape[0]}, 特征数: {X.shape[1]}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("开始训练 CascadeForestClassifier...")
    print(f"使用 n_jobs={effective_n_jobs}")
    model = CascadeForestClassifier(
        n_jobs=effective_n_jobs,
        random_state=42,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred) * 100
    print(f"测试集准确率 (Testing Accuracy): {acc:.3f}%")


if __name__ == "__main__":
    main()
