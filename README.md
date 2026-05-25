# ⚡ Green Lambda

> **Predict Before You Deploy.**  
> A Machine Learning-driven energy and carbon footprint prediction platform for AWS Lambda serverless workloads.

Green Lambda merges static code attributes with dynamic cloud metrics to estimate the energy consumption of your AWS Lambda functions *before* deployment. By feeding architectural configurations alongside live telemetry into advanced Machine Learning models, developers can directly calculate Carbon Emissions, Cloud Costs, and Energy footprints before pushing code to production.

---

## 🎯 The Problem & The Solution

Serverless computing obscures energy usage. Current profiling tools focus entirely on execution time and latency, keeping the true energy consumption of functions opaque.  

**Green Lambda** bridges this gap:
1. **Extracts Features:** Mines static attributes (cyclomatic complexity, code nesting, lines of code) and dynamic AWS metrics (memory provisions, cold starts) via local code analysis and cloud telemetry.
2. **ML Predictions:** Processes variables through highly-trained Machine Learning algorithms (XGBoost, Random Forest, Neural Networks).
3. **Explains Predictions:** Integrates SHAP (SHapley Additive exPlanations) to transparently explain which specific parameters (e.g., memory configuration vs. loop counts) drove the prediction.
4. **Simulates Demand:** Stress-tests applications across customizable timelines to project real-world carbon usage and precise billing (INR) impacts at scale during traffic spikes.

---

## ✨ Core Features

- **Live AWS Telemetry Integration:** Using Boto3, Green Lambda syncs securely with your AWS account to discover deployed functions and continuously extract CloudWatch `Duration` and `MaxMemoryUsed` data.
- **Continuous AST Profiling:** Dynamically fetches raw Lambda code bundles and scans them locally using Python Abstract Syntax Trees (`radon`) for deep complexity metrics.
- **High-Accuracy ML Engine:** Houses three predictive models trained on serverless execution datasets:
  - **XGBoost (Active Model Mode)**
  - **Random Forest**
  - **Deep Neural Networks (MLPRegressor)**
- **Multi-Model SHAP Interpretability Stack:** Provides real-time, local feature attribution. Supports:
  - XGBoost & Random Forest via TreeExplainer
  - Deep Neural Network via KernelExplainer (accelerated via k-means background sampling)
  - Interactive dual-tab display mapping exact feature impacts (color-coded red/green glows indicating increase/decrease) and model baseline contribution progress flow.
  - Actionable summaries highlighting code-level complexity drivers (e.g., loops, LOC) alongside memory config parameters.
- **Prediction Gap Analysis (Validation):** Dynamically compares CloudWatch telemetry (actual energy) with ML predictions to diagnose deviation gaps in real-time. Highlights minor vs. significant deviations with amber/red severity badges, visualizes the gap's drivers in a mini-SHAP chart, and gives automated optimization suggestions.
- **Demand Burst Simulation:** Stress tests applications across customizable timelines (e.g., 72 hours) allowing DevOps teams to actively multiply baseline load and predict carbon penalties during viral traffic events.
- **IEEE Paper Figures Exporter:** Contains a publication-quality figure exporter (`export_shap_figures.py`) that outputs 300 DPI figures with light/white backgrounds for academic submissions:
  1. Global Feature Importance Bar Chart (`fig1_global_importance.png`)
  2. SHAP Summary Beeswarm Plot (`fig2_shap_summary.png`)
  3. Local Explanation Waterfall Plot (`fig3_local_waterfall.png`)
  4. Model Performance Comparison Chart (`fig4_model_comparison.png`)
- **Interactive UI Dashboard:** A purely front-end client written seamlessly with standard HTML/JS, leveraging Chart.js for energy distribution comparisons and GSAP for fluid web animations.

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
- **SHAP** (Mathematical game-theoretic explanations for predictions).
- **matplotlib** (For publication-quality academic figure generation).

---

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.9+**
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
   > *Note:* This batch script automatically activates the machine learning virtual model, boots up the local Flask server on Port 5000, and opens the frontend UI in your default web browser!

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

4. **Generating Academic Figures (LaTeX/IEEE Paper):**
   Run the exporter script from the backend directory to update the academic images at `/ml_model/figures/`:
   ```bash
   cd backend
   python export_shap_figures.py
   ```

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
│   ├── export_shap_figures.py  # Exporter utility for IEEE publication figures
│   ├── models/                 # Pre-trained XGBoost, RF, NN (.pkl files)
│   └── results/                # Output metrics, comparison logs, and cached charts
│
└── ml_model/
    ├── model.ipynb             # Jupyter Notebook detailing Model Training
    ├── venv/                   # Active Python virtual environment 
    ├── final_ml_dataset_clean.csv # Deep Serverless parameter dataset
    └── figures/                # 300 DPI exported academic figures (PNGs)
```

---

## 🔐 AWS Security & Privacy

Green Lambda requires AWS `Access Key ID` and `Secret Access Key` exclusively to pull metric summaries and Lambda code zip files strictly for AST parsing on your local machine.

- **No Data Harvesting:** Credentials are mathematically retained purely in the localized running Flask session and never uploaded to public databases.
- **Demo Mode:** If you do not have an AWS account on hand, the application supports a built-in Demo mode that falls back to localized historical metrics and deterministic hashes of custom function names to vividly display the power of the ML engine safely.

---

## 👨‍💻 Contributing & Purpose

This framework serves as a Mini Project for Semester 4, aiming to empower stakeholders (Developers, Cloud Architects, and DevOps Teams) to proactively minimize their un-calculated web footprint.

Making sustainable programming a pre-requisite, not an afterthought.
