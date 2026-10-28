"""Train the LightGBM RQI model against expert-rated segments."""
import lightgbm as lgb
import pandas as pd

df = pd.read_parquet("data/rated_segments.parquet")
X = df[["area_D00", "area_D10", "area_D20", "area_D40", "pothole_weighted_count", "mean_confidence"]]
model = lgb.train({"objective": "regression", "learning_rate": 0.05, "num_leaves": 31},
                  lgb.Dataset(X, df["expert_rqi"]), num_boost_round=400)
model.save_model("weights/rqi_lgbm.txt")
