# Dataset acquisition

Download the **Retailrocket recommender system dataset** from https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset . Use Kaggle's Download button (login may be required) or the Kaggle CLI:

```bash
pip install kaggle
kaggle datasets download -d retailrocket/ecommerce-dataset -p data/raw --unzip
```

Put `events.csv`, `item_properties_part1.csv`, `item_properties_part2.csv`, and `category_tree.csv` inside `data/raw/` (not a nested directory). Do not commit raw or derived row-level visitor records. Public origin does not imply personal-use behavioral data should be published at row level. Verify source licensing/terms on Kaggle before redistributing anything. Dataset is third-party behavioral observations, not an experiment.
