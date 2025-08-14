from phase1_problem_solver import Phase1ProblemSolver

cfg = {
  "data_path": "test_data.csv",
  "schema_map": {
    "target": "target",
    "numeric": ["num_a","num_b","num_c","num_d","num_e","num_f"],
    "categorical": ["cat_a","cat_b"],
    "drop": ["row_id"],
    "datetime": ["event_time"]
  },
  "random_state": 42,
  "use_stratified_split": True,
  "load_fixed_split": False,
  "save_fixed_split": True,
  "reseed_on_imbalance": True,
  "strong_reg": True,
  "stacking_enabled": False,
  "calibration": "isotonic",
  "iso_max_n": 1500,
  "enable_xgb": True,
  "select_by_test": False,
  "categorical_handling": "drop",
  "xgb_params": {
    "max_depth": 3, "min_child_weight": 10, "subsample": 0.7,
    "colsample_bytree": 0.6, "reg_lambda": 2.5, "reg_alpha": 0.3,
    "learning_rate": 0.05, "n_estimators": 400
  }
}

print("[실데이터 연동 테스트] Phase1ProblemSolver 실행 (파일 생성 방식)")
Phase1ProblemSolver(cfg).run()
