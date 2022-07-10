# Exchange_rates bot

## Installation
Make sure you have Python 3.9 installed.

Next download code from Git. 
```
git clone https://github.com/RomanKorinnyi/aiogram_bot
```
You need to set your bot token in the file config.py

Import libraries from requirements.txt 
```bash
pip install -r requirements.txt
```


Run the code.
```bash
python main.py
```

## Usage

1. Get a list of all currencies with base EUR
```
/list
```
2. Convert currency.
```
 /exchange 10 USD to CAD
```
3. Get an image graph chart which shows the exchange rate graph/chart of the selected currency for the last 7 days.
```
 /history USD/CAD for 7 days
```
