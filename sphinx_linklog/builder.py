# This file is part of sphinx-ext-template.
#
# Copyright 2025 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3, as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY
# QUALITY, or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""Contains the extension's core builders."""

import json
from typing import cast

from docutils import nodes
from pydantic import TypeAdapter
from sphinx.builders.linkcheck import (
    CheckExternalLinksBuilder,
    Hyperlink,
    HyperlinkCollector,
)
from sphinx.util.nodes import get_node_line
from typing_extensions import override

from sphinx_linklog.models import LinkModel


class HyperlinkEdgeBuilder(CheckExternalLinksBuilder):
    """Builder that will build the list of edges."""

    name = "linklog"

    def init(self) -> None:
        """Start building."""
        self.broken_hyperlinks = 0
        self.timed_out_hyperlinks = 0
        self.hyperlinks: list[tuple[Hyperlink, str, str]] = []

    def finish(self) -> None:
        """Finish building and write output."""
        output_edges = self.outdir / "output_edges.json"

        adapter = TypeAdapter(list[LinkModel])
        hyperlinks_model = adapter.validate_python(
            [
                {
                    "target": hyperlink[0].uri,
                    "source": hyperlink[0].docname,
                    "context": hyperlink[1],
                    "project": hyperlink[2],
                }
                for hyperlink in self.hyperlinks
            ]
        )
        with (
            output_edges.open(mode="w") as outfile,
        ):
            json.dump(
                [link.model_dump(mode="json") for link in hyperlinks_model], outfile
            )


class HyperlinkEdgeCollector(HyperlinkCollector):
    """Link collector."""

    builders = ("linklog",)

    @override
    def _add_uri(self, uri: str, node: nodes.Element) -> None:
        """Registers a node's URI into a builder's collection of hyperlinks.

        Provides the ability to register a URI value determined from a node
        into the linkcheck's builder. URI's processed through this call can
        be manipulated through a ``linkcheck-process-uri`` event before the
        builder attempts to validate.

        :param uri: URI to add
        :param node: A node class where the URI was found
        """
        builder = cast("HyperlinkEdgeBuilder", self.app.builder)
        hyperlinks = builder.hyperlinks
        docname = self.env.docname

        try:
            lineno = get_node_line(node)
        except ValueError:
            lineno = -1

        try:
            source = node.parent.parent.astext()
        except Exception:  # noqa: BLE001
            source = node.astext()

        if node.get("internal"):
            if uri.lstrip("#") not in self.app.env.domaindata["std"]["labels"]:
                return
            target_doc, _, _ = self.app.env.domaindata["std"]["labels"][uri.lstrip("#")]
            uri = f"{self.config.website_domain}{target_doc}{uri}"

        hyperlinks.append(
            (
                Hyperlink(
                    uri,
                    f"{self.config.website_domain}{docname}",
                    self.env.doc2path(docname),
                    lineno,
                ),
                source,
                self.config.project.lower().replace(" ", "-"),
            )
        )
