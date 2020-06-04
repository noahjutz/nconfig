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

    """ prompts """
    # Initial prompts
    restore_dotfiles = click.confirm(click.style("> Restore dotfiles?", fg="magenta"))
    restore_backup = click.confirm(click.style("> Restore backup?", fg="magenta"))
    install_packages = click.confirm(click.style("> Install packages?", fg="magenta"))

    # Package specific prompts
    if install_packages:
        package_manager = \
            click.prompt("  > Package manager", type=click.Choice(choices=packages.keys(), case_sensitive=False))
        package_manager = pacman if package_manager == "PACMAN" else deb

        # Prompt each package group
        groups = {}
        packages_to_install = list()
        for group in package_manager:
            groups[group] = click.confirm("    > Install {} packages?".format(click.style(group, fg="blue")))
            if groups[group]:
                for package in package_manager[group]:
                    if click.confirm("      > Install {}?".format(click.style(package, fg="green"))):
                        packages_to_install.append(package)
        click.echo()
        click.secho("Packages to install:", fg="magenta")
        for package in packages_to_install:
            click.echo("  - {}".format(package))

    """ Install """


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
