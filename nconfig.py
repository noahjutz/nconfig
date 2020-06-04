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
    # Initial prompts
    restore_dotfiles = click.confirm("Restore dotfiles?", default=True)
    restore_backup = click.confirm("Restore backup?", default=True)
    install_packages = click.confirm("Install packages?", default=True)

    # Package specific prompts
    if install_packages:
        package_manager = \
            click.prompt("Package manager", type=click.Choice(choices=packages.keys(), case_sensitive=False))
        package_manager = pacman if package_manager == "PACMAN" else deb

        # Prompt each package group
        for group in package_manager:
            click.echo(group)


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
