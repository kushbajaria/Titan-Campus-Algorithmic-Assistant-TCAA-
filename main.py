import random
import time
import tkinter as tk

from tkinter import messagebox, simpledialog, filedialog, ttk
from tkinter import font as tkfont
from PIL import Image, ImageTk
from algorithms import dijkstra, prim, greedy_scheduler, knapsack
from algorithms.dijkstra_rebuild_path import rebuild_path as dijkstra_rebuild_path
from algorithms import naive as naive_mod, rabin_karp as rk_mod, kmp as kmp_mod

# optional document libraries
try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    import docx
except Exception:
    docx = None

# Create GUI window
root = tk.Tk()
root.title("Titan Campus Navigator")
root.geometry("1100x900")

# UI styling
style = ttk.Style(root)
try:
    style.theme_use('clam')
except Exception:
    pass
primary_font = tkfont.Font(family='Arial', size=11)
title_font = tkfont.Font(family='Arial', size=14, weight='bold')
mono_font = tkfont.Font(family='Courier', size=10)
style.configure('TButton', padding=6)
style.configure('TLabel', font=primary_font)

# page background color used by style cards
PAGE_BG = '#f7f7f7'

# card/section styles for nicer navigator
style.configure('Card.TFrame', background=PAGE_BG)
style.configure('Section.TLabel', font=title_font, background=PAGE_BG)
style.configure('Small.TLabel', font=primary_font, background=PAGE_BG)
style.configure('Accent.TButton', font=primary_font)

# status bar variable (updated by actions)
page_location_var = tk.StringVar(value='Home')

# Pages: home, navigator, study, notes, algo info
pages = {}
home_frame = ttk.Frame(root)
navigator_frame = ttk.Frame(root)
study_frame = ttk.Frame(root)
notes_frame = ttk.Frame(root)
info_frame = ttk.Frame(root)
pages['Home'] = home_frame
pages['Campus Navigator'] = navigator_frame
pages['Study Planner'] = study_frame
pages['Notes Search'] = notes_frame
pages['Algorithm Info'] = info_frame

# global header (single page-location indicator for all pages)
global_header = ttk.Frame(root)
global_header.pack(fill='x')
ttk.Label(global_header, textvariable=page_location_var, font=primary_font).pack(side='left', padx=10)

# right-side header button (switches between Home and Quit depending on page)
header_right_btn = ttk.Button(global_header, text='Home', command=lambda: show_page('Home'))
header_right_btn.pack(side='right', padx=10)

# Top right page indicator
def show_page(name):
    for f in pages.values():
        try:
            f.pack_forget()
        except Exception:
            pass
    pages[name].pack(fill='both', expand=True)
    page_location_var.set(name.title())

    # update header button: show Quit when on Home, otherwise show Home
    try:
        if name == 'Home':
            header_right_btn.config(text='Quit', command=root.destroy)
        else:
            header_right_btn.config(text='Home', command=lambda: show_page('Home'))
    except NameError:
        pass

# Build home page (simple navigation)
def build_home():
    for child in home_frame.winfo_children():
        child.destroy()
    
    title = ttk.Label(home_frame, text="Titan Campus Algorithmic Assistant", font=title_font)
    title.pack(pady=20, anchor='center')
    subtitle = ttk.Label(home_frame, text="Select a module to begin", font=primary_font)
    subtitle.pack(pady=8, anchor='center')
    btn_frame = ttk.Frame(home_frame)
    btn_frame.pack(pady=20, anchor='center')
    ttk.Button(btn_frame, text='Campus Navigator', width=20, command=lambda: show_page('Campus Navigator')).grid(row=0, column=0, padx=8, pady=8)
    ttk.Button(btn_frame, text='Study Planner', width=20, command=lambda: (build_study_page(), show_page('Study Planner'))).grid(row=0, column=1, padx=8, pady=8)
    ttk.Button(btn_frame, text='Notes Search', width=20, command=lambda: (build_notes_page(), show_page('Notes Search'))).grid(row=1, column=0, padx=8, pady=8)
    ttk.Button(btn_frame, text='Algorithm Info', width=20, command=lambda: (build_info_page(), show_page('Algorithm Info'))).grid(row=1, column=1, padx=8, pady=8)

# build home and show it at startup
build_home()
# show home page at startup
show_page('Home')

navigator_frame.config(padding=10)

# Title
title_label = ttk.Label(navigator_frame, text="CSUF Campus Navigator", font=title_font)
title_label.pack(pady=(0, 10))

# Control panel
control_frame = ttk.LabelFrame(navigator_frame, text="Navigation Controls", padding=10)
control_frame.pack(fill='x', pady=(0, 10))

# Start and End building selectors
selector_frame = ttk.Frame(control_frame)
selector_frame.pack(fill='x', pady=5)

ttk.Label(selector_frame, text='Start Building:', font=primary_font).grid(row=0, column=0, sticky='w', padx=5)
start_building = ttk.Combobox(selector_frame, width=25, state='readonly')
start_building.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(selector_frame, text='End Building:', font=primary_font).grid(row=0, column=2, sticky='w', padx=5)
end_building = ttk.Combobox(selector_frame, width=25, state='readonly')
end_building.grid(row=0, column=3, padx=5, pady=5)

# Algorithm buttons
button_frame = ttk.Frame(control_frame)
button_frame.pack(fill='x', pady=10)

bfs_button = ttk.Button(button_frame, text='Run BFS (Fewest Hops)', width=20)
bfs_button.pack(side='left', padx=5)

dfs_button = ttk.Button(button_frame, text='Run DFS Traversal', width=20)
dfs_button.pack(side='left', padx=5)

dijkstra_button = ttk.Button(button_frame, text='Run Dijkstra (Shortest)', width=20)
dijkstra_button.pack(side='left', padx=5)

prim_button = ttk.Button(button_frame, text="Run Prim's MST", width=20)
prim_button.pack(side='left', padx=5)

# Output area
output_frame = ttk.LabelFrame(navigator_frame, text="Results", padding=10)
output_frame.pack(fill='both', expand=True)

output_box = tk.Text(output_frame, width=100, height=25, font=mono_font, wrap='word', bg='#ffffff', fg='black')
output_scroll = ttk.Scrollbar(output_frame, orient='vertical', command=output_box.yview)
output_box['yscrollcommand'] = output_scroll.set
output_box.pack(side='left', fill='both', expand=True)
output_scroll.pack(side='right', fill='y')

clear_button = ttk.Button(navigator_frame, text="Clear Output", command=lambda: output_box.delete("1.0", tk.END))
clear_button.pack(pady=5)

# Graph data structures
nodes = {}
edges = []

def load_csuf_campus():
    """Load realistic CSUF campus buildings and connections"""
    nodes.clear()
    edges.clear()
    
    # CSUF Buildings (realistic campus locations)
    buildings = [
        'Pollak Library',
        'Titan Student Union',
        'McCarthy Hall',
        'Engineering & Computer Science',
        'Langsdorf Hall',
        'Titan Gym',
        'Visual Arts Center',
        'Performing Arts Center',
        'Dan Black Hall',
        'Humanities & Social Sciences'
    ]
    
    for building in buildings:
        nodes[building] = {}
    
    # Realistic campus connections with distances in meters
    # Format: (building1, building2, distance_meters, time_minutes, accessible)
    campus_edges = [
        ('Pollak Library', 'Titan Student Union', 150, 3, True),
        ('Pollak Library', 'McCarthy Hall', 200, 4, True),
        ('Titan Student Union', 'McCarthy Hall', 180, 3, True),
        ('Titan Student Union', 'Dan Black Hall', 220, 4, True),
        ('McCarthy Hall', 'Engineering & Computer Science', 250, 5, True),
        ('McCarthy Hall', 'Humanities & Social Sciences', 190, 4, True),
        ('Engineering & Computer Science', 'Langsdorf Hall', 160, 3, True),
        ('Engineering & Computer Science', 'Dan Black Hall', 280, 5, True),
        ('Langsdorf Hall', 'Titan Gym', 300, 6, True),
        ('Langsdorf Hall', 'Visual Arts Center', 240, 5, True),
        ('Titan Gym', 'Visual Arts Center', 180, 3, True),
        ('Visual Arts Center', 'Performing Arts Center', 120, 2, True),
        ('Performing Arts Center', 'Humanities & Social Sciences', 200, 4, True),
        ('Dan Black Hall', 'Humanities & Social Sciences', 170, 3, True),
        ('Pollak Library', 'Langsdorf Hall', 350, 7, True),
        ('Titan Student Union', 'Titan Gym', 400, 8, False),  # Not accessible
    ]
    
    for (u, v, dist, time_cost, accessible) in campus_edges:
        edges.append([u, v, dist, time_cost, accessible, True, None, None, None])
    
    # Update dropdowns
    building_list = sorted(buildings)
    start_building['values'] = building_list
    end_building['values'] = building_list
    
    if building_list:
        start_building.current(0)
        end_building.current(1 if len(building_list) > 1 else 0)

def build_graph():
    """Build adjacency list representation of graph"""
    graph = {node: [] for node in nodes}
    for edge in edges:
        start, end, distance, time_cost, accessible, is_open = edge[:6]
        if is_open:  # Only include open edges
            # Undirected graph - add both directions
            graph[start].append((end, distance))
            graph[end].append((start, distance))
    return graph

def bfs(start, goal):
    """BFS: Find path with fewest hops"""
    graph = build_graph()
    visited = set()
    queue = [(start, [start])]
    traversal_order = []
    
    while queue:
        current, path = queue.pop(0)
        if current in visited:
            continue
        
        visited.add(current)
        traversal_order.append(current)
        
        if current == goal:
            return path, traversal_order
        
        for neighbor, _ in sorted(graph.get(current, [])):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
    
    return None, traversal_order

def dfs(start):
    """DFS: Traverse entire graph and return order"""
    graph = build_graph()
    visited = set()
    traversal_order = []
    
    def dfs_recursive(node):
        visited.add(node)
        traversal_order.append(node)
        
        for neighbor, _ in sorted(graph.get(node, [])):
            if neighbor not in visited:
                dfs_recursive(neighbor)
    
    dfs_recursive(start)
    
    # Check connectivity
    all_nodes = set(nodes.keys())
    disconnected = all_nodes - visited
    
    return traversal_order, disconnected

def dijkstra(start, goal):
    """Dijkstra: Find shortest weighted path"""
    import heapq
    
    graph = build_graph()
    distances = {node: float('inf') for node in nodes}
    distances[start] = 0
    parents = {node: None for node in nodes}
    pq = [(0, start)]
    visited = set()
    
    while pq:
        curr_dist, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current == goal:
            break
        
        for neighbor, weight in graph.get(current, []):
            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parents[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
    
    # Rebuild path
    if distances[goal] == float('inf'):
        return None, distances[goal]
    
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parents[current]
    path.reverse()
    
    return path, distances[goal]

def prim_mst(start):
    """Prim's Algorithm: Find Minimum Spanning Tree"""
    import heapq
    
    graph = build_graph()
    mst_edges = []
    visited = set([start])
    edges_heap = []
    
    # Add all edges from start node
    for neighbor, weight in graph.get(start, []):
        heapq.heappush(edges_heap, (weight, start, neighbor))
    
    total_cost = 0
    
    while edges_heap and len(visited) < len(nodes):
        weight, u, v = heapq.heappop(edges_heap)
        
        if v in visited:
            continue
        
        # Add edge to MST
        visited.add(v)
        mst_edges.append((u, v, weight))
        total_cost += weight
        
        # Add all edges from newly visited node
        for neighbor, edge_weight in graph.get(v, []):
            if neighbor not in visited:
                heapq.heappush(edges_heap, (edge_weight, v, neighbor))
    
    disconnected = len(visited) < len(nodes)
    return mst_edges, total_cost, disconnected

def run_bfs():
    """Execute BFS and display results"""
    start = start_building.get().strip()
    goal = end_building.get().strip()
    
    if not start or not goal:
        messagebox.showwarning("Error", "Please select start and end buildings.")
        return
    
    if start not in nodes or goal not in nodes:
        messagebox.showwarning("Error", "Selected buildings do not exist.")
        return
    
    path, visited = bfs(start, goal)
    
    output_box.insert(tk.END, '\n' + '=' * 70 + '\n')
    output_box.insert(tk.END, 'BFS RESULT (Fewest Hops)\n')
    output_box.insert(tk.END, '=' * 70 + '\n')
    
    if not path:
        output_box.insert(tk.END, f"❌ No path found from '{start}' to '{goal}'\n")
    else:
        output_box.insert(tk.END, f"Start: {start}\n")
        output_box.insert(tk.END, f"Goal:  {goal}\n\n")
        output_box.insert(tk.END, f"Path (fewest hops):\n")
        for i, building in enumerate(path, 1):
            output_box.insert(tk.END, f"  {i}. {building}\n")
        output_box.insert(tk.END, f"\n✓ Number of hops: {len(path) - 1}\n")
    
    output_box.insert(tk.END, f"\nTraversal order: {' → '.join(visited)}\n")
    output_box.see(tk.END)

def run_dfs():
    """Execute DFS and display results"""
    start = start_building.get().strip()
    
    if not start:
        messagebox.showwarning("Error", "Please select a start building.")
        return
    
    if start not in nodes:
        messagebox.showwarning("Error", "Selected building does not exist.")
        return
    
    traversal, disconnected = dfs(start)
    
    output_box.insert(tk.END, '\n' + '=' * 70 + '\n')
    output_box.insert(tk.END, 'DFS RESULT (Depth-First Traversal)\n')
    output_box.insert(tk.END, '=' * 70 + '\n')
    output_box.insert(tk.END, f"Starting from: {start}\n\n")
    output_box.insert(tk.END, f"Traversal order:\n")
    for i, building in enumerate(traversal, 1):
        output_box.insert(tk.END, f"  {i}. {building}\n")
    
    output_box.insert(tk.END, f"\n✓ Visited {len(traversal)} buildings\n")
    
    if disconnected:
        output_box.insert(tk.END, f"\n⚠ Warning: {len(disconnected)} buildings not reachable:\n")
        for building in disconnected:
            output_box.insert(tk.END, f"  - {building}\n")
    else:
        output_box.insert(tk.END, "\n✓ Graph is fully connected!\n")
    
    output_box.see(tk.END)

def run_dijkstra():
    """Execute Dijkstra and display results"""
    start = start_building.get().strip()
    goal = end_building.get().strip()
    
    if not start or not goal:
        messagebox.showwarning("Error", "Please select start and end buildings.")
        return
    
    if start not in nodes or goal not in nodes:
        messagebox.showwarning("Error", "Selected buildings do not exist.")
        return
    
    path, distance = dijkstra(start, goal)
    
    output_box.insert(tk.END, '\n' + '=' * 70 + '\n')
    output_box.insert(tk.END, 'DIJKSTRA RESULT (Shortest Path)\n')
    output_box.insert(tk.END, '=' * 70 + '\n')
    
    if not path:
        output_box.insert(tk.END, f"❌ No path found from '{start}' to '{goal}'\n")
    else:
        output_box.insert(tk.END, f"Start: {start}\n")
        output_box.insert(tk.END, f"Goal:  {goal}\n\n")
        output_box.insert(tk.END, f"Shortest path:\n")
        for i, building in enumerate(path, 1):
            output_box.insert(tk.END, f"  {i}. {building}\n")
        output_box.insert(tk.END, f"\n✓ Total distance: {distance} meters\n")
        output_box.insert(tk.END, f"✓ Estimated walk time: {distance // 50} minutes\n")
    
    output_box.see(tk.END)

def run_prim():
    """Execute Prim's MST and display results"""
    start = start_building.get().strip()
    
    if not start:
        messagebox.showwarning("Error", "Please select a start building.")
        return
    
    if start not in nodes:
        messagebox.showwarning("Error", "Selected building does not exist.")
        return
    
    mst_edges, total_cost, disconnected = prim_mst(start)
    
    output_box.insert(tk.END, '\n' + '=' * 70 + '\n')
    output_box.insert(tk.END, "PRIM'S MST RESULT (Minimum Spanning Tree)\n")
    output_box.insert(tk.END, '=' * 70 + '\n')
    output_box.insert(tk.END, f"Starting from: {start}\n\n")
    
    if disconnected:
        output_box.insert(tk.END, "⚠ Warning: Graph is disconnected. Showing MST for connected component.\n\n")
    
    output_box.insert(tk.END, f"MST Edges:\n")
    for i, (u, v, weight) in enumerate(mst_edges, 1):
        output_box.insert(tk.END, f"  {i}. {u} ↔ {v} (weight: {weight}m)\n")
    
    output_box.insert(tk.END, f"\n✓ Total edges: {len(mst_edges)}\n")
    output_box.insert(tk.END, f"✓ Total MST cost: {total_cost} meters\n")
    output_box.insert(tk.END, f"✓ Buildings connected: {len(mst_edges) + 1}\n")
    
    output_box.see(tk.END)

# Connect buttons to functions
bfs_button.config(command=run_bfs)
dfs_button.config(command=run_dfs)
dijkstra_button.config(command=run_dijkstra)
prim_button.config(command=run_prim)

# Load campus data on startup
load_csuf_campus()

# Study Planner Page
study_built = False
def build_study_page():
    global study_built
    if study_built:
        return
    study_built = True
    for child in study_frame.winfo_children():
        child.destroy()

    tasks = []

    # user input
    input_frame = ttk.Frame(study_frame)
    input_frame.pack(pady=6, anchor='center')

    ttk.Label(input_frame, text="Task Name:").grid(row=0, column=0)
    task_name_entry = ttk.Entry(input_frame, width=20)
    task_name_entry.grid(row=0, column=1)

    ttk.Label(input_frame, text="Time:").grid(row=1, column=0)
    task_time_entry = ttk.Entry(input_frame, width=8)
    task_time_entry.grid(row=1, column=1)

    ttk.Label(input_frame, text="Value:").grid(row=2, column=0)
    task_value_entry = ttk.Entry(input_frame, width=8)
    task_value_entry.grid(row=2, column=1)

    listbox = tk.Listbox(study_frame, width=60)
    listbox.pack(pady=6, anchor='center')

    def add_task():
        name = task_name_entry.get().strip()
        try:
            t = int(task_time_entry.get().strip())
            v = int(task_value_entry.get().strip())
        except Exception:
            messagebox.showwarning("Error", "Please enter integer time and value.")
            return
        if not name:
            messagebox.showwarning("Error", "Please enter a task name.")
            return
        tasks.append((name, t, v))
        listbox.insert(tk.END, f"{name} | time: {t} | value: {v}")
        task_name_entry.delete(0, tk.END)
        task_time_entry.delete(0, tk.END)
        task_value_entry.delete(0, tk.END)

    add_btn = ttk.Button(input_frame, text="Add Task", command=add_task)
    add_btn.grid(row=3, column=0, columnspan=2, pady=4)

    # available time
    avail_frame = ttk.Frame(study_frame)
    avail_frame.pack(pady=6, anchor='center')
    ttk.Label(avail_frame, text="Available Time:").grid(row=0, column=0)
    avail_entry = ttk.Entry(avail_frame, width=10)
    avail_entry.grid(row=0, column=1)

    output_text = tk.Text(study_frame, height=10, width=70)
    output_text.pack(pady=6, anchor='center')

    def run_greedy():
        try:
            avail = int(avail_entry.get().strip())
        except Exception:
            messagebox.showwarning("Error", "Please enter integer available time.")
            return
        chosen, total_time, total_value = greedy_scheduler.greedy_scheduler(tasks, avail)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Greedy Selection:\n")
        for name, t, v in chosen:
            output_text.insert(tk.END, f"  {name} | time:{t} value:{v}\n")
        output_text.insert(tk.END, f"Total Time: {total_time}  Total Value: {total_value}\n")

    def run_dp():
        try:
            avail = int(avail_entry.get().strip())
        except Exception:
            messagebox.showwarning("Error", "Please enter integer available time.")
            return
        chosen, total_time, total_value = knapsack.dp_optimal_scheduler(tasks, avail)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "DP (0/1 Knapsack) Selection:\n")
        for name, t, v in chosen:
            output_text.insert(tk.END, f"  {name} | time:{t} value:{v}\n")
        output_text.insert(tk.END, f"Total Time: {total_time}  Total Value: {total_value}\n")

    btn_frame = ttk.Frame(study_frame)
    btn_frame.pack(pady=6, anchor='center')
    ttk.Button(btn_frame, text="Run Greedy", command=run_greedy).grid(row=0, column=0, padx=6)
    ttk.Button(btn_frame, text="Run DP", command=run_dp).grid(row=0, column=1, padx=6)

# Notes Search Page
notes_built = False
def build_notes_page():
    global notes_built
    if notes_built:
        return
    notes_built = True
    for child in notes_frame.winfo_children():
        child.destroy()

    # large editable text area for document text or user input
    doc_label = ttk.Label(notes_frame, text="Inputted Text:")
    doc_label.pack(padx=6, pady=(6,0), anchor='center')
    doc_text = tk.Text(notes_frame, height=22, width=140, wrap='word')
    doc_text.pack(padx=6, pady=4)

    content = {"text": ""}

    # Load file through OS
    def load_file():
        fname = filedialog.askopenfilename(filetypes=[("All", "*.*"), ("PDF", "*.pdf"), ("DOCX", "*.docx"), ("Text", "*.txt")])
        if not fname:
            return
        text = ""
        if fname.lower().endswith('.pdf'):
            if PyPDF2 is None:
                messagebox.showerror("Missing Lib", "PyPDF2 is not installed. Cannot read PDFs.")
                return
            try:
                reader = PyPDF2.PdfReader(fname)
                for p in reader.pages:
                    try:
                        text += p.extract_text() or ""
                    except Exception:
                        continue
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read PDF: {e}")
                return
        elif fname.lower().endswith('.docx'):
            if docx is None:
                messagebox.showerror("Missing Lib", "python-docx is not installed. Cannot read DOCX.")
                return
            try:
                doc = docx.Document(fname)
                for p in doc.paragraphs:
                    text += p.text + "\n"
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read DOCX: {e}")
                return
        else:
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    text = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")
                return

        content['text'] = text
        # if user hasn't typed anything into the doc_text box, paste loaded text there
        cur = doc_text.get('1.0', 'end').strip()
        if not cur:
            doc_text.delete('1.0', 'end')
            doc_text.insert('1.0', text)
        messagebox.showinfo("Loaded", f"Loaded file: {fname}")

    ttk.Button(notes_frame, text="Load File", command=load_file).pack(pady=6, padx=6, anchor='center')

    # pattern input and algorithm selection
    pat_frame = ttk.Frame(notes_frame)
    pat_frame.pack(pady=4, padx=6, anchor='center')
    ttk.Label(pat_frame, text="Pattern:").grid(row=0, column=0, sticky='w')
    pattern_entry = ttk.Entry(pat_frame, width=60)
    pattern_entry.grid(row=0, column=1, sticky='w', padx=6)

    alg_var = tk.StringVar(value="ALL")
    rb_frame = ttk.Frame(notes_frame)
    rb_frame.pack(pady=4, padx=6, anchor='center')
    for val in ["Naive", "Rabin-Karp", "KMP", "ALL"]:
        ttk.Radiobutton(rb_frame, text=val, variable=alg_var, value=val).pack(side='left', padx=6)

    # run button
    run_btn = ttk.Button(notes_frame, text="Run Search")
    run_btn.pack(pady=6, padx=6, anchor='center')

    # results text box (separate from the document input text box)
    res_label = ttk.Label(notes_frame, text="Results:")
    res_label.pack(padx=6, anchor='center')
    results_text = tk.Text(notes_frame, height=16, width=100, wrap='word')
    results_text.pack(padx=6, pady=(4,10))

    def run_search():
        txt = doc_text.get('1.0', 'end').rstrip('\n')
        pat = pattern_entry.get()
        if not txt:
            messagebox.showwarning("No Input", "Provide text in the document box or load a file first.")
            return
        if not pat:
            messagebox.showwarning("No Pattern", "Enter a pattern to search.")
            return

        choice = alg_var.get()
        results_text.delete('1.0', tk.END)

        def run_and_report(name, func):
            t0 = time.perf_counter()
            try:
                res = func(txt, pat)
            except TypeError:
                res = func(txt, pat)
            t1 = time.perf_counter()
            results_text.insert(tk.END, f"{name}: found {len(res)} matches; indices sample: {res[:10]}\nTime: {t1-t0:.6f}s\n\n")

        if choice == 'Naive' or choice == 'ALL':
            run_and_report('Naive', naive_mod.naive_string_match)
        if choice == 'Rabin-Karp' or choice == 'ALL':
            run_and_report('Rabin-Karp', rk_mod.rabin_karp)
        if choice == 'KMP' or choice == 'ALL':
            run_and_report('KMP', kmp_mod.kmp_search)

    run_btn.config(command=run_search)

# Algorithm Info Page
info_built = False
def build_info_page():
    global info_built
    if info_built:
        return
    info_built = True
    for child in info_frame.winfo_children():
        child.destroy()
    txt = tk.Text(info_frame, wrap='word')
    txt.pack(expand=True, fill='both', padx=10, pady=6)
    info = (
        "Algorithm Info & Complexities (CPSC 335)\n"
        "\nGraph Algorithms:\n"
        "- BFS: O(V + E)\n"
        "- DFS: O(V + E)\n"
        "- Dijkstra (binary heap): O((V + E) log V)\n"
        "- Prim's MST (binary heap): O((V + E) log V)\n"
        "\nStudy Planner:\n"
        "- Greedy Scheduler: O(n log n)\n"
        "- DP 0/1 Knapsack: O(n * C) where C = capacity in time units\n"
        "\nNotes Search:\n"
        "- Naive: Worst Case: O(m * n), Average Case: O(n + m) or O(n), Best Case: O(n)\n"
        "- Rabin-Karp: Worst Case: O(n * m), Average Case: O(n + m), Best Case: O(n + m)\n"
        "- KMP: Worst Case: O(n + m)\n"
        "\nP vs NP Reflection\n"
        "- P: Problems that can be solved in polynomial time.\n"
        "- NP: Solutions that can be checked in polynomial time.\n"
        "\nSolutions:\n"
        "- Dijkstra Shortest Path Algorithm\n"
        "- Prim's Algorithms (Minimum Spanning Tree)\n"
        "--> Both Algorithms are in Polynomial Time (P). "
    )
    txt.insert('1.0', info)
    # make the info textbox read-only so users can select/copy but not edit
    txt.config(state='disabled')

# status bar at bottom
status_frame = ttk.Frame(root)
status_frame.pack(side='bottom', fill='x')

# run main loop only when executed directly
if __name__ == '__main__':
    root.mainloop()