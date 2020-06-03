#!/usr/bin/env python
import click

text = 'DEB if debian-based. PACMAN if arch-based. RPM if red-hat/fedora-based.'


@click.command()
@click.option('--pkg-manager', prompt='Package manager [DEB|PACMAN|RPM]',
              help=text)
def main(pkg_manager):
    """Simple program that greets"""
    click.echo(click.style('==> ', fg='green', bold=True) + " " + click.style('Hello World!', bold=True))


if __name__ == '__main__':
    main()
