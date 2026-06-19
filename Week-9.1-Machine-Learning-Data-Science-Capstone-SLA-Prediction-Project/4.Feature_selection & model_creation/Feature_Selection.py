import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import RFE

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

# (added because your code uses them)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import confusion_matrix, accuracy_score, classification_report


class RFE_class:

    @staticmethod
    def cm_prediction(classifier, X_test, y_test):
        y_pred = classifier.predict(X_test)

        cm = confusion_matrix(y_test, y_pred)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)

        return accuracy, report, cm

    @staticmethod
    def logistic(X_train, y_train, X_test, y_test):
        model = LogisticRegression(max_iter=5000, solver='liblinear')
        model.fit(X_train, y_train)
        accuracy, report, cm = RFE_class.cm_prediction(model, X_test, y_test)
        return accuracy

    @staticmethod
    def svm_linear(X_train, y_train, X_test, y_test):
        model = SVC(kernel='linear', random_state=0)
        model.fit(X_train, y_train)
        accuracy, report, cm = RFE_class.cm_prediction(model, X_test, y_test)
        return accuracy

    @staticmethod
    def svm_rbf(X_train, y_train, X_test, y_test):
        model = SVC(kernel='rbf', random_state=0)
        model.fit(X_train, y_train)
        accuracy, report, cm = RFE_class.cm_prediction(model, X_test, y_test)
        return accuracy

    @staticmethod
    def naive_bayes(X_train, y_train, X_test, y_test):
        model = GaussianNB()
        model.fit(X_train, y_train)
        accuracy, report, cm = RFE_class.cm_prediction(model, X_test, y_test)
        return accuracy

    @staticmethod
    def knn(X_train, y_train, X_test, y_test):
        model = KNeighborsClassifier(n_neighbors=5)
        model.fit(X_train, y_train)
        accuracy, report, cm = RFE_class.cm_prediction(model, X_test, y_test)
        return accuracy

    @staticmethod
    def decision_tree(X_train, y_train, X_test, y_test):
        model = DecisionTreeClassifier(random_state=0)
        model.fit(X_train, y_train)
        accuracy, report, cm = RFE_class.cm_prediction(model, X_test, y_test)
        return accuracy

    @staticmethod
    def random_forest(X_train, y_train, X_test, y_test):
        model = RandomForestClassifier(n_estimators=10, random_state=0)
        model.fit(X_train, y_train)
        accuracy, report, cm = RFE_class.cm_prediction(model, X_test, y_test)
        return accuracy

    @staticmethod
    def rfe_regression(acclin, accsvml, accsvmnl, accdes, accrf):

        df = pd.DataFrame(
            index=['RFE_Logistic', 'RFE_SVC', 'RFE_DecisionTree', 'RFE_RandomForest'],
            columns=['Logistic', 'SVM_Linear', 'SVM_RBF', 'Decision', 'Random']
        )

        for i, idx in enumerate(df.index):
            df.loc[idx, 'Logistic'] = acclin[i]
            df.loc[idx, 'SVM_Linear'] = accsvml[i]
            df.loc[idx, 'SVM_RBF'] = accsvmnl[i]
            df.loc[idx, 'Decision'] = accdes[i]
            df.loc[idx, 'Random'] = accrf[i]

        return df

    @staticmethod
    def Result():

        dataset = pd.read_csv(
            r"D:\python1\Week-9.1-Machine-Learning-Data-Science-Capstone-SLA-Prediction-Project\2.Data preprocessing\preprocessed_data.csv"
        )

        dataset1 = pd.get_dummies(dataset, drop_first=True)

        X = dataset1.drop("SLA_Breached", axis=1)
        y = dataset1["SLA_Breached"]

        feature_names = X.columns

        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=0
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_raw)
        X_test_scaled = scaler.transform(X_test_raw)

        rfemodellist = [
            LogisticRegression(max_iter=5000, solver='liblinear'),
            SVC(kernel='linear'),
            RandomForestClassifier(n_estimators=10, random_state=0),
            DecisionTreeClassifier(random_state=0)
        ]

        acclin, accsvml, accsvmnl, accdes, accrf = [], [], [], [], []

        for model in rfemodellist:

            rfe = RFE(
                estimator=model,
                n_features_to_select=20,
                step=1
            )

            X_train_rfe = rfe.fit_transform(X_train_scaled, y_train)
            X_test_rfe = rfe.transform(X_test_scaled)

            acclin.append(RFE_class.logistic(X_train_rfe, y_train, X_test_rfe, y_test))
            accsvml.append(RFE_class.svm_linear(X_train_rfe, y_train, X_test_rfe, y_test))
            accsvmnl.append(RFE_class.svm_rbf(X_train_rfe, y_train, X_test_rfe, y_test))
            accdes.append(RFE_class.decision_tree(X_train_rfe, y_train, X_test_rfe, y_test))
            accrf.append(RFE_class.random_forest(X_train_rfe, y_train, X_test_rfe, y_test))

        result = RFE_class.rfe_regression(
            acclin, accsvml, accsvmnl, accdes, accrf
        )

        best_idx = result.stack().idxmax()

        return result, best_idx


