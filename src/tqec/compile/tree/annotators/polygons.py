from typing_extensions import override

from tqec.compile.blocks.layers.atomic.layout import LayoutLayer
from tqec.compile.tree.annotations import Polygon
from tqec.compile.tree.node import LayerNode, NodeWalker
from tqec.utils.position import Shift2D


class AnnotatePolygonOnLayerNode(NodeWalker):
    def __init__(self, k: int):
        self._k = k

    @override
    def visit_node(self, node: LayerNode) -> None:
        if not node.is_leaf:
            return
        assert isinstance(node._layer, LayoutLayer)
        node.get_annotations(self._k).polygons = generate_polygons_for_layout_layer(
            node._layer, self._k
        )


def generate_polygons_for_layout_layer(layer: LayoutLayer, k: int) -> list[Polygon]:
    template, plaquettes = layer.to_template_and_plaquettes()

    _indices = list(range(1, template.expected_plaquettes_number + 1))
    template_plaquettes = template.instantiate(k, _indices)
    increments = template.get_increments()

    polygons: list[Polygon] = []

    for row_index, line in enumerate(template_plaquettes):
        for column_index, plaquette_index in enumerate(line):
            if plaquette_index != 0:
                # Computing the offset that should be applied to each qubits.
                plaquette = plaquettes[plaquette_index]
                debug_info = plaquette.debug_information
                # No rpng information is available for this plaquette.
                if debug_info is None or debug_info.rpng is None:
                    basis = None
                else:
                    bases = {
                        rpng.p for rpng in debug_info.rpng.corners if rpng.p is not None
                    }
                    # Only construct polygons for plaquettes with a single basis.
                    if len(bases) != 1:
                        continue
                    basis = bases.pop()

                qubit_offset = Shift2D(
                    plaquette.origin.x + column_index * increments.x,
                    plaquette.origin.y + row_index * increments.y,
                )
                qubits = frozenset(
                    q + qubit_offset for q in plaquette.qubits.data_qubits
                )
                polygons.append(Polygon(basis, qubits))

    # Shift the qubits of the returned scheduled circuit
    mincube, _ = layer.bounds
    eshape = layer.element_shape.to_shape_2d(k)
    # See: https://github.com/tqec/tqec/issues/525
    # This is a temporary fix to the above issue, we may need a utility function
    # to calculate shift to avoid similar issues in the future.
    shift = Shift2D(mincube.x * (eshape.x - 1), mincube.y * (eshape.y - 1))
    shifted_polygons = [
        Polygon(p.basis, frozenset(q + shift for q in p.qubits)) for p in polygons
    ]

    return shifted_polygons
