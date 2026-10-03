"""
Smart Home Electricity Consumption Prediction System
Predicts electricity usage using historical energy consumption patterns and machine learning
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

def generate_energy_consumption_dataset(n_samples=730, random_state=42):
    """Generate synthetic smart home electricity consumption dataset (2 years of daily data)"""
    np.random.seed(random_state)
    
    dates = pd.date_range(start='2022-01-01', periods=n_samples, freq='D')
    
    # Base consumption pattern
    day_of_year = np.arange(n_samples) % 365
    seasonal_pattern = 20 + 15 * np.sin(2 * np.pi * day_of_year / 365)  # Seasonal variation
    
    # Temperature influence (simulated)
    temperature = 20 + 15 * np.sin(2 * np.pi * day_of_year / 365) + np.random.normal(0, 5, n_samples)
    
    # Occupancy pattern (weekday vs weekend)
    day_of_week = np.array([d.dayofweek for d in dates])
    occupancy_pattern = np.where(day_of_week < 5, 1.0, 1.2)  # Higher consumption on weekends
    
    # Random daily variations
    daily_variation = np.random.normal(1.0, 0.15, n_samples)
    
    # Calculate electricity consumption (kWh)
    electricity_consumption = (seasonal_pattern * occupancy_pattern * daily_variation + 
                              np.random.normal(0, 2, n_samples))
    electricity_consumption = np.clip(electricity_consumption, 5, 60)  # Realistic range
    
    data = {
        'Date': dates,
        'Day_of_Week': day_of_week,
        'Month': np.array([d.month for d in dates]),
        'Day_of_Year': day_of_year,
        'Temperature': temperature,
        'Humidity': np.random.uniform(30, 80, n_samples),
        'Is_Weekend': (day_of_week >= 5).astype(int),
        'Is_Holiday': np.random.choice([0, 1], n_samples, p=[0.97, 0.03]),
        'Occupancy_Level': np.random.choice([1, 2, 3, 4], n_samples, p=[0.3, 0.4, 0.2, 0.1]),
        'HVAC_Usage_Hours': np.random.uniform(4, 16, n_samples),
        'Appliance_Usage_Count': np.random.randint(5, 25, n_samples),
        'Previous_Day_Consumption': np.roll(electricity_consumption, 1),
        'Electricity_Consumption_kWh': electricity_consumption
    }
    
    df = pd.DataFrame(data)
    df.loc[0, 'Previous_Day_Consumption'] = df.loc[0, 'Electricity_Consumption_kWh']
    
    return df

def preprocess_energy_data(df):
    """Preprocess energy consumption data for modeling"""
    df_processed = df.copy()
    
    feature_cols = [
        'Day_of_Week', 'Month', 'Day_of_Year', 'Temperature', 'Humidity',
        'Is_Weekend', 'Is_Holiday', 'Occupancy_Level', 'HVAC_Usage_Hours',
        'Appliance_Usage_Count', 'Previous_Day_Consumption'
    ]
    
    return df_processed, feature_cols

def train_regression_models(X_train, X_test, y_train, y_test):
    """Train multiple regression models"""
    models = {}
    results = {}
    
    # Model 1: Linear Regression
    print("Training Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    y_pred_lr = lr_model.predict(X_test)
    
    models['Linear Regression'] = lr_model
    results['Linear Regression'] = {
        'predictions': y_pred_lr,
        'mse': mean_squared_error(y_test, y_pred_lr),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred_lr)),
        'mae': mean_absolute_error(y_test, y_pred_lr),
        'r2': r2_score(y_test, y_pred_lr)
    }
    
    # Model 2: Random Forest Regressor
    print("Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    
    models['Random Forest'] = rf_model
    results['Random Forest'] = {
        'predictions': y_pred_rf,
        'mse': mean_squared_error(y_test, y_pred_rf),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred_rf)),
        'mae': mean_absolute_error(y_test, y_pred_rf),
        'r2': r2_score(y_test, y_pred_rf)
    }
    
    # Model 3: Gradient Boosting Regressor
    print("Training Gradient Boosting Regressor...")
    gb_model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
    gb_model.fit(X_train, y_train)
    y_pred_gb = gb_model.predict(X_test)
    
    models['Gradient Boosting'] = gb_model
    results['Gradient Boosting'] = {
        'predictions': y_pred_gb,
        'mse': mean_squared_error(y_test, y_pred_gb),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred_gb)),
        'mae': mean_absolute_error(y_test, y_pred_gb),
        'r2': r2_score(y_test, y_pred_gb)
    }
    
    return models, results

def plot_consumption_distribution(df):
    """Plot distribution of electricity consumption"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram
    axes[0].hist(df['Electricity_Consumption_kWh'], bins=30, color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_xlabel('Electricity Consumption (kWh)', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0].set_title('Distribution of Daily Electricity Consumption', fontsize=12, fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    axes[0].axvline(df['Electricity_Consumption_kWh'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df["Electricity_Consumption_kWh"].mean():.2f} kWh')
    axes[0].legend()
    
    # Box plot by month
    df['Month_Name'] = pd.to_datetime(df['Date']).dt.strftime('%b')
    df.boxplot(column='Electricity_Consumption_kWh', by='Month_Name', ax=axes[1])
    axes[1].set_xlabel('Month', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Electricity Consumption (kWh)', fontsize=11, fontweight='bold')
    axes[1].set_title('Monthly Electricity Consumption Distribution', fontsize=12, fontweight='bold')
    plt.sca(axes[1])
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/energy_consumption_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: energy_consumption_distribution.png")
    plt.close()

def plot_model_comparison(results, y_test):
    """Compare model performance metrics"""
    models = list(results.keys())
    metrics = ['rmse', 'mae', 'r2']
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    colors = ['#3498db', '#e74c3c', '#f39c12']
    
    # RMSE
    rmse_values = [results[m]['rmse'] for m in models]
    axes[0].bar(models, rmse_values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_ylabel('RMSE (kWh)', fontsize=11, fontweight='bold')
    axes[0].set_title('Root Mean Squared Error', fontsize=12, fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    for i, v in enumerate(rmse_values):
        axes[0].text(i, v + 0.1, f'{v:.4f}', ha='center', fontweight='bold', fontsize=9)
    
    # MAE
    mae_values = [results[m]['mae'] for m in models]
    axes[1].bar(models, mae_values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_ylabel('MAE (kWh)', fontsize=11, fontweight='bold')
    axes[1].set_title('Mean Absolute Error', fontsize=12, fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    for i, v in enumerate(mae_values):
        axes[1].text(i, v + 0.05, f'{v:.4f}', ha='center', fontweight='bold', fontsize=9)
    
    # R² Score
    r2_values = [results[m]['r2'] for m in models]
    axes[2].bar(models, r2_values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[2].set_ylabel('R² Score', fontsize=11, fontweight='bold')
    axes[2].set_title('Coefficient of Determination', fontsize=12, fontweight='bold')
    axes[2].set_ylim([0, 1])
    axes[2].grid(axis='y', alpha=0.3)
    for i, v in enumerate(r2_values):
        axes[2].text(i, v + 0.02, f'{v:.4f}', ha='center', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/energy_model_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: energy_model_comparison.png")
    plt.close()

def plot_predictions_vs_actual(results, y_test):
    """Plot predictions vs actual values"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    models = list(results.keys())
    colors = ['#3498db', '#e74c3c', '#f39c12']
    
    for idx, model_name in enumerate(models):
        y_pred = results[model_name]['predictions']
        axes[idx].scatter(y_test, y_pred, alpha=0.6, color=colors[idx], edgecolor='black', linewidth=0.5)
        axes[idx].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2, label='Perfect Prediction')
        axes[idx].set_xlabel('Actual Consumption (kWh)', fontsize=11, fontweight='bold')
        axes[idx].set_ylabel('Predicted Consumption (kWh)', fontsize=11, fontweight='bold')
        axes[idx].set_title(f'{model_name}\nR² = {results[model_name]["r2"]:.4f}', fontsize=12, fontweight='bold')
        axes[idx].legend()
        axes[idx].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/energy_predictions_vs_actual.png', dpi=300, bbox_inches='tight')
    print("Saved: energy_predictions_vs_actual.png")
    plt.close()

def plot_feature_importance(models, feature_names):
    """Plot feature importance for tree-based models"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Random Forest
    rf_importance = models['Random Forest'].feature_importances_
    rf_indices = np.argsort(rf_importance)[-10:]
    axes[0].barh(range(len(rf_indices)), rf_importance[rf_indices], 
                color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_yticks(range(len(rf_indices)))
    axes[0].set_yticklabels([feature_names[i] for i in rf_indices], fontsize=10)
    axes[0].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[0].set_title('Random Forest - Feature Importance', fontsize=12, fontweight='bold')
    axes[0].grid(axis='x', alpha=0.3)
    
    # Gradient Boosting
    gb_importance = models['Gradient Boosting'].feature_importances_
    gb_indices = np.argsort(gb_importance)[-10:]
    axes[1].barh(range(len(gb_indices)), gb_importance[gb_indices], 
                color='#f39c12', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_yticks(range(len(gb_indices)))
    axes[1].set_yticklabels([feature_names[i] for i in gb_indices], fontsize=10)
    axes[1].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[1].set_title('Gradient Boosting - Feature Importance', fontsize=12, fontweight='bold')
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/energy_feature_importance.png', dpi=300, bbox_inches='tight')
    print("Saved: energy_feature_importance.png")
    plt.close()

def plot_consumption_trends(df):
    """Plot consumption trends over time"""
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Time series plot
    axes[0].plot(df['Date'], df['Electricity_Consumption_kWh'], color='#3498db', linewidth=1.5, alpha=0.7)
    axes[0].fill_between(df['Date'], df['Electricity_Consumption_kWh'], alpha=0.3, color='#3498db')
    axes[0].set_xlabel('Date', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Consumption (kWh)', fontsize=11, fontweight='bold')
    axes[0].set_title('Daily Electricity Consumption Over Time', fontsize=12, fontweight='bold')
    axes[0].grid(alpha=0.3)
    
    # Consumption by day of week
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    consumption_by_day = df.groupby('Day_of_Week')['Electricity_Consumption_kWh'].agg(['mean', 'std'])
    axes[1].bar(range(7), consumption_by_day['mean'], yerr=consumption_by_day['std'], 
               color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5, capsize=5)
    axes[1].set_xticks(range(7))
    axes[1].set_xticklabels(day_names, rotation=45)
    axes[1].set_ylabel('Average Consumption (kWh)', fontsize=11, fontweight='bold')
    axes[1].set_title('Average Daily Consumption by Day of Week', fontsize=12, fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/energy_consumption_trends.png', dpi=300, bbox_inches='tight')
    print("Saved: energy_consumption_trends.png")
    plt.close()

def plot_temperature_correlation(df):
    """Plot temperature and consumption correlation"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(df['Temperature'], df['Electricity_Consumption_kWh'], 
                        c=df['Month'], cmap='coolwarm', alpha=0.6, s=50, edgecolor='black', linewidth=0.5)
    ax.set_xlabel('Temperature (°C)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Electricity Consumption (kWh)', fontsize=11, fontweight='bold')
    ax.set_title('Temperature vs Electricity Consumption', fontsize=12, fontweight='bold')
    ax.grid(alpha=0.3)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Month', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/energy_temperature_correlation.png', dpi=300, bbox_inches='tight')
    print("Saved: energy_temperature_correlation.png")
    plt.close()

def main():
    print("="*80)
    print("SMART HOME ELECTRICITY CONSUMPTION PREDICTION SYSTEM - ANALYSIS")
    print("="*80)
    
    # Generate dataset
    print("\n[1] Generating smart home energy consumption dataset...")
    df = generate_energy_consumption_dataset(n_samples=730)
    df.to_csv('/home/ubuntu/energy_consumption_data.csv', index=False)
    print(f"Dataset generated: {df.shape[0]} days of data")
    print(f"Average daily consumption: {df['Electricity_Consumption_kWh'].mean():.2f} kWh")
    print(f"Min consumption: {df['Electricity_Consumption_kWh'].min():.2f} kWh")
    print(f"Max consumption: {df['Electricity_Consumption_kWh'].max():.2f} kWh")
    
    # Preprocess data
    print("\n[2] Preprocessing energy consumption data...")
    df_processed, feature_cols = preprocess_energy_data(df)
    
    # Prepare features and target
    X = df_processed[feature_cols]
    y = df_processed['Electricity_Consumption_kWh']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Training set: {X_train_scaled.shape[0]} samples, {X_train_scaled.shape[1]} features")
    print(f"Test set: {X_test_scaled.shape[0]} samples")
    
    # Train models
    print("\n[3] Training regression models...")
    models, results = train_regression_models(X_train_scaled, X_test_scaled, y_train, y_test)
    
    # Print results
    print("\n[4] Model Performance Results:")
    print("-" * 80)
    for model_name, result in results.items():
        print(f"\n{model_name}:")
        print(f"  RMSE: {result['rmse']:.6f} kWh")
        print(f"  MAE:  {result['mae']:.6f} kWh")
        print(f"  R²:   {result['r2']:.6f}")
    
    # Generate visualizations
    print("\n[5] Generating visualizations...")
    plot_consumption_distribution(df)
    plot_model_comparison(results, y_test)
    plot_predictions_vs_actual(results, y_test)
    plot_feature_importance(models, feature_cols)
    plot_consumption_trends(df)
    plot_temperature_correlation(df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE - All visualizations saved")
    print("="*80)

if __name__ == "__main__":
    main()
