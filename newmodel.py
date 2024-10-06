import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import joblib

# Load dataset
electric = pd.read_csv('ElectricalWorks.csv')

# Features and target variable
x = electric.drop(['id', 'title', 'gov_est_price', 'percentage', 'org'], axis=1)
y = electric['gov_est_price']

# Split dataset
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=2)

# Initialize and train the model
linear = LinearRegression()
linear.fit(x_train, y_train)

# Save the trained model
joblib.dump(linear, 'linearElectrical_model.pkl')

# Make predictions
prediction = linear.predict(x_test)
r2_score = metrics.r2_score(y_test, prediction)
print(f"R2 Score: {r2_score}")

