import tkinter as tk
from tkinter import filedialog  # Adicionado para a caixa de diálogo de seleção de arquivo
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Canvas, Label, Button, StringVar
from itertools import combinations

class GraphVisualizer:
    def hover_enter(self, event):
        event.widget.config(bg="#DDD")  # Cor cinza mais escura ao passar o mouse

    def hover_leave(self, event):
        event.widget.config(bg="SystemButtonFace")  # Cor original ao sair do hover

    def create_buttons(self):
        self.load_button = Button(self.master, text="Carregar Arquivo", command=self.load_graph_file, width=20, height=2)
        self.load_button.pack(pady=(20, 0))
        self.load_button.bind("<Enter>", self.hover_enter)
        self.load_button.bind("<Leave>", self.hover_leave)

        self.kruskal_button = Button(self.master, text="Árvore Geradora Mínima", command=self.generate_minimum_spanning_tree, width=20, height=2)
        self.kruskal_button.pack(pady=(10, 0))
        self.kruskal_button.bind("<Enter>", self.hover_enter)
        self.kruskal_button.bind("<Leave>", self.hover_leave)

    def __init__(self, master):
        self.master = master
        self.master.title("Visualizador de Gráficos")

        # Frames
        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.tree_frame = tk.Frame(master)
        self.tree_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # Canvas para o gráfico
        self.graph_canvas = FigureCanvasTkAgg(plt.Figure(figsize=(4, 4)), master=self.canvas_frame)
        self.graph_canvas.get_tk_widget().pack()
        self.graph_ax = self.graph_canvas.figure.add_subplot(111)

        self.graph_ax.set_xticks([])
        self.graph_ax.set_yticks([])
        self.graph_ax.set_xticklabels([])
        self.graph_ax.set_yticklabels([])

        # Canvas para a árvore mínima
        self.tree_canvas = FigureCanvasTkAgg(plt.Figure(figsize=(4, 4)), master=self.tree_frame)
        self.tree_canvas.get_tk_widget().pack()
        self.tree_ax = self.tree_canvas.figure.add_subplot(111)

        self.tree_ax.set_xticks([])
        self.tree_ax.set_yticks([])
        self.tree_ax.set_xticklabels([])
        self.tree_ax.set_yticklabels([])

        # Label de informações
        self.info_label = Label(self.master, text="", font=("Helvetica", 12))
        self.info_label.pack()

        # variável para armazenar o layout
        self.graph_layout = None

        # Modificar o tamanho da tela em pixels
        root.geometry("1150x500")

        # Desabilitar a capacidade de redimensionar a janela
        root.resizable(width=False, height=False)

        # Crie os botões com efeitos de mouse hover
        self.create_buttons()

    def load_graph_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.graph = self.read_graph(file_path)
            print("Gráfico carregado:")
            for row in self.graph:
                print(row)
            self.load_graph()
            self.draw_graph()


    def read_graph(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            graph = []
            for line in lines:
                row = [int(x) for x in line.strip().rstrip(';').split(',')]
                graph.append(row)
            return graph

    def load_graph(self):
        self.G = nx.Graph()
        num_nodes = len(self.graph)

        for i in range(num_nodes):
            for j in range(num_nodes):
                if self.graph[i][j] > 0:
                    self.G.add_edge(chr(65 + i), chr(65 + j), weight=self.graph[i][j])

    def draw_graph(self):
        self.graph_ax.clear()
        # Use o layout armazenado
        if self.graph_layout is None:
            self.graph_layout = nx.spring_layout(self.G)
        pos = self.graph_layout
        labels = nx.get_edge_attributes(self.G, 'weight')

        nx.draw_networkx_nodes(self.G, pos, ax=self.graph_ax, node_size=700, node_color='skyblue')
        nx.draw_networkx_labels(self.G, pos, ax=self.graph_ax, font_size=10, font_weight='bold')

        edges = nx.draw_networkx_edges(self.G, pos, ax=self.graph_ax)
        edges_labels = nx.draw_networkx_edge_labels(self.G, pos, edge_labels=labels, ax=self.graph_ax)

        for text in edges_labels.values():
            text.set_fontsize(8)

        self.graph_canvas.draw()

    def generate_minimum_spanning_tree(self):
        if hasattr(self, 'G'):  # Verifica se o grafo foi carregado
            self.tree_ax.clear()
            mst = nx.Graph()
            mst_edges = list(self.kruskal_algorithm())[-1]
            mst.add_edges_from(mst_edges)

            pos = nx.spring_layout(self.G)
            nx.draw(self.G, pos, with_labels=True, font_weight='bold', node_size=700, node_color='skyblue', font_size=10, ax=self.graph_ax)
            labels = nx.get_edge_attributes(self.G, 'weight')
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=labels, ax=self.tree_ax)

            self.animate_tree_generation(mst)
        else:
            self.info_label.config(text="Por favor, carregue o arquivo primeiro.")

    def kruskal_algorithm(self):
        edges = []
        for i in range(len(self.graph)):
            for j in range(len(self.graph[i])):
                if self.graph[i][j] > 0:
                    edges.append((chr(65 + i), chr(65 + j), self.graph[i][j]))

        edges.sort(key=lambda x: x[2])

        mst = set()
        parent = {}

        def find(node):
            if parent[node] != node:
                parent[node] = find(parent[node])
            return parent[node]

        def union(node1, node2):
            root1 = find(node1)
            root2 = find(node2)
            parent[root1] = root2

        for node in self.G.nodes:
            parent[node] = node

        for edge in edges:
            u, v, weight = edge
            if find(u) != find(v):
                mst.add((u, v))
                union(u, v)
                yield mst

            # Verifica se a árvore geradora mínima está completa
            if len(mst) == len(self.G.nodes) - 1:
                break

    def animate_tree_generation(self, mst):
        mst_edges = list(mst.edges())

        total_weight = sum([self.G[u][v]['weight'] for u, v in mst_edges])
        self.info_label.config(text=f"Peso mínimo da árvore geradora: {total_weight}")

        pos = self.graph_layout  # Use o mesmo layout do grafo original

        for i in range(len(mst_edges) + 1):
            self.tree_ax.clear()

            nx.draw_networkx_nodes(self.G, pos, ax=self.tree_ax, nodelist=self.G.nodes(), node_size=700, node_color='skyblue')
            nx.draw_networkx_labels(self.G, pos, ax=self.tree_ax)
            nx.draw_networkx_edges(self.G, pos, ax=self.tree_ax)

            current_mst = nx.Graph()
            current_mst.add_edges_from(mst_edges[:i])

            nx.draw_networkx_nodes(self.G, pos, ax=self.tree_ax, nodelist=current_mst.nodes(), node_size=700, node_color='#00FF00')
            nx.draw_networkx_nodes(self.G, pos, ax=self.tree_ax, nodelist=set(self.G.nodes()) - set(current_mst.nodes()), node_size=700, node_color='skyblue')

            nx.draw_networkx_edges(self.G, pos, edgelist=current_mst.edges(), edge_color='#00FF00', width=2, ax=self.tree_ax)

            labels = {(u, v): self.G[u][v]['weight'] for u, v in current_mst.edges()}
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=labels, ax=self.tree_ax)

            self.tree_canvas.draw()
            self.master.update()
            self.master.after(1000)

    def draw_mst(self, mst, edge):
        pos = nx.spring_layout(self.G)

        nx.draw_networkx_nodes(self.G, pos, ax=self.tree_ax, nodelist=self.G.nodes(), node_size=700, node_color='skyblue')
        nx.draw_networkx_labels(self.G, pos, ax=self.tree_ax)
        nx.draw_networkx_edges(self.G, pos, ax=self.tree_ax)

        mst_edges = list(mst.edges())
        mst_weights = nx.get_edge_attributes(self.G, 'weight')

        nx.draw_networkx_edges(self.G, pos, edgelist=mst_edges, edge_color='#00FF00', width=2, ax=self.tree_ax)

        labels = {(u, v): mst_weights.get((u, v), '') for u, v in mst_edges}
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=labels, ax=self.tree_ax)

        self.tree_canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphVisualizer(root)
    root.mainloop()