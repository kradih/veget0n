import logging

import click

from .linkedin import LinkedIn


logging.basicConfig(level=logging.INFO)


@click.command()
@click.option('--username', prompt='LinkedIn username',)
@click.option('--password', prompt='LinkedIn password', hide_input=True)
@click.option('--search-url', prompt='Linkedin company URL')
@click.option('--sleep-time', prompt='Time to sleep between page loads', default=5)
@click.option('--timeout', prompt='Timeout looking for web elements', default=10)
def main(username, password, search_url, sleep_time, timeout):
    with LinkedIn(username, password, sleep_time=sleep_time, timeout=timeout) as li:
        profiles = li.search(search_url)
        logging.info(f"Found {len(profiles)} profiles")
        for i, profile in enumerate(profiles):
            logging.info(f"[{i}] {li.get_profile(profile)}")


if __name__ == '__main__':
    main()
