from __future__ import annotations
import sys, json, os, datetime, copy
from typing import List, Dict, Any

DB = "todos.json"
UNDO_STACK: List[List[Dict[str, Any]]] = []

def load() -> List[Dict[str, Any]]:
    if not os.path.exists(DB): return []
    with open(DB, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return []

def save(items: List[Dict[str, Any]]) -> None:
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

def snapshot(items: List[Dict[str, Any]]):
    UNDO_STACK.append(copy.deepcopy(items))

def add_task(text: str):
    items = load()
    snapshot(items)
    items.append({"text": text, "done": False, "created": ts(), "done_at": None})
    save(items); print("Added:", text)

def list_tasks():
    items = load()
    if not items: print("No tasks."); return
    items_sorted = sorted(items, key=lambda x: (x["done"], x["text"].lower()))
    for i, t in enumerate(items_sorted, 1):
        status = "✓" if t["done"] else " "
        extra = f" (done {t['done_at']})" if t["done_at"] else ""
        print(f"{i}. [{status}] {t['text']} (created {t['created']}){extra}")

def done_task(i: int):
    items = load()
    if not (1 <= i <= len(items)): print("Invalid index."); return
    snapshot(items)
    items[i-1]["done"] = True
    items[i-1]["done_at"] = ts()
    save(items); print("Marked done:", items[i-1]["text"])

def delete_task(i: int):
    items = load()
    if not (1 <= i <= len(items)): print("Invalid index."); return
    snapshot(items)
    removed = items.pop(i-1)
    save(items); print("Deleted:", removed["text"])

def undo():
    if not UNDO_STACK: print("Nothing to undo."); return
    prev = UNDO_STACK.pop()
    save(prev); print("Undone last change.")

def ts() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")

def help():
    print("Usage:")
    print("  python todo.py add \"Task text\"")
    print("  python todo.py list")
    print("  python todo.py done <index>")
    print("  python todo.py delete <index>")
    print("  python todo.py undo")

def main(argv: List[str]):
    if len(argv) < 1: help(); return
    cmd = argv[0]
    if cmd == "add": add_task(" ".join(argv[1:]))
    elif cmd == "list": list_tasks()
    elif cmd == "done": done_task(int(argv[1]))
    elif cmd == "delete": delete_task(int(argv[1]))
    elif cmd == "undo": undo()
    else: help()

# Mini tests
def _test():
    if os.path.exists(DB): os.remove(DB)
    add_task("Alpha"); add_task("beta"); add_task("Beta feature")
    list_tasks(); done_task(2); list_tasks(); undo(); list_tasks()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "_test":
        _test()
    else:
        main(sys.argv[1:])
