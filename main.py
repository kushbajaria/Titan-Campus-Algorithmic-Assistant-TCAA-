import random
import time
import tkinter as tk

from tkinter import messagebox, simpledialog
from tkinter import filedialog
from PIL import Image, ImageTk
from algorithms import dijkstra
from algorithms.dijkstra_rebuild_path import rebuild_path as dijkstra_rebuild_path
from algorithms import prim
from algorithms import greedy_scheduler, knapsack
from algorithms import naive as naive_mod, rabin_karp as rk_mod, kmp as kmp_mod


# create gui window
root = tk.Tk()
root.title("Titan Campus Algorithmic Assistant (TCAA)")
root.geometry("1100x900")

# load campus map image (keep same filename or update)
try:
    campus_map = Image.open("campus_map.png")
    campus_map = campus_map.resize((850, 600))
    campus_bg = ImageTk.PhotoImage(campus_map)
except Exception:
    campus_bg = None

# campus map canvas
canvas = tk.Canvas(root, width=850, height=600, bg="white")
if campus_bg:
    canvas.create_image(0, 0, anchor="nw", image=campus_bg)
    canvas.image = campus_bg
canvas.pack(pady=10, side="left")

# right-side output / controls frame
right_frame = tk.Frame(root)
right_frame.pack(side="left", padx=10, fill="y")

# top row controls (on right frame)
control_frame_top = tk.Frame(right_frame)
control_frame_top.pack(pady=5, anchor="nw")

tk.Label(control_frame_top, text="Building Name:").grid(row=0, column=0, sticky="w", padx=2)
node_entry = tk.Entry(control_frame_top, width=20)
node_entry.grid(row=0, column=1, padx=2)

add_node_button = tk.Button(control_frame_top, text="Add Node")
add_node_button.grid(row=0, column=2, padx=5)

connect_button = tk.Button(control_frame_top, text="Connect Nodes")
connect_button.grid(row=0, column=3, padx=5)

# middle controls: start/end selection (keep entries for familiarity)
control_frame_middle = tk.Frame(right_frame)
control_frame_middle.pack(pady=5, anchor="nw")

tk.Label(control_frame_middle, text="Start:").grid(row=0, column=0, padx=2, sticky="w")
traversal_start = tk.Entry(control_frame_middle, width=12)
traversal_start.grid(row=0, column=1, padx=2)

tk.Label(control_frame_middle, text="End:").grid(row=0, column=2, padx=2, sticky="w")
end_entry = tk.Entry(control_frame_middle, width=12)
end_entry.grid(row=0, column=3, padx=2)

tk.Label(control_frame_middle, text="Goal (for set):").grid(row=1, column=0, padx=2, sticky="w")
traversal_goal = tk.Entry(control_frame_middle, width=12)
traversal_goal.grid(row=1, column=1, padx=2)

goal_button = tk.Button(control_frame_middle, text="Set Goal")
goal_button.grid(row=1, column=3, padx=2)

accessible_only_var = tk.BooleanVar()
accessible_check = tk.Checkbutton(right_frame, text="Accessible Only", variable=accessible_only_var)
accessible_check.pack(pady=5, anchor="nw")

# bottom row buttons for algorithms
control_frame_bottom = tk.Frame(right_frame)
control_frame_bottom.pack(pady=8, anchor="nw")

bfs_button = tk.Button(control_frame_bottom, text="Run BFS")
bfs_button.grid(row=0, column=0, padx=3, pady=2)

dfs_button = tk.Button(control_frame_bottom, text="Run DFS")
dfs_button.grid(row=0, column=1, padx=3, pady=2)

dijkstra_button = tk.Button(control_frame_bottom, text="Run Dijkstra")
dijkstra_button.grid(row=0, column=2, padx=3, pady=2)

prim_button = tk.Button(control_frame_bottom, text="Run Prim's MST")
prim_button.grid(row=0, column=3, padx=3, pady=2)

randomize_button = tk.Button(control_frame_bottom, text="Randomize Weights")
randomize_button.grid(row=0, column=4, padx=3, pady=2)

# info / output box
output_label = tk.Label(right_frame, text="Output")
output_label.pack(anchor="nw")
output_box = tk.Text(right_frame, width=40, height=25)
output_box.pack(pady=5, anchor="nw")

# dictionary/list to store nodes/edges
# nodes[name] = (x,y)
nodes = {}
# edges: [start, end, distance, time, accessible(bool), open_(bool), line_id, label_id]
edges = []
pending_node = None

# prepare to place node function
def prepare_node_placement():
    global pending_node
    name = node_entry.get().strip()
    if not name:
        messagebox.showwarning("Error", "Please enter a building name.")
        return
    if name in nodes:
        messagebox.showwarning("Error", f"Building {name} already exists.")
        return
    pending_node = name
    node_entry.delete(0, tk.END)
    messagebox.showinfo("Node Placement", f"Click on the canvas to place '{name}'.")

# place node function
def place_node(event):
    global pending_node
    if not pending_node:
        return

    x, y = event.x, event.y
    radius = 18
    oval = canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="lightblue", outline="black", width=2)
    text_id = canvas.create_text(x, y, text=pending_node)
    nodes[pending_node] = (x, y)
    pending_node = None

add_node_button.config(command=prepare_node_placement)
canvas.bind("<Button-1>", place_node)

# connect nodes function
def connect_nodes():
    start = traversal_start.get().strip()
    end = end_entry.get().strip()

    if start not in nodes or end not in nodes:
        messagebox.showwarning("Error", "One or both buildings do not exist.")
        return
    if start == end:
        messagebox.showwarning("Error", "Cannot connect a building to itself.")
        return

    distance = simpledialog.askinteger("Distance", f"Enter distance from {start} to {end}:")
    if distance is None:
        return
    time = simpledialog.askinteger("Time", f"Enter time from {start} to {end}:")
    if time is None:
        return
    accessible = messagebox.askyesno("Accessibility", "Is this path accessible?")

    x1, y1 = nodes[start]
    x2, y2 = nodes[end]
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
    color = "black" if accessible else "orange"

    line_id = canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
    label_id = canvas.create_text(mid_x, mid_y, text=f"{distance}/{time}", fill="black", tags="edge_label")

    # store edge; undirected graph represented by storing once but we'll add both directions when building adjacency
    edges.append([start, end, int(distance), int(time), bool(accessible), True, line_id, label_id])

    messagebox.showinfo("Edge Created", f"Edge from {start} to {end} created successfully.")

connect_button.config(command=connect_nodes)

# toggle edges function (right-click)
def toggle_edge(event):
    clicked_items = canvas.find_overlapping(event.x - 2, event.y - 2, event.x + 2, event.y + 2)
    for item in clicked_items:
        for edge in edges:
            if len(edge) >= 8 and edge[6] == item:
                edge[5] = not edge[5]  # open/closed
                new_color = "red" if not edge[5] else ("black" if edge[4] else "orange")
                canvas.itemconfig(edge[6], fill=new_color)
                status = "closed" if not edge[5] else "open"
                messagebox.showinfo("Edge Update", f"Edge between {edge[0]} and {edge[1]} is now {status}.")
                return

canvas.bind("<Button-3>", toggle_edge)

# build weighted adjacency list
def build_graph(accessible_only=False):
    """
    Returns graph in format:
    { node: [(neighbor, weight), ...], ... }
    weight used = distance (you can change to time if preferred)
    """
    graph = {node: [] for node in nodes}
    for start, end, distance, time_cost, accessible, open_, line_id, label_id in edges:
        if not open_:
            continue
        if accessible_only and not accessible:
            continue
        # undirected: add both directions
        graph[start].append((end, distance))
        graph[end].append((start, distance))
    return graph

# BFS (fewest hops) - works with weighted adjacency list (ignores weights)
def bfs(start, goal, accessible_only=False):
    graph = build_graph(accessible_only)
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

        for neighbor, _ in graph.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return None, traversal_order

# DFS traversal (iterative) - works with weighted adjacency list (ignores weights)
def dfs(start, goal, accessible_only=False):
    graph = build_graph(accessible_only)
    visited = set()
    stack = [(start, [start])]
    traversal_order = []

    while stack:
        current, path = stack.pop()
        if current in visited:
            continue

        visited.add(current)
        traversal_order.append(current)

        if current == goal:
            return path, traversal_order

        # reversed so original order similar to recursive
        for neighbor, _ in reversed(graph.get(current, [])):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))

    return None, traversal_order

# visualization implementation function
def visualize(path, visited, highlight_color="green", line_width=3):
    canvas.delete("traversal")
    # highlight visited nodes
    for node in visited:
        if node not in nodes:
            continue
        x, y = nodes[node]
        radius = 18
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="gray", width=2, tags="traversal")

    # draw path edges
    if path:
        for i in range(len(path) - 1):
            a = path[i]
            b = path[i + 1]
            if a in nodes and b in nodes:
                x1, y1 = nodes[a]
                x2, y2 = nodes[b]
                canvas.create_line(x1, y1, x2, y2, fill=highlight_color, width=line_width, tags="traversal")

# Bind and handlers for buttons
def run_bfs():
    start = traversal_start.get().strip()
    goal = traversal_goal.get().strip()
    if start not in nodes or goal not in nodes:
        messagebox.showwarning("Error", "Start or goal building does not exist.")
        return
    path, visited = bfs(start, goal, accessible_only_var.get())
    if not path:
        output_box.insert(tk.END, "BFS: No path was found.\n\n")
        messagebox.see(tk.END)
    else:
        output_box.insert(tk.END,
            f"BFS Result:\nFull Path: {' -> '.join(path)}\n"
            f"Traversal Order: {' -> '.join(visited)}\n"
            f"Path Length (edges): {len(path) - 1}\n\n"
        )
        output_box.see(tk.END)
    visualize(path if path else [], visited)

def run_dfs():
    start = traversal_start.get().strip()
    goal = traversal_goal.get().strip()
    if start not in nodes or goal not in nodes:
        messagebox.showwarning("Error", "Start or goal building does not exist.")
        return
    path, visited = dfs(start, goal, accessible_only_var.get())
    if not path:
        output_box.insert(tk.END, "DFS: No path was found.\n\n")
        output_box.see(tk.END)
    else:
        output_box.insert(tk.END,
            f"DFS Result:\nFull Path: {' -> '.join(path)}\n"
            f"Traversal Order: {' -> '.join(visited)}\n"
            f"Path Length (edges): {len(path) - 1}\n\n"
        )
        output_box.see(tk.END)
    visualize(path if path else [], visited, highlight_color="blue")

def run_dijkstra():
    start = traversal_start.get().strip()
    goal = end_entry.get().strip()
    if start not in nodes or goal not in nodes:
        messagebox.showwarning("Error", "Start or end building does not exist.")
        return

    graph = build_graph(accessible_only_var.get())
    try:
        distances, parents = dijkstra(graph, start)
    except Exception as e:
        messagebox.showerror("Error", f"Dijkstra failed: {e}")
        return

    dist_to_goal = distances.get(goal, float('inf'))
    if dist_to_goal == float('inf'):
        output_box.insert(tk.END, f"Dijkstra: No path found from {start} to {goal}.\n\n")
        output_box.see(tk.END)
        return

    # rebuild path
    try:
        path = dijkstra_rebuild_path(parents, goal)
    except Exception:
        # fall back to reconstruct manually
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = parents.get(cur)
        path.reverse()

    output_box.insert(tk.END,
        f"Dijkstra Result:\nStart: {start}  End: {goal}\n"
        f"Shortest Distance: {dist_to_goal}\n"
        f"Path: {' -> '.join(path)}\n\n"
    )
    output_box.see(tk.END)
    visualize(path, path, highlight_color="darkgreen")

def run_prim():
    start = traversal_start.get().strip()
    if start not in nodes:
        messagebox.showwarning("Error", "Start building does not exist.")
        return

    graph = build_graph(accessible_only_var.get())
    try:
        res = prim(graph, start)
        # handle prim returning (mst_edges, cost) or (mst_edges, cost, disconnected)
        if len(res) == 2:
            mst_edges, total_cost = res
            disconnected = (len(mst_edges) == 0 and len(nodes) > 0)
        else:
            mst_edges, total_cost, disconnected = res
    except Exception as e:
        messagebox.showerror("Error", f"Prim failed: {e}")
        return

    if disconnected:
        output_box.insert(tk.END, "Prim's MST: Graph appears to be disconnected. Returned forest for component of start node.\n")
    output_box.insert(tk.END, "Prim's MST Edges:\n")
    for u, v, w in mst_edges:
        output_box.insert(tk.END, f"  {u} -- {v} (weight {w})\n")
    output_box.insert(tk.END, f"Total MST Cost: {total_cost}\n\n")
    output_box.see(tk.END)

    # visualize MST: draw each MST edge in purple
    canvas.delete("mst")
    for u, v, w in mst_edges:
        if u in nodes and v in nodes:
            x1, y1 = nodes[u]
            x2, y2 = nodes[v]
            canvas.create_line(x1, y1, x2, y2, fill="purple", width=3, tags="mst")
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            canvas.create_text(mx, my + 12, text=str(w), tags="mst")

# connect buttons
bfs_button.config(command=run_bfs)
dfs_button.config(command=run_dfs)
dijkstra_button.config(command=run_dijkstra)
prim_button.config(command=run_prim)

# randomize weights function
def randomize_weights():
    for edge in edges:
        edge[2] = random.randint(1, 20)  # distance
        edge[3] = random.randint(1, 20)  # time

    # update edge labels
    for start, end, distance, time_cost, accessible, open_, line_id, label_id in edges:
        if label_id:
            canvas.itemconfig(label_id, text=f"{distance}/{time_cost}")
    messagebox.showinfo("Randomize", "Edge distances and times have been randomized.")

randomize_button.config(command=randomize_weights)

# set goal function
def set_goal():
    goal = traversal_goal.get().strip()
    if goal not in nodes:
        messagebox.showwarning("Error", "Goal building does not exist.")
        return
    messagebox.showinfo("Goal Set", f"Goal set to {goal}")

goal_button.config(command=set_goal)

# helper: clear output
def clear_output():
    output_box.delete("1.0", tk.END)

clear_button = tk.Button(right_frame, text="Clear Output", command=clear_output)
clear_button.pack(anchor="nw", pady=6)

# Module launcher buttons
module_frame = tk.Frame(right_frame)
module_frame.pack(pady=6, anchor="nw")

study_button = tk.Button(module_frame, text="Study Planner")
study_button.grid(row=0, column=0, padx=3)

notes_button = tk.Button(module_frame, text="Notes Search")
notes_button.grid(row=0, column=1, padx=3)

info_button = tk.Button(module_frame, text="Algorithm Info")
info_button.grid(row=0, column=2, padx=3)

def open_study_planner():
    win = tk.Toplevel(root)
    win.title("Study Planner")
    win.geometry("600x500")

    tasks = []  # local list of (name, time, value)

    # inputs
    input_frame = tk.Frame(win)
    input_frame.pack(pady=6)

    tk.Label(input_frame, text="Task Name:").grid(row=0, column=0)
    task_name_entry = tk.Entry(input_frame, width=20)
    task_name_entry.grid(row=0, column=1)

    tk.Label(input_frame, text="Time:").grid(row=1, column=0)
    task_time_entry = tk.Entry(input_frame, width=8)
    task_time_entry.grid(row=1, column=1)

    tk.Label(input_frame, text="Value:").grid(row=2, column=0)
    task_value_entry = tk.Entry(input_frame, width=8)
    task_value_entry.grid(row=2, column=1)

    listbox = tk.Listbox(win, width=60)
    listbox.pack(pady=6)

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

    add_btn = tk.Button(input_frame, text="Add Task", command=add_task)
    add_btn.grid(row=3, column=0, columnspan=2, pady=4)

    # available time
    avail_frame = tk.Frame(win)
    avail_frame.pack(pady=6)
    tk.Label(avail_frame, text="Available Time:").grid(row=0, column=0)
    avail_entry = tk.Entry(avail_frame, width=10)
    avail_entry.grid(row=0, column=1)

    output_text = tk.Text(win, height=10, width=70)
    output_text.pack(pady=6)

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

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=6)
    tk.Button(btn_frame, text="Run Greedy", command=run_greedy).grid(row=0, column=0, padx=6)
    tk.Button(btn_frame, text="Run DP", command=run_dp).grid(row=0, column=1, padx=6)

def open_notes_search():
    win = tk.Toplevel(root)
    win.title("Notes Search")
    win.geometry("700x600")

    content = {"text": ""}

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
        messagebox.showinfo("Loaded", f"Loaded file: {fname}")

    tk.Button(win, text="Load File", command=load_file).pack(pady=6)

    # pattern input
    pat_frame = tk.Frame(win)
    pat_frame.pack(pady=6)
    tk.Label(pat_frame, text="Pattern:").grid(row=0, column=0)
    pattern_entry = tk.Entry(pat_frame, width=40)
    pattern_entry.grid(row=0, column=1)

    alg_var = tk.StringVar(value="ALL")
    rb_frame = tk.Frame(win)
    rb_frame.pack(pady=4)
    for val in ["Naive", "Rabin-Karp", "KMP", "ALL"]:
        tk.Radiobutton(rb_frame, text=val, variable=alg_var, value=val).pack(side='left', padx=6)

    output = tk.Text(win, height=20, width=80)
    output.pack(pady=6)

    def run_search():
        txt = content.get('text', '')
        pat = pattern_entry.get()
        if not txt:
            messagebox.showwarning("No File", "Load a document first.")
            return
        if not pat:
            messagebox.showwarning("No Pattern", "Enter a pattern to search.")
            return

        choice = alg_var.get()
        output.delete('1.0', tk.END)

        def run_and_report(name, func):
            t0 = time.perf_counter()
            try:
                res = func(txt, pat)
            except TypeError:
                # some functions have different signatures; try wrapper
                res = func(txt, pat)
            t1 = time.perf_counter()
            output.insert(tk.END, f"{name}: found {len(res)} matches; indices sample: {res[:10]}\nTime: {t1-t0:.6f}s\n\n")

        if choice == 'Naive' or choice == 'ALL':
            run_and_report('Naive', naive_mod.naive_string_match)
        if choice == 'Rabin-Karp' or choice == 'ALL':
            run_and_report('Rabin-Karp', rk_mod.rabin_karp)
        if choice == 'KMP' or choice == 'ALL':
            run_and_report('KMP', kmp_mod.kmp_search)

    tk.Button(win, text="Run Search", command=run_search).pack(pady=6)

def open_info_window():
    win = tk.Toplevel(root)
    win.title("Algorithm Info")
    win.geometry("600x500")
    txt = tk.Text(win, wrap='word')
    txt.pack(expand=True, fill='both')
    info = (
        "Algorithm Complexities:\n"
        "BFS/DFS: O(V+E)\n"
        "Dijkstra (binary heap): O((V+E) log V)\n"
        "Prim (binary heap): O((V+E) log V)\n"
        "Greedy Scheduler (sort by ratio): O(n log n)\n"
        "0/1 Knapsack (DP): O(n * W) where W is available time\n"
        "Naive string match: O(nm)\n"
        "Rabin-Karp average: O(n+m), worst-case O(nm) due to collisions\n"
        "KMP: O(n+m)\n\n"
        "P vs NP (short reflection):\n"
        "P is the class of problems solvable in polynomial time. NP is the class whose solutions can be verified in polynomial time.\n"
        "It is unknown whether P == NP. Many combinatorial optimization problems (e.g., subset sum) are NP-complete, meaning if any NP-complete problem is in P, then P==NP.\n"
    )
    txt.insert('1.0', info)

study_button.config(command=open_study_planner)
notes_button.config(command=open_notes_search)
info_button.config(command=open_info_window)

# run loop
root.mainloop()
