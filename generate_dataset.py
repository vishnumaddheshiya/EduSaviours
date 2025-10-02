#!/usr/bin/env python3
"""
Generate a realistic synthetic dataset for dropout prediction
This creates a CSV file that matches the features mentioned in the problem statement
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime

def generate_synthetic_dataset(n_samples=2000, output_file='student_dataset.csv'):
    """Generate a synthetic dataset with realistic correlations"""
    
    print(f"Generating {n_samples} synthetic student records...")
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    for i in range(n_samples):
        # Demographics
        marital_status = np.random.choice([1, 2, 3, 4, 5, 6], p=[0.85, 0.08, 0.03, 0.02, 0.01, 0.01])  # Most single
        age_at_enrollment = np.random.normal(20, 2.5)
        age_at_enrollment = max(17, min(35, age_at_enrollment))  # Clamp between 17-35
        gender = np.random.choice([0, 1], p=[0.52, 0.48])  # Slightly more females
        
        # Application details
        application_mode = np.random.randint(1, 58)  # Various application modes
        application_order = np.random.choice([1, 2, 3, 4, 5, 6], p=[0.4, 0.25, 0.15, 0.1, 0.06, 0.04])
        course = np.random.randint(9003, 9991)  # Course codes
        daytime_evening_attendance = np.random.choice([0, 1], p=[0.75, 0.25])  # Most daytime
        
        # Educational background
        previous_qualification = np.random.randint(1, 52)
        nationality = np.random.choice([1, 2, 6, 11, 13, 14, 17, 21, 25, 26, 32, 41, 62, 100, 101, 103, 105, 108, 109], 
                                    p=[0.85, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005])
        
        # Family background (affects dropout risk)
        mothers_qualification = np.random.randint(1, 47)
        fathers_qualification = np.random.randint(1, 47)
        mothers_occupation = np.random.randint(0, 195)
        fathers_occupation = np.random.randint(0, 195)
        
        # Special circumstances
        displaced = np.random.choice([0, 1], p=[0.95, 0.05])
        educational_special_needs = np.random.choice([0, 1], p=[0.97, 0.03])
        debtor = np.random.choice([0, 1], p=[0.8, 0.2])
        tuition_fees_up_to_date = np.random.choice([0, 1], p=[0.15, 0.85])
        scholarship_holder = np.random.choice([0, 1], p=[0.7, 0.3])
        international = np.random.choice([0, 1], p=[0.92, 0.08])
        
        # Academic performance - 1st semester
        # These are correlated - better students tend to perform consistently
        base_performance = np.random.normal(0.7, 0.2)  # Base academic ability
        base_performance = max(0.1, min(1.0, base_performance))
        
        curricular_units_1st_sem_credited = np.random.randint(0, 20)
        curricular_units_1st_sem_enrolled = np.random.randint(1, 26)
        
        # Performance affects evaluations and approvals
        performance_factor = base_performance + np.random.normal(0, 0.1)
        performance_factor = max(0.1, min(1.0, performance_factor))
        
        curricular_units_1st_sem_evaluations = int(curricular_units_1st_sem_enrolled * np.random.uniform(0.7, 1.0))
        curricular_units_1st_sem_approved = int(curricular_units_1st_sem_evaluations * performance_factor)
        curricular_units_1st_sem_grade = np.random.normal(10 + performance_factor * 8, 2)
        curricular_units_1st_sem_grade = max(0, min(20, curricular_units_1st_sem_grade))
        curricular_units_1st_sem_without_evaluations = curricular_units_1st_sem_enrolled - curricular_units_1st_sem_evaluations
        
        # Academic performance - 2nd semester (correlated with 1st)
        performance_change = np.random.normal(0, 0.1)  # Small random change
        performance_factor_2nd = max(0.1, min(1.0, performance_factor + performance_change))
        
        curricular_units_2nd_sem_credited = np.random.randint(0, 20)
        curricular_units_2nd_sem_enrolled = np.random.randint(1, 26)
        curricular_units_2nd_sem_evaluations = int(curricular_units_2nd_sem_enrolled * np.random.uniform(0.7, 1.0))
        curricular_units_2nd_sem_approved = int(curricular_units_2nd_sem_evaluations * performance_factor_2nd)
        curricular_units_2nd_sem_grade = np.random.normal(10 + performance_factor_2nd * 8, 2)
        curricular_units_2nd_sem_grade = max(0, min(20, curricular_units_2nd_sem_grade))
        curricular_units_2nd_sem_without_evaluations = curricular_units_2nd_sem_enrolled - curricular_units_2nd_sem_evaluations
        
        # Economic indicators (affect all students similarly by year)
        unemployment_rate = np.random.normal(10.8, 1.5)
        inflation_rate = np.random.normal(1.4, 0.8)
        gdp = np.random.normal(1.74, 1.2)
        
        # Calculate dropout probability based on risk factors
        dropout_prob = 0.1  # Base probability
        
        # Academic risk factors
        if curricular_units_1st_sem_grade < 9.5:
            dropout_prob += 0.3
        if curricular_units_2nd_sem_grade < 9.5:
            dropout_prob += 0.3
        if curricular_units_1st_sem_approved < (curricular_units_1st_sem_enrolled * 0.5):
            dropout_prob += 0.2
        if curricular_units_2nd_sem_approved < (curricular_units_2nd_sem_enrolled * 0.5):
            dropout_prob += 0.2
        
        # Financial risk factors
        if debtor == 1:
            dropout_prob += 0.15
        if tuition_fees_up_to_date == 0:
            dropout_prob += 0.25
        if scholarship_holder == 0:
            dropout_prob += 0.1
        
        # Social risk factors
        if displaced == 1:
            dropout_prob += 0.1
        if educational_special_needs == 1:
            dropout_prob += 0.05
        if age_at_enrollment > 23:
            dropout_prob += 0.1
        if marital_status != 1:  # Not single
            dropout_prob += 0.05
        
        # Economic environment
        if unemployment_rate > 12:
            dropout_prob += 0.05
        
        # Protective factors
        if scholarship_holder == 1:
            dropout_prob -= 0.1
        if curricular_units_1st_sem_grade > 14:
            dropout_prob -= 0.1
        if curricular_units_2nd_sem_grade > 14:
            dropout_prob -= 0.1
        
        # Ensure probability is between 0 and 1
        dropout_prob = max(0.01, min(0.95, dropout_prob))
        
        # Determine target (0=Graduate, 1=Dropout, 2=Enrolled)
        rand_val = np.random.random()
        if rand_val < dropout_prob:
            target = 1  # Dropout
        elif rand_val < dropout_prob + 0.3:  # Some students still enrolled
            target = 2  # Enrolled
        else:
            target = 0  # Graduate
        
        # Create record
        record = {
            'Marital status': marital_status,
            'Application mode': application_mode,
            'Application order': application_order,
            'Course': course,
            'Daytime/evening attendance': daytime_evening_attendance,
            'Previous qualification': previous_qualification,
            'Nacionality': nationality,
            "Mother's qualification": mothers_qualification,
            "Father's qualification": fathers_qualification,
            "Mother's occupation": mothers_occupation,
            "Father's occupation": fathers_occupation,
            'Displaced': displaced,
            'Educational special needs': educational_special_needs,
            'Debtor': debtor,
            'Tuition fees up to date': tuition_fees_up_to_date,
            'Gender': gender,
            'Scholarship holder': scholarship_holder,
            'Age at enrollment': round(age_at_enrollment, 1),
            'International': international,
            'Curricular units 1st sem (credited)': curricular_units_1st_sem_credited,
            'Curricular units 1st sem (enrolled)': curricular_units_1st_sem_enrolled,
            'Curricular units 1st sem (evaluations)': curricular_units_1st_sem_evaluations,
            'Curricular units 1st sem (approved)': curricular_units_1st_sem_approved,
            'Curricular units 1st sem (grade)': round(curricular_units_1st_sem_grade, 2),
            'Curricular units 1st sem (without evaluations)': curricular_units_1st_sem_without_evaluations,
            'Curricular units 2nd sem (credited)': curricular_units_2nd_sem_credited,
            'Curricular units 2nd sem (enrolled)': curricular_units_2nd_sem_enrolled,
            'Curricular units 2nd sem (evaluations)': curricular_units_2nd_sem_evaluations,
            'Curricular units 2nd sem (approved)': curricular_units_2nd_sem_approved,
            'Curricular units 2nd sem (grade)': round(curricular_units_2nd_sem_grade, 2),
            'Curricular units 2nd sem (without evaluations)': curricular_units_2nd_sem_without_evaluations,
            'Unemployment rate': round(unemployment_rate, 2),
            'Inflation rate': round(inflation_rate, 2),
            'GDP': round(gdp, 2),
            'Target': target
        }
        
        data.append(record)
        
        if (i + 1) % 500 == 0:
            print(f"Generated {i + 1} records...")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    # Print statistics
    print(f"\nDataset generated successfully: {output_file}")
    print(f"Total records: {len(df)}")
    print("\nTarget distribution:")
    print(df['Target'].value_counts().sort_index())
    print(f"Graduate: {(df['Target'] == 0).sum()} ({(df['Target'] == 0).mean()*100:.1f}%)")
    print(f"Dropout: {(df['Target'] == 1).sum()} ({(df['Target'] == 1).mean()*100:.1f}%)")
    print(f"Enrolled: {(df['Target'] == 2).sum()} ({(df['Target'] == 2).mean()*100:.1f}%)")
    
    print(f"\nKey statistics:")
    print(f"Average age at enrollment: {df['Age at enrollment'].mean():.1f}")
    print(f"Scholarship holders: {(df['Scholarship holder'] == 1).mean()*100:.1f}%")
    print(f"Students with debt: {(df['Debtor'] == 1).mean()*100:.1f}%")
    print(f"Tuition up to date: {(df['Tuition fees up to date'] == 1).mean()*100:.1f}%")
    print(f"Average 1st sem grade: {df['Curricular units 1st sem (grade)'].mean():.2f}")
    print(f"Average 2nd sem grade: {df['Curricular units 2nd sem (grade)'].mean():.2f}")
    
    return df

if __name__ == "__main__":
    # Generate dataset
    dataset = generate_synthetic_dataset(2000, 'student_dataset.csv')
    
    print("\nDataset generation complete!")
    print("You can now use this dataset to train the machine learning model.")
    print("The dataset includes all 35 features mentioned in your problem statement.")
