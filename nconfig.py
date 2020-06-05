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


logfile_path = "nconfig.log"


def prompt(text, indent, type):
    prefix = ""
    color = ""
    if type == 0:
        prefix = "?"
        color = "magenta"
    elif type == 1:
        prefix = ">"
        color = "blue"
    return cl.style(indent * "  " + prefix + " ", bold=True, fg=color) + text


@cl.group()
def cli():
    """CLI for configuring linux."""
    # Clear logfile
    f = open(logfile_path, "w")
    f.write("")


@cli.command()
def auto_install():
    """Configure everything according to passed options"""

    global package_manager
    """ prompts """
    while True:
        packages_to_install = list()
        # Initial prompts
        restore_dotfiles = cl.confirm(prompt("Restore dotfiles?", 0, 0))
        restore_backup = cl.confirm(prompt("Restore backups?", 0, 0))

        # Backup prompts
        if restore_backup:
            backup_path = cl.prompt(prompt("Backup path", 1, 0),
                                    type=cl.Path(dir_okay=True, exists=True, readable=True, ))

        install_packages = cl.confirm(prompt("Install packages?", 0, 0))

        # Package specific prompts
        if install_packages:
            package_manager = \
                cl.prompt(prompt("Package manager", 1, 0),
                          type=cl.Choice(choices=packages.keys(), case_sensitive=False))
            package_manager = pacman if package_manager == "PACMAN" else deb

            # Prompt each package group
            groups = {}
            for group in package_manager:
                groups[group] = cl.confirm(prompt("Install {} packages?".format(group), 2, 0))
                if groups[group]:
                    for package in package_manager[group]:
                        if cl.confirm(prompt("Install {}?".format(package), 3, 0)):
                            packages_to_install.append(package)

        cl.echo()
        # User decides to do nothing
        if not restore_dotfiles and not restore_backup and not install_packages:
            cl.echo(prompt("Nothing selected. Starting over.", 0, 1))
            cl.echo()
            continue

        # Confirmation screen
        cl.echo(prompt("Confirm your input:", 0, 1))

        # Task list
        cl.echo(prompt("Task list:", 1, 1))
        if restore_dotfiles:
            cl.echo(prompt("Restore dotfiles", 2, 1))

        if restore_backup:
            cl.echo(prompt("Restore backup", 2, 1))

        if install_packages:
            cl.echo(prompt("Install packages", 2, 1))

        # Packages to install
        for package in packages_to_install:
            cl.echo(prompt(package, 3, 1))
        cl.echo()

        # Confirmation prompt
        if cl.confirm(prompt("Start installation?", 0, 0)):
            cl.echo()
            break
        else:
            cl.echo()
            cl.echo(prompt("Starting over.", 0, 1))
            cl.echo()

    """ install """
    cl.echo(prompt("Starting installation.", 0, 1))

    # Restore dotfiles
    if restore_dotfiles:
        cl.echo(prompt("Restoring dotfiles...", 1, 1))
        os.system("git clone --bare https://github.com/noahjutz/dotfiles $HOME/.cfg &>> {logfile_path}\n" +
                  "git --git-dir=$HOME/.cfg/ --work-tree=$HOME checkout -f\n" +
                  "git --git-dir=$HOME/.cfg/ --work-tree=$HOME config --local status.showUntrackedFiles no\n" +
                  "echo \".cfg\" >> .gitignore &>> {logfile_path}")

    # Restore backup
    if restore_backup:
        cl.echo(prompt("Restoring backup...", 1, 1))
        os.system("dconf load / &>> {logfile_path} < {backup_path}/gnome-settings\n" +
                  "tar xf {backup_path}/brave.tar.gz -C $HOME/.config/ &>> {logfile_path}")

    # Install packages
    if install_packages:
        if package_manager == pacman:
            # Update
            cl.echo(prompt("Updating packages...", 1, 1))
            os.system("yay -Syu --answerclean None --answerdiff None --ask no &>> {logfile_path}")
            # Install packages
            cl.echo(prompt("Installing packages...", 1, 1))
            for package in packages_to_install:
                cl.echo(prompt("Installing {}...".format(package), 2, 1))
                os.system("yay -S --answerclean None --answerdiff None --ask no {package} &>> {logfile_path}")
        elif package_manager == deb:
            # Update
            cl.echo(prompt("Updating packages...", 1, 1))
            # Install packages
            cl.echo(prompt("Installing packages...", 1, 1))

    # Done
    cl.echo(prompt("Installation complete.", 0, 1))


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
