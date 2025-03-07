# 📊 Pemantauan Kualitas Udara 2013 - 2017 di 12 Stasiun Beijing 🌍

Dashboard ini menganalisis data kualitas udara dari 12 stasiun di Beijing menggunakan **Streamlit** dan **RFM Analysis**.

## 📂 Dataset

Dataset yang digunakan mencakup data kualitas udara dari tahun **2013 - 2017**.  
Sumber data: [Beijing Air Quality](https://github.com/marceloreis/HTI/tree/master/PRSA_Data_20130301-20170228)

## 🛠 Setup Environment - Anaconda

```
conda create --name airquality-ds python=3.9
conda activate airquality-ds
pip install -r requirements.txt
```

## 🛠 Setup Environment - Shell/Terminal

```
mkdir dashboard_air_quality
cd dashboard_air_quality
pipenv install
pipenv shell
pip install -r requirements.txt
```

## 🚀 Run streamlit app

```
streamlit run dashboard.py
```
