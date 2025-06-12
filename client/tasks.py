from invoke import task


@task
def build(c):
    c.run("pyinstaller -F -w main.py")
