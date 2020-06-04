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


def prompt_h1(prompt):
    return click.style("> ", bold=True) + click.style(prompt, fg="magenta")


def prompt_h2(prompt):
    return click.style("  > ", bold=True) + click.style(prompt, fg="blue")


def prompt_h3(prompt):
    return click.style("    > ", bold=True) + click.style(prompt, fg="green")


def prompt_h4(prompt):
    return click.style("      > ", bold=True) + prompt


@click.group()
def cli():
    """CLI for configuring linux."""
    pass


@cli.command()
def auto_install():
    """Configure everything according to passed options"""

    """ prompts """
    # Initial prompts
    restore_dotfiles = click.confirm(prompt_h1("Restore dotfiles?"))
    restore_backup = click.confirm(prompt_h1("Restore backups?"))
    install_packages = click.confirm(prompt_h1("Install packages?"))

    # Package specific prompts
    if install_packages:
        package_manager = \
            click.prompt(prompt_h2("Package manager"), type=click.Choice(choices=packages.keys(), case_sensitive=False))
        package_manager = pacman if package_manager == "PACMAN" else deb

        # Prompt each package group
        groups = {}
        packages_to_install = list()
        for group in package_manager:
            groups[group] = click.confirm(prompt_h3("Install {} packages?".format(group)))
            if groups[group]:
                for package in package_manager[group]:
                    if click.confirm(prompt_h4("Install {}?".format(package))):
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
