# app/components/graph_visualizer.py

import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from typing import Dict, List

class GraphVisualizer:
    """Visualise le graphe de connaissances."""
    
    def __init__(self, height: str = "600px"):
        self.height = height
    
    def visualize_subgraph(self, nodes: List[Dict], relationships: List[Dict]):
        """Visualise un sous-graphe."""
        
        # Créer le réseau
        net = Network(height=self.height, width="100%", bgcolor="#222222", font_color="white")
        
        # Configurer la physique
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "barnesHut": {
                    "gravitationalConstant": -8000,
                    "springLength": 250,
                    "springConstant": 0.001
                },
                "minVelocity": 0.75
            }
        }
        """)
        
        # Ajouter les nœuds
        for node in nodes:
            node_id = node.get('name', str(id(node)))
            node_type = node.get('type', 'unknown')
            
            # Couleur selon le type
            color = self._get_color_for_type(node_type)
            
            net.add_node(
                node_id,
                label=node_id,
                color=color,
                title=f"Type: {node_type}"
            )
        
        # Ajouter les relations
        for rel in relationships:
            source = rel.get('subject', rel.get('start'))
            target = rel.get('object', rel.get('end'))
            rel_type = rel.get('type', rel.get('predicate', 'relates_to'))
            
            if source and target:
                net.add_edge(source, target, label=rel_type)
        
        # Générer le HTML
        html = net.generate_html()
        
        # Afficher dans Streamlit
        components.html(html, height=int(self.height.replace("px", "")))
    
    def _get_color_for_type(self, entity_type: str) -> str:
        """Retourne une couleur selon le type d'entité."""
        colors = {
            'PERSON': '#FF6B6B',
            'ORG': '#4ECDC4',
            'GPE': '#45B7D1',
            'DATE': '#FFA07A',
            'EVENT': '#98D8C8',
            'PRODUCT': '#F7DC6F',
            'unknown': '#95A5A6'
        }
        return colors.get(entity_type, colors['unknown'])
