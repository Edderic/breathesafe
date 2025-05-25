import pandas as pd
import pickle

def recommend(
    predictors_dict,
    model_filename='python/mask_recommender/models/fit_predictor.pkl',
    mask_dummies_and_predictors_filename='python/mask_recommender/models/mask_dummies_and_predictors.pkl'
):
    with open(model_filename, 'rb') as file:
        loaded_model = pickle.load(file)

    with open(mask_dummies_and_predictors_filename, 'rb') as file:
        mask_dummies_and_predictors = pickle.load(file)

    user_predictor = pd.DataFrame([predictors_dict])
    for_prediction = user_predictor.merge(
        mask_dummies_and_predictors,
        how='cross'
    )

    integer_columns = [c for c in mask_dummies_and_predictors.columns if type(c) == int]
    integer_columns

    mask_id = mask_dummies_and_predictors[integer_columns].idxmax(axis=1).reset_index()[0]

    for_prediction.columns = for_prediction.columns.astype(str)
    predictions = loaded_model.predict_proba(for_prediction)

    for_prediction['proba_fit'] = predictions[:,1]
    for_prediction['mask_id'] = mask_id

    return for_prediction.sort_values(
        by='proba_fit',
        ascending=False
    )[['mask_id', 'proba_fit']]


def dummify_mask_ids(with_mask_dummies):
    mask_ids = sorted(with_mask_dummies['mask_id'].astype(int).unique())
    each_masks = pd.get_dummies(
        pd.Series(
            mask_ids
        )
    )
    each_masks['mask_id'] = mask_ids

    return each_masks

if __name__ == '__main__':
    predictors_dict = {
        'bitragion_subnasale_arc': 230,
        'face_width': 137,
        'nose_protrusion': 27,
        'facial_hair_beard_length_mm': 0
    }

    recommendations = recommend(predictors_dict)

    print("Recommendations:")
    print(recommendations)
