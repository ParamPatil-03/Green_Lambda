# ⚡ Green Lambda

> **Predict Before You Deploy.**
> A Machine Learning-driven energy prediction framework for serverless workloads.

Green Lambda merges static code attributes with dynamic cloud metrics to estimate the energy consumption of your AWS Lambda functions *before* deployment. By feeding architectural configurations alongside live telemetry into advanced Machine Learning models, developers can directly calculate Carbon Emissons, Cloud Costs, and Energy foot-prints before pushing code to production.

---

## 🎯 The Problem & The Solution

Serverless computing obscures energy usage. Current profiling tools focus entirely on execution time and latency, keeping the true energy consumption of functions opaque.  

**Green Lambda** bridges this gap:
1. **Extracts Features:** Mines static attributes (cyclomatic complexity, code nesting, lines of code) and dynamic AWS metrics (memory provisions, cold starts).
2. **ML Predictions:** Processes variables through highly-trained Machine Learning algorithms (XGBoost, Random Forest, Neural Networks).
3. **Simulates Demand:** Artificially stresses the prediction model with high-traffic spikes to confidently project real-world carbon usage and precise billing (INR) impacts at scale.

---

## ✨ Core Features

- **Live AWS Telemetry Integration:** Using Boto3, Green Lambda syncs securely with your AWS account to discover deployed functions and continuously extract CloudWatch `Duration` and `MaxMemoryUsed` data.
- **Continuous AST Profiling:** Dynamically fetches raw Lambda code bundles and scans them locally using Python Abstract Syntax Trees (`radon`) for deep complexity metrics.
- **High-Accuracy ML Engine:** Houses three predictive models trained on serverless execution datasets:
  - **XGBoost (Active Model Mode)**
  - Random Forest
  - Deep Neural Networks
- **Demand Burst Simulation:** Stress tests applications across customizable timelines (e.g., 72 hours) allowing DevOps teams to actively multiply baseline load and predict carbon penalties during huge virality events.
- **Interactive UI Dashboard:** A purely front-end client written seamlessly with standard HTML/JS, leveraging Chart.js for energy distrubtion comparisons and GSAP for fluid web animations.

---

## 🛠️ Technology Stack

**Frontend:**
- HTML5, Vanilla JavaScript, Custom CSS.
- **Chart.js** & **GSAP** (Animations).
- Supabase (Used for potential Auth).

**Backend (Python Flask):**
- **Flask** & **Flask-CORS** for REST API endpoints. 
- **boto3** for AWS lambda code & CloudWatch pulling.
- **radon** for on-the-fly Cyclomatic Complexity analysis against Python functions.

**Machine Learning (Models & Data):**
- **xgboost**, **scikit-learn** (Model generation, Scalers).
- **pandas**, **numpy** (Matrix operations & Dataset Handling).
- **SHAP** (Underlying mathematics mapping feature priorities).

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

---

## 📂 Project Structure

```
├── index.html                  # Landing Page / Engine Walkthrough
├── dashboard.html              # Main ML Statistics Frontend Component
├── connect.html                # UI flow for AWS Boto3 Key Injection
├── runtime-test.html           # Live validation between ML & CloudWatch
├── login.html                  # Supabase Authentication Interface
├── style.css & script.js       # Core styles and interaction scripts
│
├── Start_GreenLambda.bat       # Auto-deploy Batch Script (Windows)
├── requirements.txt            # Python Dependencies
│
├── backend/
│   ├── app.py                  # Core Flask REST Application
│   ├── models/                 # Pre-trained XGBoost, RF, NN (.pkl files)
│   └── results/                # Output graphs & Scatter logs
│
└── ml_model/
    ├── model.ipynb             # ML Jupyter Notebook detailing Training
    ├── venv/                   # Active Python virtual environment 
    └── final_ml_dataset_clean.csv # Deep Serverless parameter dataset
```

---

## 🔐 AWS Security & Privacy

Green Lambda requires AWS `Access Key ID` and `Secret Access Key` exclusively to pull metric summaries and Lambda code zip files strictly for AST parsing on your local machine.

- **No Data Harvesting:** Credentials are mathematically retained purely in the localized running Flask session and never uploaded to public databases.
- **Demo Mode:** If you do not have an AWS account on hand, the application supports a built-in Demo mode that falls back to localized historical metrics to vividly display the power of the ML engine safely.

---

## 👨‍💻 Contributing & Purpose

This framework serves as a Mini Project for Semester 4, aiming to empower stakeholders (Developers, Cloud Architects, and DevOps Teams) to proactively minimize their un-calculated web footprint. 

Making sustainable programming a pre-requisite, not an afterthought.
