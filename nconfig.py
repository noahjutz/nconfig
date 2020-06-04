#!/usr/bin/env python
import os

import click as cl

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
    return cl.style("? ", bold=True, fg="magenta") + prompt


def prompt_h2(prompt):
    return cl.style("  ? ", bold=True, fg="magenta") + prompt


def prompt_h3(prompt):
    return cl.style("    ? ", bold=True, fg="magenta") + prompt


def prompt_h4(prompt):
    return cl.style("      ? ", bold=True, fg="magenta") + prompt


def info_h1(info):
    return cl.style("> ", bold=True, fg="blue") + info


def info_h2(info):
    return cl.style("  > ", bold=True, fg="blue") + info


def info_h3(info):
    return cl.style("    > ", bold=True, fg="blue") + info


@cl.group()
def cli():
    """CLI for configuring linux."""
    pass


@cli.command()
def auto_install():
    """Configure everything according to passed options"""

    global package_manager
    """ prompts """
    packages_to_install = list()
    while True:
        # Initial prompts
        restore_dotfiles = cl.confirm(prompt_h1("Restore dotfiles?"))
        restore_backup = cl.confirm(prompt_h1("Restore backups?"))
        install_packages = cl.confirm(prompt_h1("Install packages?"))

        # Package specific prompts
        if install_packages:
            package_manager = \
                cl.prompt(prompt_h2("Package manager"), type=cl.Choice(choices=packages.keys(), case_sensitive=False))
            package_manager = pacman if package_manager == "PACMAN" else deb

            # Prompt each package group
            groups = {}
            for group in package_manager:
                groups[group] = cl.confirm(prompt_h3("Install {} packages?".format(group)))
                if groups[group]:
                    for package in package_manager[group]:
                        if cl.confirm(prompt_h4("Install {}?".format(package))):
                            packages_to_install.append(package)

        cl.echo()
        # User decides to do nothing
        if not restore_dotfiles and not restore_backup and not install_packages:
            cl.echo(info_h1("Nothing selected. Starting over."))
            cl.echo()
            continue

        # Confirmation screen
        cl.echo(info_h1("Confirm your input:"))

        # Task list
        cl.echo(info_h2("Task list:"))
        if restore_dotfiles:
            cl.echo(info_h3("Restore dotfiles"))

        if restore_backup:
            cl.echo(info_h3("Restore backup"))

        if install_packages:
            cl.echo(info_h3("Install packages"))

        # Packages to install
        cl.echo(info_h2("Packages to install:"))
        if not packages_to_install:
            cl.echo(info_h3("None"))
        else:
            for package in packages_to_install:
                cl.echo(info_h3(package))
        cl.echo()

        # Confirmation prompt
        if cl.confirm(prompt_h1("Start installation?")):
            cl.echo()
            break
        else:
            cl.echo()
            cl.echo(info_h1("Starting over."))
            cl.echo()

    """ install """
    cl.echo(info_h1("Starting installation."))
    # Install packages
    if install_packages:
        if package_manager == pacman:
            # Update
            cl.echo(info_h2("Updating packages..."))
            os.system("yay -Syu --answerclean None --answerdiff None --ask no")
            # Install packages
            cl.echo(info_h2("Installing packages..."))
            for package in packages_to_install:
                cl.echo(info_h3("Installing {}...".format(package)))
                os.system("yay -S --answerclean None --answerdiff None --ask no {} &> /dev/null".format(package))
        elif package_manager == deb:
            # Update
            cl.echo(info_h2("Updating packages..."))
            # Install packages
            cl.echo(info_h2("Installing packages..."))

    # Done
    cl.echo(info_h1("Installation complete."))


@cli.command()
def backup():
    """Back up app settings and push to a server"""
    cl.echo("Backup")


@cli.command()
def restore():
    """Restore app settings"""
    cl.echo("Restore")


if __name__ == '__main__':
    cli()
