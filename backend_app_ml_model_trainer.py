import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import logging

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
    
    def prepare_time_series_data(self, data, target_col, look_back=12):
        """Prépare les données pour les modèles de séries temporelles"""
        # Normalisation des données
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data[[target_col]])
        
        # Création de séquences pour LSTM
        X, y = [], []
        for i in range(len(scaled_data) - look_back):
            X.append(scaled_data[i:(i + look_back), 0])
            y.append(scaled_data[i + look_back, 0])
        
        return np.array(X), np.array(y), scaler
    
    def train_lstm_model(self, X_train, y_train, X_val, y_val):
        """Entraîne un modèle LSTM pour les prédictions de séries temporelles"""
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25))
        model.add(Dense(1))
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        
        # Callbacks pour sauvegarder le meilleur modèle
        callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint('best_lstm_model.h5', save_best_only=True)
        ]
        
        history = model.fit(
            X_train, y_train,
            epochs=100,
            batch_size=32,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=0
        )
        
        return model, history
    
    def train_xgboost_model(self, X_train, y_train):
        """Entraîne un modèle XGBoost"""
        model = XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Extraire l'importance des caractéristiques
        feature_importance = model.get_booster().get_score(importance_type='weight')
        
        return model, feature_importance
    
    def train_sarima_model(self, data, target_col, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)):
        """Entraîne un modèle SARIMA"""
        model = SARIMAX(
            data[target_col],
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        results = model.fit(disp=False)
        
        return results
    
    def train_prophet_model(self, data, target_col):
        """Entraîne un modèle Prophet"""
        # Préparation des données pour Prophet
        prophet_df = data.reset_index()
        prophet_df = prophet_df.rename(columns={
            prophet_df.columns[0]: 'ds',  # Colonne de date
            target_col: 'y'  # Colonne cible
        })
        
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )
        
        model.fit(prophet_df)
        
        return model
    
    def evaluate_model(self, model, X_test, y_test, model_type):
        """Évalue les performances du modèle"""
        if model_type == 'lstm':
            predictions = model.predict(X_test)
            # Inverser la normalisation pour obtenir les prédictions réelles
            predictions = self.scalers[model_type].inverse_transform(predictions)
            y_test = self.scalers[model_type].inverse_transform(y_test.reshape(-1, 1))
        elif model_type == 'sarima':
            predictions = model.get_forecast(steps=len(X_test))
            predictions = predictions.predicted_mean
        elif model_type == 'prophet':
            future = model.make_future_dataframe(periods=len(X_test))
            forecast = model.predict(future)
            predictions = forecast.iloc[-len(X_test):]['yhat'].values
        else:  # xgboost, random forest, etc.
            predictions = model.predict(X_test)
        
        # Calculer les métriques
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2_score': r2
        }
    
    def train_all_models(self, data, target_col, test_size=0.2):
        """Entraîne tous les modèles et retourne les performances"""
        # Diviser les données en ensembles d'entraînement et de test
        train_data, test_data = train_test_split(data, test_size=test_size, shuffle=False)
        
        results = {}
        
        # Entraîner le modèle LSTM
        X_train, y_train, scaler_lstm = self.prepare_time_series_data(train_data, target_col)
        X_test, y_test, _ = self.prepare_time_series_data(test_data, target_col)
        
        # Reshape pour LSTM [samples, time_steps, features]
        X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
        
        self.scalers['lstm'] = scaler_lstm
        lstm_model, _ = self.train_lstm_model(X_train, y_train, X_test, y_test)
        results['lstm'] = self.evaluate_model(lstm_model, X_test, y_test, 'lstm')
        self.models['lstm'] = lstm_model
        
        # Entraîner le modèle XGBoost
        # Préparer les données pour XGBoost (créer des caractéristiques temporelles)
        xgb_data = self.create_time_series_features(data, target_col)
        xgb_train, xgb_test = train_test_split(xgb_data, test_size=test_size, shuffle=False)
        
        X_train_xgb = xgb_train.drop(target_col, axis=1)
        y_train_xgb = xgb_train[target_col]
        X_test_xgb = xgb_test.drop(target_col, axis=1)
        y_test_xgb = xgb_test[target_col]
        
        xgb_model, feature_importance = self.train_xgboost_model(X_train_xgb, y_train_xgb)
        results['xgboost'] = self.evaluate_model(xgb_model, X_test_xgb, y_test_xgb, 'xgboost')
        self.feature_importance['xgboost'] = feature_importance
        self.models['xgboost'] = xgb_model
        
        # Entraîner le modèle SARIMA
        sarima_model = self.train_sarima_model(train_data, target_col)
        results['sarima'] = self.evaluate_model(sarima_model, test_data.drop(target_col, axis=1), test_data[target_col], 'sarima')
        self.models['sarima'] = sarima_model
        
        # Entraîner le modèle Prophet
        prophet_model = self.train_prophet_model(train_data, target_col)
        results['prophet'] = self.evaluate_model(prophet_model, test_data.drop(target_col, axis=1), test_data[target_col], 'prophet')
        self.models['prophet'] = prophet_model
        
        return results
    
    def create_time_series_features(self, data, target_col):
        """Crée des caractéristiques temporelles pour les modèles de ML"""
        df = data.copy()
        
        # Caractéristiques temporelles
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        df['year'] = df.index.year
        
        # Lag features
        for i in range(1, 13):  # 12 mois de retard
            df[f'lag_{i}'] = df[target_col].shift(i)
        
        # Moyennes mobiles
        df['rolling_mean_3'] = df[target_col].rolling(window=3).mean()
        df['rolling_mean_6'] = df[target_col].rolling(window=6).mean()
        df['rolling_mean_12'] = df[target_col].rolling(window=12).mean()
        
        # Différences
        df['diff_1'] = df[target_col].diff(1)
        df['diff_12'] = df[target_col].diff(12)
        
        # Supprimer les valeurs NaN résultantes
        df = df.dropna()
        
        return df