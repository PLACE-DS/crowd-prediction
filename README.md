# Crowd count prediction and dashboard

## Pipeline v2
![pipeline v2](https://user-images.githubusercontent.com/37158629/144886644-e670f144-0ff6-40b2-bfbb-dc2664b5bd00.png)

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
