**Live demo:** https://martins-codebreaker.streamlit.app

# CodeBreaker

> Deconstruct, Analyze, and Architect Systems with AI-Driven Engineering Insights.

## Vision
CodeBreaker is an AI-powered code analysis and architectural blueprint platform designed to help developers and system architects analyze legacy codebases, map complex software architectures, and document engineering decisions securely and efficiently.

## Tech Stack
- **Frontend / Application Framework**: Streamlit
- **Runtime Environment**: Python 3.10+
- **Environment Management**: Python `venv`

## Setup & Installation

1. **Prerequisites**
   Ensure Python 3.10+ is installed on your system.

2. **Activate Virtual Environment**
   ```bash
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

5. **Access Application**
   Open your browser and navigate to `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

Deploying CodeBreaker to Streamlit Community Cloud is streamlined with zero code changes required.

### Required Secret Names (Set in Cloud Dashboard)
In your Streamlit Cloud app settings under **Secrets**, configure the following secret keys (values must be kept strictly in the cloud dashboard and never committed to version control):
- `GROQ_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

### Deployment Steps
1. Push your repository to GitHub (ensure `.env` is excluded via `.gitignore`).
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/) and click **New app**.
3. Select your repository, branch (`main`), and main file path (`app.py`).
4. Expand **Advanced settings** -> **Secrets** and enter your production `GROQ_API_KEY`, `SUPABASE_URL`, and `SUPABASE_ANON_KEY`.
5. Click **Deploy!**
