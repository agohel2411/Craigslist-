## This repo contains FastAPI file app.py

For this particular project we will be using Python VENV.

**To make a venv for the project, run:**

```bash
python3 -m venv <venv_name>
```

**To activate VENV, run:**

```bash
source <venv_name>/bin/activate ## for linux
<venv_name>\Scripts\activate ## for windows
```
### After activating VENV, first install all the requirements by:

```bash
pip3 install -r requirements.txt
```

### To create sqlite database from json, run:

```bash
python3 convert.py 
```
table.db database file will be added to main folder with sales table.

### To run app.py fastapi on localhost with port 10001, in your terminal run:

```bash
uvicorn app:app --port 10001 --reload
```

Now you can view all the results by,
1. On Swagger interface by just typing : http://127.0.0.1:10001/docs and can test API
2. By manually entering routes and passing parameters after http://127.0.0.1:10001

### File Structure

```bash
Craigslist/
│
├── data/
│   └── sale.json               # Raw data file
│
├── router/
│   ├── jsonrouter.py           # Handles routing for JSON-based APIs
│   └── sqlrouter.py            # Handles routing for SQL-based APIs
│
├── src/
│   ├── __init__.py             # Package initializer
│   ├── database.py             # Database connection and queries
│   ├── log.py                  # Logging setup
│   ├── model.py                # ORM models or data models
│   └── schema.py               # Pydantic schemas or DB schemas
│
├── app.py                      # Main FastAPI (or Flask) application
├── convert.py                  # Script to convert or process data
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation

```