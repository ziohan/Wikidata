import os
import ast
import math
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from textwrap import wrap

# Getting all the qids from the list of triplets and normalizing them
def normalize_qid_list(qid_value):
    if isinstance(qid_value, list):
        values = qid_value
    elif isinstance(qid_value, str):
        qid_value = qid_value.strip()
        try:
            parsed = ast.literal_eval(qid_value)
            values = parsed if isinstance(parsed, list) else [qid_value]
        except:
            values = [x.strip() for x in qid_value.split(",") if x.strip()]
    else:
        values = []

    clean_qids = []
    for x in values:
        x = str(x).strip()
        if not x:
            continue
        if not x.startswith("Q"):
            x = "Q" + x
        clean_qids.append(x)
    return clean_qids

# Break the text into multiple lines for better display in the graph
def short_label(text, width=14):
    return "\n".join(wrap(str(text), width=width))

# Remove duplicates
def duplicates_order(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

# Uses predicate weight and object count to assign a score to each triple, then ranks them
PREFERRED_PREDICATES = {
    "instance of",
    "subclass of",
    "part of",
    "field of work",
    "topic's main category",
    "has part(s)",
    "has characteristic",
    "different from",
    "use",
    "described by source"
}

GENERIC_TERMS = {
    "entity", "object", "item", "concept", "thing", "document",
    "method", "record", "writing", "information", "type of document"
}

def compute_predicate_weight(pred_block):
    """Poids vertical d'un prédicat = max(1, nb objets)"""
    return max(1, len(pred_block["objects"]))

def compute_entity_weight(entity_block):
    """Poids vertical d'une entité = somme des poids de ses prédicats"""
    if not entity_block["predicates"]:
        return 1
    return sum(compute_predicate_weight(p) for p in entity_block["predicates"])

def assign_subtree_positions(pos, entity_block, side, entity_y, x_entity, x_pred, x_obj,
                             pred_gap=1.8, obj_gap=1.2):
    """
    Place une entité, ses prédicats et ses objets sur un côté.
    side = -1 pour gauche, +1 pour droite
    """
    entity_name = entity_block["entity"]
    pos[entity_name] = (side * x_entity, entity_y)

    preds = entity_block["predicates"]
    if not preds:
        return

    pred_weights = [compute_predicate_weight(p) for p in preds]
    total_weight = sum(pred_weights)

    current_top = entity_y + (total_weight - 1) * pred_gap / 2

    for pred_block, w in zip(preds, pred_weights):
        pred_node = pred_block["pred_node"]

        pred_center_y = current_top - (w - 1) * pred_gap / 2
        pos[pred_node] = (side * x_pred, pred_center_y)

        obj_nodes = pred_block["objects"]
        n_objs = len(obj_nodes)

        if n_objs == 0:
            current_top -= w * pred_gap
            continue

        if n_objs == 1:
            obj_ys = [pred_center_y]
        else:
            total_obj_height = (n_objs - 1) * obj_gap
            obj_top = pred_center_y + total_obj_height / 2
            obj_ys = [obj_top - k * obj_gap for k in range(n_objs)]

        for obj_node, oy in zip(obj_nodes, obj_ys):
            pos[obj_node] = (side * x_obj, oy)

        current_top -= w * pred_gap

def graph_design(UniqueList3, listtripletslabel, data, query_id):
    plt.rcParams["figure.figsize"] = (24, 16)
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.facecolor"] = "white"

    path_results = "./KG_papers_tree_layout/"
    os.makedirs(path_results, exist_ok=True)

    ListeEntity = UniqueList3
    ListeTripletLabel = listtripletslabel

    file = data.copy()
    file = file.dropna(subset=["Title", "QID"]).reset_index(drop=True)

    i = 0
    doc_id = f"Doc-{i}"
    title = file.loc[i, "Title"]
    doc_qids = normalize_qid_list(file.loc[i, "QID"])
    list_index = [idx for idx, qid in enumerate(ListeEntity) if qid in doc_qids]

    doc_entities = []

    for j in list_index:
        if j >= len(ListeTripletLabel):
            continue

        triplet_labels = ListeTripletLabel[j]
        if not triplet_labels:
            continue

        entity_label = triplet_labels[0][0].strip()
        if entity_label.lower() in GENERIC_TERMS:
            continue

        grouped_predicates = {}
        for t in triplet_labels:
            if len(t) < 3:
                continue

            subj, pred, obj = t[0].strip(), t[1].strip(), t[2].strip()

            if not obj or obj.lower() in GENERIC_TERMS:
                continue

            grouped_predicates.setdefault(pred, [])
            if obj not in grouped_predicates[pred]:
                grouped_predicates[pred].append(obj)

        if grouped_predicates:
            doc_entities.append({
                "entity": entity_label,
                "predicates": grouped_predicates
            })

    unique_entities = []
    seen_entities = set()
    for ent in doc_entities:
        if ent["entity"] not in seen_entities:
            seen_entities.add(ent["entity"])
            unique_entities.append(ent)

    doc_entities = unique_entities

    if not doc_entities:
        return None, None

    G = nx.DiGraph()
    G.add_node(doc_id, node_type="document", display_label=doc_id)

    structured_entities = []

    for entity_info in doc_entities:
        entity_name = entity_info["entity"]
        G.add_node(entity_name, node_type="entity", display_label=short_label(entity_name, 16))
        G.add_edge(doc_id, entity_name)

        predicates = list(entity_info["predicates"].items())
        predicates = sorted(
            predicates,
            key=lambda x: (x[0] not in PREFERRED_PREDICATES, -len(x[1]), x[0])
        )

        entity_block = {
            "entity": entity_name,
            "predicates": []
        }

        for pred, obj_list in predicates:
            pred_node = f"{entity_name}__{pred}"
            clean_objects = duplicates_order(obj_list)

            G.add_node(pred_node, node_type="predicate", display_label=short_label(pred, 14))
            G.add_edge(entity_name, pred_node)

            obj_nodes = []
            for obj in clean_objects:
                obj_node = f"{pred_node}__{obj}"
                G.add_node(obj_node, node_type="object", display_label=short_label(obj, 14))
                G.add_edge(pred_node, obj_node)
                obj_nodes.append(obj_node)

            entity_block["predicates"].append({
                "pred_node": pred_node,
                "objects": obj_nodes
            })

        structured_entities.append(entity_block)

    if G.number_of_edges() == 0:
        return None, None

    pos = {}
    pos[doc_id] = (0, 0)

    n = len(structured_entities)
    left_entities = structured_entities[: math.ceil(n / 2)]
    right_entities = structured_entities[math.ceil(n / 2):]

    left_weights = [compute_entity_weight(e) for e in left_entities]
    right_weights = [compute_entity_weight(e) for e in right_entities]

    left_total = sum(left_weights) if left_weights else 1
    right_total = sum(right_weights) if right_weights else 1

    x_entity = 3.0
    x_pred = 6.8
    x_obj = 10.6

    entity_gap_unit = 2.0

    current_top = (left_total - 1) * entity_gap_unit / 2
    for entity_block, w in zip(left_entities, left_weights):
        entity_center_y = current_top - (w - 1) * entity_gap_unit / 2
        assign_subtree_positions(
            pos, entity_block, side=-1,
            entity_y=entity_center_y,
            x_entity=x_entity, x_pred=x_pred, x_obj=x_obj,
            pred_gap=1.8, obj_gap=1.15
        )
        current_top -= w * entity_gap_unit

    current_top = (right_total - 1) * entity_gap_unit / 2
    for entity_block, w in zip(right_entities, right_weights):
        entity_center_y = current_top - (w - 1) * entity_gap_unit / 2
        assign_subtree_positions(
            pos, entity_block, side=+1,
            entity_y=entity_center_y,
            x_entity=x_entity, x_pred=x_pred, x_obj=x_obj,
            pred_gap=1.8, obj_gap=1.15
        )
        current_top -= w * entity_gap_unit

    node_colors = []
    node_sizes = []
    labels = {}

    for n_node, attrs in G.nodes(data=True):
        ntype = attrs["node_type"]
        labels[n_node] = attrs["display_label"]

        if ntype == "document":
            node_colors.append("#2E7D32")
            node_sizes.append(4200)
        elif ntype == "entity":
            node_colors.append("#F57C00")
            node_sizes.append(2600)
        elif ntype == "predicate":
            node_colors.append("#FFEB3B")
            node_sizes.append(1900)
        else:
            node_colors.append("#29B6F6")
            node_sizes.append(1700)

    ys = [p[1] for p in pos.values()]
    y_span = max(ys) - min(ys) if ys else 10
    fig_h = max(12, 0.9 * y_span + 6)
    fig_w = 20

    plt.figure(figsize=(fig_w, fig_h))
    ax = plt.gca()
    ax.set_facecolor("white")

    nx.draw_networkx_edges(
        G, pos,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=12,
        edge_color="black",
        width=1.8,
        alpha=0.95,
        connectionstyle="arc3,rad=0.0"
    )

    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=node_sizes,
        edgecolors="#444444",
        linewidths=1.0,
        node_shape="o"
    )

    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        font_size=7,
        font_weight="bold",
        font_family="DejaVu Sans"
    )

    plt.title(
        f"Knowledge Graph - {doc_id}",
        fontsize=16,
        fontweight="bold",
        pad=18
    )

    short_title = "\n".join(wrap(title, width=110))
    plt.figtext(0.5, 0.02, short_title, ha="center", fontsize=9)

    plt.axis("off")
    plt.subplots_adjust(left=0.04, right=0.96, top=0.90, bottom=0.08)

    save_png = os.path.join(path_results, f"{query_id}.png")
    save_pdf = os.path.join(path_results, f"{query_id}.pdf")

    plt.savefig(save_pdf, format="pdf", dpi=600, bbox_inches="tight", facecolor="white")
    plt.savefig(save_png, format="png", dpi=400, bbox_inches="tight", facecolor="white")

    plt.close()
    return str(save_png), str(save_pdf)