import pandas as pd

def relative_risk_reduction(df, col='pm1_0_mass_conc'):
    """
    Takes the first five readings and the last five readings, averages each
    one. Then subtracts.  Assumes that the first five readings correspond to a
    state without the intervention, and the last five readings correspond to a
    state *with* the intervention.

    Returns: float
        Percent Reduction
    """
    col_data = df[col].astype('float')
    return (col_data.iloc[0:5].mean() - col_data.iloc[-5:].mean()) / col_data.iloc[0:5].mean() * 100

def adjust_timestamps_to_match_local_timezone(columns, df, delta='4 hours'):
    """
    Convert UTC to Eastern Time Zone

    TODO: this assumes the measurer is in Eastern Time Zone. Could be brittle
    if other people are using it
    """
    for x in columns:
        df.loc[:, x] = df[x] - pd.to_timedelta(delta)

def compute_relative_risk_reduction_per_row(row):
    """
    Meant to 'apply'-d on the dataframe of metadata.

    Parameters:
        row: pd.Series
            Has 'filepath', 'datetime', 'start_time',  'end_time'

    Returns: float
    """
    df = pd.read_csv(row['filepath'], parse_dates=['datetime'], index_col='datetime')
    row_data = df[(df.index > row['start_time']) & (df.index < row['end_time'])]
    return relative_risk_reduction(row_data)

def compute_fit_factor(relative_reduction_percent):
    """
    Converts the relative reduction percentage into the fit factor.

    E.g. If relative_reduction_percent = 90, this should correspond to 1 / 10
    times the original amount. 10 is the fit factor here.

    Parameters:
        relative_reduction_percent: float

    Returns: float
    """
    return 100 / ((100 - relative_reduction_percent))

def compute_overall_fit_factor(
    df,
    groupby,
    reduction_col='relative_reduction_pm1_0_mass_conc',
):
    """
    Parameters:
        df: pd.DataFrame
            Has a 'fit_factor' column

        reduction_col: str
            The column that represents relative reduction of particulate matter.

        groupby: list[str]
            What will be used to group the results by.

    Returns: pd.DataFrame
        With 'overall fit factor' as the column of interest, along with
        the groupby as the indices
    """
    df['fit_factor'] = df[reduction_col].apply(compute_fit_factor)
    df['1/ff'] = 1 / df['fit_factor']
    agg = df.groupby(groupby).sum()[['1/ff']].rename(columns={'1/ff': 'sum 1/ff'})
    agg_merge = agg.merge(
        df.groupby(groupby).count()[['1/ff']].rename(columns={'1/ff': 'count'}),
        left_index=True,
        right_index=True
    )
    agg_merge['overall fit factor'] = agg_merge['count'] / agg_merge['sum 1/ff']
    return agg_merge

def compute_cadr(
    df,
    number_of_readings_per_grouping,
    single_pass_filtration_efficiency,
    column_names,
    groupby_cols,
    filter_area_sq_meters,
):

    """
    Parameters:
        df: pd.DataFrame
            Contains anemometer readings.
        number_of_readings_per_grouping: int
            Number of readings for each grouping of groupby_cols.
        groupby_cols: list[str]
            The list of names of columns that will be used for grouping by.

        column_names: list[str]
            The columns that have the speed readings from the anemometer.
            Readings are assumed to be in meters per second (m/s).

        single_pass_filtration_efficiency: float
            float between 0 and 1

        filter_area_sq_meters: float
            The filter area in square meters


    Returns: float
        In cubic feet per minute (CFM).
    """
    speed_estimates = readings.groupby(groupby_cols).sum()[column_names].sum(axis=1) / number_of_readings_per_grouping


    cubic_meters_per_second = speed_estimates * filter_area_sq_meters

    seconds_per_minute = 60
    cubic_feet_per_cubic_meter = 35.3147
    cubic_feet_per_minute = cubic_meters_per_second \
            * seconds_per_minute \
            * cubic_feet_per_cubic_meter \
            * single_pass_filtration_efficiency # cubic feet per minute

    return cubic_feet_per_minute
