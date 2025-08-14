import ast, os

NEEDS = "from DuRiCore.trace import emit_trace"

def _join_args(args):
    # " ".join(map(str, [a, b, ...]))
    return ast.Call(
        func=ast.Attribute(value=ast.Constant(" "), attr="join", ctx=ast.Load()),
        args=[ast.Call(
            func=ast.Name("map", ast.Load()),
            args=[ast.Name("str", ast.Load()), ast.List(elts=list(args), ctx=ast.Load())],
            keywords=[]
        )],
        keywords=[]
    )

class Fixer(ast.NodeTransformer):
    def __init__(self, src):
        self.src = src

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            # level 기본 info, file=sys.stderr면 error
            level = "info"
            for kw in node.keywords or []:
                if kw.arg == "file":
                    frag = ast.get_source_segment(self.src, kw.value) or ""
                    if "sys.stderr" in frag:
                        level = "error"
                    break
            return ast.copy_location(
                ast.Call(
                    func=ast.Name("emit_trace", ast.Load()),
                    args=[ast.Constant(level), _join_args(node.args or [])],
                    keywords=[]
                ),
                node
            )
        return node

def ensure_import(text):
    return text if NEEDS in text else f"{NEEDS}\n{text}"

def fix_file(path):
    src = open(path, encoding="utf-8").read()
    try:
        tree = ast.parse(src)
    except Exception:
        return False  # 파서 실패시 건너뜀
    new_tree = Fixer(src).visit(tree)
    ast.fix_missing_locations(new_tree)
    body = ast.unparse(new_tree)
    out = ensure_import(body)
    if out != src:
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        return True
    return False

if __name__ == "__main__":
    changed = 0
    for root in ("DuRiCore", "core", "duri_brain", "duri_core", "duri_common", "models"):
        if not os.path.isdir(root): continue
        for dp, _, fs in os.walk(root):
            for fn in fs:
                if fn.endswith(".py"):
                    changed += fix_file(os.path.join(dp, fn)) or 0
    print(f"modified_files={changed}")


