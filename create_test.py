import os

os.makedirs('test_repo', exist_ok=True)

with open('test_repo/README.md', 'w') as f:
    f.write('# Test Project\n\nA sample project for testing MCP Builder.\n')

with open('test_repo/main.py', 'w') as f:
    f.write('import typer\n\napp = typer.Typer()\n\n@app.command()\ndef hello():\n    print("Hello World")\n\nif __name__ == "__main__":\n    app()\n')

with open('test_repo/requirements.txt', 'w') as f:
    f.write('typer\npydantic\n')

print("Test repo created")