import os
import stat
import tempfile
from pathlib import Path
from datetime import datetime
import paramiko

# ======================================================
# CONFIG
# ======================================================
LOCAL_DIR = Path(r"\\fs01\ITAPEVA ATIVAS\JURIDICO\--- TERMOS DE CESSÃO ---")
LOG_DIR   = LOCAL_DIR / "Logs"
CRED_TXT  = Path(r"\\fs01\ITAPEVA ATIVAS\DADOS\SA_Credencials.txt")

DATA_EXEC = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE  = LOG_DIR / f"sync_termos_{DATA_EXEC}.txt"

# ======================================================
# LOG
# ======================================================
def log(msg: str):
    linha = f"{datetime.now():%Y-%m-%d %H:%M:%S} - {msg}"
    print(linha)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8", errors="replace") as f:
        f.write(linha + "\n")


# ======================================================
# LER CREDENCIAIS
# ======================================================
def load_creds(path: Path) -> dict:
    ns = {}

    class _Dummy:
        class cursors:
            class Cursor:
                pass

    ns["pymysql"] = _Dummy

    exec(path.read_text(encoding="utf-8", errors="replace"), ns, ns)

    return {
        "host": ns["SFTP_HOST_ORIG"],
        "port": int(ns["SFTP_PORT_ORIG"]),
        "user": ns["SFTP_USERNAME_ORIG"],
        "pwd":  ns["SFTP_PASSWORD_ORIG"],
        "root": str(ns["REMOTE_DIR_ORIG"]).rstrip("/") or "/",
    }


# ======================================================
# SFTP
# ======================================================
def connect_sftp(cfg):
    transport = paramiko.Transport((cfg["host"], cfg["port"]))
    transport.connect(username=cfg["user"], password=cfg["pwd"])
    return paramiko.SFTPClient.from_transport(transport)


def sftp_list(sftp, root):
    files = {}
    root = root.rstrip("/")

    def walk(p):
        for e in sftp.listdir_attr(p):
            full = f"{p}/{e.filename}".replace("//", "/")
            if stat.S_ISDIR(e.st_mode):
                walk(full)
            else:
                rel = full[len(root)+1:]
                files[rel] = int(e.st_size)

    walk(root)
    return files


def local_list(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    out = {}
    for p in root.rglob("*"):
        if p.is_file():
            out[p.relative_to(root).as_posix()] = p.stat().st_size
    return out


def download_atomic(sftp, r_full, l_full: Path):
    l_full.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=str(l_full.parent), prefix="tmp_", suffix=".part") as tmp:
        tmp_path = Path(tmp.name)

    try:
        sftp.get(r_full, str(tmp_path))
        if l_full.exists():
            l_full.unlink()
        tmp_path.replace(l_full)
    finally:
        if tmp_path.exists() and tmp_path != l_full:
            try:
                tmp_path.unlink()
            except Exception:
                pass


# ======================================================
# MAIN
# ======================================================
def main():
    log("Iniciando sincronizacao SFTP -> LOCAL (nome + tamanho)")

    if not CRED_TXT.exists():
        log(f"ERRO: Credenciais nao encontradas: {CRED_TXT}")
        return

    cfg = load_creds(CRED_TXT)
    log(f"Remoto: {cfg['host']}:{cfg['port']}{cfg['root']}")
    log(f"Local : {LOCAL_DIR}")
    log(f"Arquivo de log: {LOG_FILE.name}")

    sftp = connect_sftp(cfg)

    try:
        remote = sftp_list(sftp, cfg["root"])
        local  = local_list(LOCAL_DIR)

        log(f"Arquivos remoto: {len(remote)}")
        log(f"Arquivos local : {len(local)}")

        # remover extras locais
        extras = sorted(set(local) - set(remote))
        for rel in extras:
            try:
                (LOCAL_DIR / rel).unlink()
                log(f"REMOVIDO local (nao existe no remoto): {rel}")
            except Exception as e:
                log(f"ERRO removendo {rel}: {e}")

        # baixar novos/diferentes
        iguais = 0
        baixados = 0

        for rel, rsize in remote.items():
            lsize = local.get(rel)
            if lsize is not None and int(lsize) == int(rsize):
                iguais += 1
                continue

            r_full = f"{cfg['root'].rstrip('/')}/{rel}".replace("//", "/")
            l_full = LOCAL_DIR / rel

            try:
                download_atomic(sftp, r_full, l_full)
                baixados += 1
                log(f"BAIXADO/ATUALIZADO: {rel} ({rsize} bytes)")
            except Exception as e:
                log(f"ERRO baixando {rel}: {e}")

        log(f"Iguais: {iguais}")
        log(f"Baixados/atualizados: {baixados}")
        log("Sincronizacao concluida com sucesso.")

    finally:
        sftp.close()


if __name__ == "__main__":
    main()
