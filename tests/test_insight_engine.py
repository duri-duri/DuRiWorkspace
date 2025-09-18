import pytest
from insight import score_candidate, rank

def test_score_ranges():
    br = score_candidate("rehab drill", "new balance drill with metronome pacing")
    assert 0.0 <= br["novelty"] <= 1.0
    assert 0.0 <= br["coherence"] <= 1.0
    assert 0.0 <= br["brevity"] <= 1.0
    assert 0.0 <= br["S"] <= 1.0

def test_repetition_penalty():
    txt = "a b c " * 50
    br = score_candidate("", txt)
    assert br["novelty"] < 0.6

def test_length_prior():
    short = "x y z"
    long = "word " * 400
    b_short = score_candidate("", short)["brevity"]
    b_long  = score_candidate("", long)["brevity"]
    mid     = score_candidate("", "word " * 120)["brevity"]
    assert mid > b_short and mid > b_long

def test_rank_topk():
    r = rank("balance", ["foo", "bar", "baz"], k=2)
    assert len(r) == 2
    assert r[0][1] >= r[1][1]

def test_empty_candidates():
    assert rank("x", []) == []
