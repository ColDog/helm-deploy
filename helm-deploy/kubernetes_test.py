import kubernetes


def test_helm():
    out = kubernetes.render_chart("testdata/test-0.1.0.tgz", "test", "default")
    assert out is not None
