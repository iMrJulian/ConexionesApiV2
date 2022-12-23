import pandas as pd
import networkx
import matplotlib.pyplot as plt
import numpy as np

from bokeh.io import output_notebook, show, save, curdoc, output_file
from bokeh.models import Button, Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges, LabelSet, TapTool, Div, CustomJS
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.plotting import from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
from networkx.algorithms import community
from bokeh.events import Tap

#Evento a la hora de hacer click en un nodo
def display_event(div, source, attributes=[]):
    """
    Function to build a suitable CustomJS to display the current event
    in the div model.
    """
    style = 'float: left; clear: left; font-size: 13px'
    return CustomJS(args=dict(div=div, source=source), code="""


        if (source.selected.indices.length) {
            const indice = source.selected.indices[0]
            const name = source.data["index"][indice]
            const depreciada = source.data["depreciada"][indice]
            const port = source.data["port"][indice]
            const services = source.data["service"][indice]
            const testLink = source.data["testLink"][indice]
            const productionLink = source.data["productionLink"][indice]
            const authenticationLink = source.data["authenticationLink"][indice]
            const repositoryLink = source.data["repositoryLink"][indice]
            const excelLink = source.data["excelLink"][indice]

            const apiDiv = "<h2>" + name + "</h2>";
            const depreciadaDiv = "<p> <b> Depreciada: </b>" + depreciada + "</p>";
            const portDiv = "<p> <b> Puerto: </b>" + port + "</p>";
            const servicesDiv = "<p> <b> Servicios: </b>" + services + "</p>";
            const testDiv = "<p> <b> Pruebas: </b>" + testLink + "</p>";
            const productionDiv = "<p> <b> Producción: </b>" + productionLink + "</p>";
            const authenticationDiv = "<p> <b> WSO2: </b>" + authenticationLink + "</p>";
            const repositoryDiv = "<p> <b> Repositorio: </b>" + repositoryLink + "</p>";
            const excelDiv = "<p> <b> Excel: </b>" + excelLink + "</p>";

            const lineDiv = apiDiv + depreciadaDiv + portDiv + servicesDiv + testDiv + productionDiv + authenticationDiv + repositoryDiv + excelDiv;
            //const portFrame = "<span> Port:" + services + "</span>\\n";

            //const lineFrame = "<div>" + apiFrame  + portFrame "</div>";

            console.log(port)

            const {to_string} = Bokeh.require("core/util/pretty")
            const attrs = %s;
            const args = [];
            console.log(attrs)
            for (let i = 0; i<attrs.length; i++ ) {
                const val = to_string(cb_obj[attrs[i]], {precision: 2})
                args.push(attrs[i] + '=' + val)  
            }
            const line = "<span style=%r><b>" + cb_obj.event_name + "</b>(" + args.join(", ") + ")</span>\\n";
            const text = lineDiv;
            const lines = text.split("\\n")
            if (lines.length > 35)
                lines.shift();
            div.text = lines.join("\\n");
        }
    """ % (attributes, style))

#Se leen los datos
apiConnections = pd.read_csv('./data/Conexiones2.csv')
nodes = pd.read_csv('./data/Nodos2.csv')

#Se separan los datos
service = nodes.ServicesList
for i in range(0,len(service)):
    service.loc[i] = service.loc[i].replace(";","\n\t")
    # service.loc[i] = service.loc[i].split(";")

service.index = nodes.Name

depreciada = nodes.Depreciada
depreciada.index = nodes.Name

port = nodes.Port
port.index = nodes.Name

testLink = nodes.Test
testLink.index = nodes.Name

productionLink = nodes.Production
productionLink.index = nodes.Name

authenticationLink = nodes.Authentication
authenticationLink.index = nodes.Name

repositoryLink = nodes.Repository
repositoryLink.index = nodes.Name

excelLink = nodes.ConnectionMap
excelLink.index = nodes.Name

# Se formatea todos los dataframes a diccionarios para su posterior insersión 
services = pd.Series(service, index = nodes.Name).to_dict()
depreciada = pd.Series(depreciada, index = nodes.Name).to_dict()
port = pd.Series(port, index = nodes.Name).to_dict()
testLink = pd.Series(testLink, index=nodes.Name).to_dict()
productionLink = pd.Series(productionLink, index=nodes.Name).to_dict()
authenticationLink = pd.Series(authenticationLink, index=nodes.Name).to_dict()
repositoryLink = pd.Series(repositoryLink, index=nodes.Name).to_dict()
excelLink = pd.Series(excelLink, index=nodes.Name).to_dict()

#Se crea el grafo
G = networkx.from_pandas_edgelist(apiConnections, 'Source', 'Target', 'Weight')

#Se insertan los datos como atributos
degrees = dict(networkx.degree(G))
networkx.set_node_attributes(G, name='depreciada',          values =depreciada)
networkx.set_node_attributes(G, name='degree',              values=degrees)
networkx.set_node_attributes(G, name='port',                values = port)
networkx.set_node_attributes(G, name='service',             values = service)
networkx.set_node_attributes(G, name='testLink',            values = testLink)
networkx.set_node_attributes(G, name='productionLink',      values = productionLink)
networkx.set_node_attributes(G, name='authenticationLink',  values = authenticationLink)
networkx.set_node_attributes(G, name='repositoryLink',      values = repositoryLink)
networkx.set_node_attributes(G, name='excelLink',           values = excelLink)

#Paleta de colores para el nodo seleccionado — Blues8, Reds8, Purples8, Oranges8, Viridis8
node_highlight_color = 'blue'
edge_highlight_color = 'red'

#Atributo por nodo para el color y el tamaño
size_by_this_attribute = 'adjusted_node_size'
color_by_this_attribute = 'modularity_color'

#paleta de colores para los nodos
color_palette = Blues8

#tamaño de los nodos
number_to_adjust_by = 10
adjusted_node_size = dict([(node, (degree*3)+number_to_adjust_by) for node, degree in networkx.degree(G)])
networkx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

#Titulo
title = 'Mapa'

#Caracteristas o atributos que apareceran en el nodo
HOVER_TOOLTIPS = [
       ("Api", "@index"),
        ("¿Depreciada?", "@depreciada"),
        ("Consumida", "@degree"),
        ("Puerto", "@port"),
        ("Servicios", "@service"),
        ("Prueba", "@testLink"),
        ("Produccion", "@productionLink"),
        ("WSO2", "@authenticationLink"),
        ("Repositorio", "@repositoryLink"),
        ("Excel map", "@excelLink")
]


#Creación de la figura con su herramientas y tamaño
plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
            x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

#Click listener
plot.add_tools(TapTool())

#Elemento para información detallada del nodo
div = Div(width=100, height=plot.height, height_policy="fixed")
layout = row(plot, div)
point_attributes = ['x','y','sx','sy']

#Create a network graph object
# https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
network_graph = from_networkx(G, networkx.spring_layout, scale=10, center=(0, 0))


#render del nodo con tamaño y color
network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color="grey")
#colores al seleccionar un nodo
network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)

#opacidad del nodo cuando otro esta seleccionado
network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.3, line_width=1)
#Set edge highlight colors
network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)

#Highlight nodes and edges
network_graph.selection_policy = NodesAndLinkedEdges()
network_graph.inspection_policy = NodesAndLinkedEdges()
plot.renderers.append(network_graph)

#Add Labels
x, y = zip(*network_graph.layout_provider.graph_layout.values())
node_labels = list(G.nodes())
source = ColumnDataSource({'x': x, 'y': y, 'name': [node_labels[i] for i in range(len(x))]})
labels = LabelSet(x='x', y='y', text='name', source=source, background_fill_color='white', text_font_size='10px', background_fill_alpha=.7)
plot.renderers.append(labels)

#Se vincula el metodo con la acción de click
taptool = plot.select(type=TapTool)
plot.js_on_event(Tap, display_event(div, network_graph.node_renderer.data_source, attributes=point_attributes))
#  plot.js_on_event(events.DoubleTap, display_event(div, attributes=point_attributes))


curdoc().add_root(layout)

output_file("main.html", title="Apis Map")
show(layout)
#save(plot, filename=f"{title}.html")