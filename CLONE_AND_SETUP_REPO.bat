@echo off

git clone https://github.com/Brunner246/IFCComparator.git
cd IFCComparator

python -m venv .venv

call .venv\Scripts\activate

pip install -r requirements.txt

echo IFCComparator Repository cloned and packages installed successfully.