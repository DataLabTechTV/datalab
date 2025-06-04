import click


@click.command()
def dlctl():
    click.echo("Hello")


if __name__ == "__main__":
    dlctl()
