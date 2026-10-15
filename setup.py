from setuptools import setup, find_packages
setup(
    name="farm_ai",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy", "pandas", "scikit-learn", "joblib",
        "streamlit", "plotly", "requests", "python-dotenv",
    ],
)
