"""Aggregate from all files in directory to build a graph."""

import json
from datetime import datetime, timezone
from logging import getLogger
from pathlib import Path

import click

from sphinx_linklog.models import LinkModel, LinkModelAdapter

DIRECTORY = Path(__file__).parent.parent / "example-output"
OUTPUT_DIRECTORY = Path(__file__).parent.parent / "output-final"

ALL_LINKS: dict[str, list[LinkModel]] = {}

logger = getLogger(__name__)


@click.command()
@click.option(
    "--input-dir",
    default=DIRECTORY,
    help="Directory containing the input files.",
    type=click.Path(exists=True),
)
@click.option(
    "--output-dir",
    default=OUTPUT_DIRECTORY,
    help="Directory containing the output file.",
    type=click.Path(exists=True),
)
def aggregate(input_dir: Path, output_dir: Path) -> None:
    """Aggregate all edges into one."""
    for file in input_dir.iterdir():
        data = file.read_text()
        formatted_links = LinkModelAdapter.validate_json(data)
        for link in formatted_links:
            if not ALL_LINKS.get(link.project):
                ALL_LINKS[link.project] = []
            ALL_LINKS[link.project].append(link)

    logger.info(f"{ALL_LINKS=}")

    output_edges_file = output_dir / f"graph-edges-{datetime.now(tz=timezone.utc)}.json"
    output_nodes_file = output_dir / f"graph-nodes-{datetime.now(tz=timezone.utc)}.json"
    _ = output_edges_file.write_text(
        json.dumps(
            [
                link.model_dump(mode="json")
                for link_list in ALL_LINKS.values()
                for link in link_list
            ],
            newline="\n",
        ),
    )
    _ = output_nodes_file.write_text(json.dumps(list(ALL_LINKS), newline="\n"))
