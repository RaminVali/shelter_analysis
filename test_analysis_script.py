from pytest import raises
import pandas as pd

path = "test_data.csv"
def test_load_data_results():
    from analysis_script import load_data
    df = load_data(path)
    assert isinstance(df, pd.DataFrame), 'Dataframe object not found'

missing_cols_path = 'test_data_missing cols.csv'
def test_load_data_error():
    from analysis_script import load_data
    with raises(ValueError):
        load_data(missing_cols_path)


def test_preprocess():
    df = pd.read_csv('preped_df_test.csv')
    from analysis_script import preprocess
    with raises(ValueError):
        preprocess(df)
