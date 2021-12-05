# Crowd count prediction and dashboard

## Development
### Python venv
Make sure `virtualenv` is installed on your machine. Then do these following steps: 

- ```virtualenv venv -p python3.7```

- ```source venv/bin/activate```

- ```pip install -r requirements.txt```

### conda venv
- ```conda create --name <envname> python=3.7```
- ```conda activate <envname>```
- ```pip install -r requirements.txt```
- Optionally, if you run on Mac, run the following:
```
brew install libomp
conda install -c conda-forge py-xgboost
```

Go to src directory, run this from the shell/terminal:

- ```streamlit run app.py```

You should see this pop up.

![](img/first_look.png)