def sensitivity(df, actual_col, prediction_col):
    """
    Out of those that *do* fit, how many are labeled by the model as such?

    P(model is + | actual is +) = P(model is + AND actual is +) / P(actual is +)
        = (# model is + and actual is +) / (actual is +)
    """
    return ((df[actual_col]) & (df[prediction_col])).sum() / df[actual_col].sum()

def specificity(df, actual_col, prediction_col):
    """
    Out of those that *do not* fit, how many are labeled by the model as such?

    P(model is - | actual is -) = P(model is - AND actual is -) / P(actual is -)
        = (# model is - and actual is -) / (actual is -)
    """

    return ((~df[actual_col]) & (~df[prediction_col])).sum() / (~df[actual_col]).sum()
