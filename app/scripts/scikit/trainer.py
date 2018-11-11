from sklearn.base import BaseEstimator, TransformerMixin


class FeedbackTransformer(BaseEstimator, TransformerMixin):

    def fit(self):
        pass

    def fit_transform(self, X, y=None, **fit_params):
        pass
