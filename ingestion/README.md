# gathering the raw data

Run these commands from the root folder to gather the raw data.

You probably wont need to pass any parameters to the functions as they run from gva data start (2020-08-31) to today by default.<br>
However, since this is a pretty long period you could pass<br>`--start_date 2021-11-01 --end_date 2021-12-01`<br>to save some time.

Data will be placed in `/data/raw/`

---

**KNMI**<br>
`python ingestion/knmi_ingestion.py (--help)`

**COVID Stringency**<br>
`python ingestion/cov_ingestion.py (--help)`
