# stockspider

A Python web crawler for stock prices and financial reports of Taiwan Stock Exchange (TWSE)

## Requirements  
- Python 3.6 or above  
- requests  
- pandas

You can install the dependencies via the following commands:  
```shell
pip install -r requirements.txt
```

## Usage
Download this repository.  
```
git clone https://github.com/tings0802/stockspider.git
```

Open a new Python script under the `stockspider` directory, and import `stockspider` module.  
```python
import stockspider
```
Or manually append the `stockspider` directory to `sys.path` first so that you can create new file outside the directory.  
```python
import sys

if dir_to_stockspider not in sys.path:
    sys.path.append(dir_to_stockspider)

import stockspider
```

Module `stockspider` provides some useful functions to crawl data from TWSE. Here is the prototypes.
```python
getDailyPrice(date: str = 'yesterday') -> pd.DataFrame
```
> parameters  
> `date`: `str` {`'yyyymmdd'`, `'today'`, `'yesterday'`}, default `'yesterday'`  
> 
> returns  
>`pandas.DataFrame`  

```python
getMonthlyReport(year: int, month: int) -> pd.DataFrame
```
> parameters  
> `year`: `yyyy`, **required**  
> `month`: {`1` ~ `12`}, **required**  
> 
> returns  
> `pandas.DataFrame`  

```python
saveData(data: pd.DataFrame, filename: str, overwrite: bool = False) -> bool
```
> parameters  
> `data`: `pandas.DataFrame`, **required**  
> `filename`: `str`, **required**  
> `overwrite`: {`True` or `False`} overwrite if true and the filename has existed , default `False`  
> 
> returns  
> `bool`: wheather the file is successfully saved    

## Contributing  
Open Issue, send PR or start a discussion.  

## License  
`stockspider` is under the [MIT License](https://github.com/tings0802/stockspider/blob/main/LICENSE).  