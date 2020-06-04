#!/usr/bin/env python
import click

pacman = {
    "essential": (
        "yay",
        "binutils",
        "make",
        "gcc",
        "pkg-config",
        "fakeroot",

        "python",
        "python-pip"
    ),
    "cli": (
        "fish",
        "htop",
        "gvim",
        "ranger"
    ),
    "social": (
        "discord",
        "telegram-desktop"
    ),
    "ide": (
        "android-studio",
        "pycharm-community-edition",
        "code"
    ),
    "tools": (
        "bitwarden",
        "torbrowser-launcher",
        "brave",
        "etcher",
        "virtualbox"
    )
}

deb = {
    # TODO
}

packages = {
    "PACMAN": pacman,
    "DEB": deb
}


@click.group()
def cli():
    """CLI for configuring linux."""
    pass


@cli.command()
def auto_install():
    """Configure everything according to passed options"""
    package_manager = click.prompt("TODO", type=click.Choice(choices=packages.keys(), case_sensitive=False))
    restore_backup = click.confirm("TODO", default=True)
    restore_dotfiles = click.confirm("TODO", default=True)


@cli.command()
def backup():
    """Back up app settings and push to a server"""
    click.echo("Backup")


@cli.command()
def restore():
    """Restore app settings"""
    click.echo("Restore")


if __name__ == '__main__':
    cli()
