# model_io.py
from pathlib import Path
import joblib, os, tempfile

def atomic_joblib_dump(obj, path: Path, compress=3, protocol=4):
    path = Path(path)
    tmp_dir = path.parent
    tmp_fd, tmp_name = tempfile.mkstemp(prefix=path.name, dir=tmp_dir)
    os.close(tmp_fd)
    try:
        joblib.dump(obj, tmp_name, compress=compress, protocol=protocol)
        os.replace(tmp_name, path)   # atomic move
        return True
    finally:
        if os.path.exists(tmp_name):
            try: os.remove(tmp_name)
            except: pass

def latest_model_path(artifacts_dir: Path) -> Path | None:
    cands = sorted((Path(artifacts_dir).glob("*model*.pkl")),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None



