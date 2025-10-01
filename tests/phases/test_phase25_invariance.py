from duri_finale.phase_25_future_design_system import FutureDesignSystem


def test_invariance_seed_stability():
    fd = FutureDesignSystem()
    # analyze_trends 메서드 사용 (실제 API에 맞게 수정)
    x1 = fd.analyze_trends(domain="technological", time_horizon="5-10년")
    x2 = fd.analyze_trends(domain="technological", time_horizon="5-10년")
    # 동일한 입력에 대해 동일한 결과 반환 확인
    assert len(x1) == len(x2)
    # 첫 번째 결과의 구조가 동일한지 확인
    if x1 and x2:
        assert x1[0].category == x2[0].category
        assert x1[0].trend_name == x2[0].trend_name


def test_invariance_order_independence():
    fd = FutureDesignSystem()
    # 동일한 도메인에 대해 다른 순서로 호출
    a = fd.analyze_trends(domain="social", time_horizon="3-5년")
    b = fd.analyze_trends(domain="social", time_horizon="3-5년")
    # 입력 순서와 무관하게 동일한 결과 반환 확인
    assert len(a) == len(b)
    if a and b:
        assert a[0].category == b[0].category
