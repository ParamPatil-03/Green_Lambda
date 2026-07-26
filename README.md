# ⚡ Green Lambda

> **Predict Before You Deploy.**  
> A Machine Learning-driven energy and carbon footprint prediction platform for AWS Lambda serverless workloads.

Green Lambda merges static code attributes with dynamic cloud metrics to estimate the energy consumption of your AWS Lambda functions *before* deployment. By feeding architectural configurations alongside live telemetry into advanced Machine Learning models, developers can directly calculate Carbon Emissions, Cloud Costs, and Energy footprints before pushing code to production.

---

## 🎯 The Problem & The Solution

Serverless computing obscures energy usage. Current profiling tools focus entirely on execution time and latency, keeping the true energy consumption of functions opaque.  

**Green Lambda** bridges this gap:
1. **Extracts Features:** Mines static attributes (cyclomatic complexity, code nesting, lines of code) and dynamic AWS metrics (memory provisions, cold starts) via local code analysis and cloud telemetry.
2. **ML Predictions:** Processes variables through highly-trained Machine Learning algorithms (XGBoost, Random Forest, Neural Networks) predicting on a physically grounded formula: `Energy (Wh) = ((10 + 0.2 × memory_mb) × duration_ms) / 3600000`.
3. **Explains Predictions:** Integrates SHAP (SHapley Additive exPlanations) and LIME to transparently explain which specific parameters (e.g., memory configuration vs. loop counts) drove the prediction.
4. **Simulates Demand:** Stress-tests applications across customizable timelines to project real-world carbon usage and precise billing impacts at scale during traffic spikes.

---

## ✨ Core Features

- **Live AWS Telemetry Integration:** Using Boto3, Green Lambda syncs securely with your AWS account to discover deployed functions and continuously extract CloudWatch `Duration` and `MaxMemoryUsed` data.
- **Continuous AST Profiling:** Dynamically fetches raw Lambda code bundles and scans them locally using Python Abstract Syntax Trees (`radon`) for deep complexity metrics.
- **High-Accuracy ML Engine:** Houses three predictive models trained on a robust serverless execution dataset:
  - **XGBoost (Active Model Mode):** R² = 0.9998, MAPE = 2.41%
  - **Random Forest:** R² = 0.9993, MAPE = 6.70%
  - **Deep Neural Networks (MLPRegressor):** R² = 0.9997, MAPE = 71.64%
- **Multi-Model SHAP/LIME Interpretability Stack:** Provides real-time, local feature attribution highlighting actionable summaries highlighting code-level complexity drivers (e.g., loops, LOC) alongside memory config parameters.
- **Prediction Gap Analysis (Validation):** Dynamically compares CloudWatch telemetry (Formula-based actual energy) with ML predictions to diagnose deviation gaps in real-time. Highlights minor vs. significant deviations with amber/red severity badges, visualizes the gap's drivers in a mini-SHAP chart, and gives automated optimization suggestions.
- **Cross-Platform Transferability Insights:** Models have been validated against traces from Alibaba Cloud (Strong transfer: R² = 0.6997) and Microsoft Azure (Weak transfer: R² = -2.497).
- **Interactive UI Dashboard:** A purely front-end client written seamlessly with standard HTML/JS, leveraging Chart.js for energy distribution comparisons and GSAP for fluid web animations.

## ⚠️ Known Limitations
- **Weak Azure Generalization:** As noted above, the model struggles to generalize to Azure (R² = -2.497). Azure dynamically allocates memory on a continuous spectrum (unlike AWS/Alibaba's discrete configurations) and exhibits higher variance skew, limiting the model's out-of-the-box accuracy on Azure.
- **Sub-1-Second Inaccuracy:** Model reliability drops (higher relative error percentage) for functions completing in under 1 second (e.g., sub-10ms), as fixed invocation and runtime overheads heavily distort the baseline energy.
- **Prediction Clipping:** Extreme outlier configurations (ultra-high memory combined with ultra-short execution durations) may result in negative energy predictions, requiring a floor clipping layer at 0.0001 Wh.

---

## 🛠️ Technology Stack

**Frontend:**
- HTML5, Vanilla JavaScript, Vanilla CSS.
- **Chart.js** & **GSAP** (Animations).
- Supabase (Authentication & User management integration).

**Backend (Python Flask REST API):**
- **Flask** & **Flask-CORS** for REST API endpoints.
- **boto3** for AWS lambda code & CloudWatch telemetry retrieval.
- **radon** for AST-based code complexity analysis on the fly.

**Machine Learning (Models & Interpretability):**
- **xgboost**, **scikit-learn** (Model wrappers, scaling, metrics).
- **pandas**, **numpy** (Matrix operations & Dataset Handling).
- **SHAP** & **LIME** (Mathematical game-theoretic explanations for predictions).
- **matplotlib** (For publication-quality academic figure generation).

---

## 📊 Dataset Overview
The model is trained on a comprehensive dataset compiled from executed serverless workloads:
- **175 Lambda Functions:** (25 original benchmarks + 150 expansion functions, sourced/adapted from the Serverless Benchmark Suite / SeBS)
- **6,132 Execution Records** across 8 workload categories
- **Memory Range:** 128 MB to 3,000 MB
- **Duration Range:** up to 66.9 seconds
- **Lambda Runtime:** Python 3.11 exclusively

---

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.13.5**
- **AWS Account** with Read-Only Lambda and CloudWatch execution permissions (If connecting Live AWS).

### Getting Started

For Windows users, we provide a unified startup script to streamline backend initialization and frontend launching.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/green-lambda.git
   cd green-lambda
   ```

2. **Quick Launch (Windows):**
   Simply double-click or run the `Start_GreenLambda.bat` script located in the root of the project:
   ```cmd
   Start_GreenLambda.bat
   ```
   > *Note:* This batch script automatically activates the machine learning virtual environment, boots up the local Flask server on Port 5000, and opens the frontend UI in your default web browser!

3. **Manual Launch:**
   *Setting up the backend:*
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate       # On Windows use: venv\Scripts\activate
   pip install -r ../requirements.txt
   python app.py
   ```
   
   *Opening the frontend:*
   Simply open `index.html` in your web browser of choice.

---

## 🔬 Reproducibility Details
To reproduce the findings in our research, ensure your environment matches the following configurations:
- **Python Version:** 3.13.5
- **Library Versions:**
  - XGBoost: `3.2.0`
  - scikit-learn: `1.8.0`
  - pandas: `3.0.1`
  - numpy: `2.4.3`
  - SHAP: `0.51.0`
  - LIME: `0.2.0.1`
  - radon: `6.0.1`
  - boto3: `1.42.73`
- **Random Seed:** A fixed seed of `random_state=42` is used strictly across all scripts for train/test splits, cross-validation, and model initializations.
- **Infrastructure:** Run entirely on standard, unmodified AWS Lambda; no special infrastructure access or instrumentation was required. Training hardware consisted of standard desktop/laptop CPUs.

---

## 📂 Project Structure

```
├── index.html                  # Landing Page / Engine Walkthrough
├── dashboard.html              # Main ML Statistics Dashboard Component
├── analyze.html                # Engine analysis page detailing SHAP explanations
├── connect.html                # UI flow for AWS Boto3 Key Injection
├── runtime-test.html           # Live validation and Gap Analysis (CloudWatch vs. ML)
├── login.html                  # Supabase Authentication Interface
├── style.css & script.js       # Core styles and interaction scripts
│
├── Start_GreenLambda.bat       # Auto-deploy Batch Script (Windows)
├── requirements.txt            # Python Dependencies
│
├── backend/
│   ├── app.py                  # Core Flask REST Application
│   ├── model_loader.py         # Singleton loader for ML models and scaler
│   ├── shap_explainer.py       # Multi-model SHAP explanation engine
│   ├── models/                 # Pre-trained XGBoost, RF, NN (.pkl files)
│   └── results/                # Output metrics, comparison logs, and cached charts
│
└── ml_model/
    ├── train_v3.py             # Script for Model Training
    ├── final_ml_dataset_clean.csv # Core Serverless parameter dataset
    └── new_ml_dataset.csv      # Processed dataset file
```

*(Note: The `export_shap_figures.py` script has been deprecated from the main pipeline as the V3 figures are now manually generated via `generate_v3_figures.py` as needed.)*

---

## 🔐 AWS Security & Privacy

Green Lambda requires AWS `Access Key ID` and `Secret Access Key` exclusively to pull metric summaries and Lambda code zip files strictly for AST parsing on your local machine.

- **No Data Harvesting:** Credentials are mathematically retained purely in the localized running Flask session and never uploaded to public databases.
- **Demo Mode:** If you do not have an AWS account on hand, the application supports a built-in Demo mode that falls back to dataset median/mode imputation for unrecognized functions, clearly flagged with reduced confidence to distinguish it from genuine live predictions.

---

## 👨‍💻 Contributing & Purpose

This framework serves as a Mini Project for Semester 4, aiming to empower stakeholders (Developers, Cloud Architects, and DevOps Teams) to proactively minimize their un-calculated web footprint.

Making sustainable programming a pre-requisite, not an afterthought.
