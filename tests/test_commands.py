from commands import CommandExecutor


def test_build_add_user_cmd_contains_flags():
    cmd = CommandExecutor.build_add_user_cmd("my-list", "x@example.com")
    assert "-NoProfile" in cmd
    assert "-ExecutionPolicy Bypass" in cmd
    assert "AddUserToList.ps1" in cmd
    assert "my-list" in cmd
    assert "x@example.com" in cmd


def test_run_executes_echo():
    # Use a platform-agnostic echo
    result = CommandExecutor.run("echo hello_test")
    # echo may include newline; just check stdout contains the word
    assert result.returncode == 0
    assert "hello_test" in result.stdout
