from mcp_workflows.main import main


def test_main(capsys):
    """Test that main function prints 'Hello, World!'"""
    main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World!"
