import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer 
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


class SLA_prediction:

    @staticmethod
    def decision_tree(X_train_enc, X_test_enc, y_train, y_test):

        base_estimator = DecisionTreeClassifier(random_state=42)

        # safer feature selection
        n_features = min(20, X_train_enc.shape[1])

        rfe = RFE(
            estimator=base_estimator,
            n_features_to_select=n_features,
            step=10
        )

        X_train_rfe = rfe.fit_transform(X_train_enc, y_train)
        X_test_rfe = rfe.transform(X_test_enc)

        final_model = DecisionTreeClassifier(random_state=42)
        final_model.fit(X_train_rfe, y_train)

        y_pred = final_model.predict(X_test_rfe)

        print("Accuracy:", accuracy_score(y_test, y_pred))

        return final_model, rfe


    @staticmethod
    def Result():

        dataset = pd.read_csv(
            r"D:\python1\Week-9.1-Machine-Learning-Data-Science-Capstone-SLA-Prediction-Project\2.Data preprocessing\preprocessed_data.csv"
        )

        X = dataset.drop("SLA_Breached", axis=1)
        y = dataset["SLA_Breached"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        cat_cols = [
            "Incident_ID", "Incident_Type", "Priority",
            "Assigned_Department", "Location", "Status",
            "Resolution_Type"
        ]

        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown='ignore'), cat_cols)
            ],
            remainder="passthrough"
        )

        X_train_enc = preprocessor.fit_transform(X_train)
        X_test_enc = preprocessor.transform(X_test)

        print("Encoded Train Shape:", X_train_enc.shape)

        model, rfe = SLA_prediction.decision_tree(
            X_train_enc, X_test_enc, y_train, y_test
        )

        joblib.dump(preprocessor, "preprocessor.pkl")
        joblib.dump(rfe, "rfe_selector.pkl")
        joblib.dump(model, "SLA_prediction_model.pkl")

        print("Models saved successfully")


