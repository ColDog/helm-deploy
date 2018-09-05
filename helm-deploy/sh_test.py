import sh


def test_sh():
    sh.sh("ls", "-la")


def test_sh_quiet():
    sh.sh("ls", "-la", quiet=True)


def test_sh_capture():
    out = sh.sh("echo", "hi", capture=True)
    assert "hi\n" == out.decode()


def test_sh_write():
    out = sh.sh("base64", write="hello\n".encode(), capture=True)
    assert "aGVsbG8K\n" == out.decode()
